import unittest
from unittest.mock import Mock, patch

from apis.wazuh_api.wazuh import WazuhClient


# pylint: disable=protected-access
class TestWazuhClient(unittest.TestCase):
    """
    Unit test suite for WazuhClient.

    Tests client authentication, internal query pagination, and public-facing wrapper methods.
    Network calls are mocked using `unittest.mock.patch` to isolate local logic execution.
    """

    def setUp(self):
        """Set up dummy configuration and initialize a clean WazuhClient instance prior to each test."""
        self.config = {
            "wazuh_username": "user",
            "wazuh_password": "pass",
            "wazuh_url": "https://wazuh.example.com",
        }
        self.client = WazuhClient(self.config)

    @patch("apis.wazuh_api.wazuh.requests.get")
    def test_get_wazuh_token(self, mock_get):
        """
        WHAT IT TESTS:
            Verifies that `_get_wazuh_token` successfully fetches and extracts the JWT token string.

        HOW IT WORKS:
            Mocks `requests.get` to return a 200 OK JSON payload containing a fake token.

        WHY IT PREVENTS BUGS:
            Ensures that changes to the token authentication URL, Basic Auth credentials, timeout,
            or JSON parsing logic do not break authentication.
        """
        response = Mock()
        response.json.return_value = {"data": {"token": "jwt-token"}}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        token = self.client._get_wazuh_token()

        # Check token extraction
        self.assertEqual(token, "jwt-token")

        # Check HTTP request parameters
        mock_get.assert_called_once_with(
            "https://wazuh.example.com/security/user/authenticate",
            auth=("user", "pass"),
            verify=False,
            timeout=60,
        )

    @patch("apis.wazuh_api.wazuh.requests.get")
    @patch.object(WazuhClient, "_get_wazuh_token", return_value="jwt-token")
    def test_query_agents_pagination(self, mock_token, mock_get):
        """
        WHAT IT TESTS:
            Verifies `_query_agents` loops through paginated API results until an empty page is returned.

        HOW IT WORKS:
            1. Mocks `_get_wazuh_token` to return "jwt-token" without calling the real auth method.
            2. Mocks `requests.get` using `side_effect` with 2 responses: Page 1 with items, Page 2 empty.

        WHY IT PREVENTS BUGS:
            Guarantees offset increments (0 -> 500), pagination headers/tokens are attached,
            and the loop terminates correctly on empty responses without causing infinite loops.
        """
        # First API call returns 2 agents
        first_response = Mock()
        first_response.raise_for_status.return_value = None
        first_response.json.return_value = {
            "data": {
                "affected_items": [
                    {"id": "001"},
                    {"id": "002"},
                ]
            }
        }

        # Second API call returns empty list to stop loop
        second_response = Mock()
        second_response.raise_for_status.return_value = None
        second_response.json.return_value = {"data": {"affected_items": []}}

        mock_get.side_effect = [first_response, second_response]

        agents = self.client._query_agents(values=["name"], query="status=active")

        # Verify aggregated data
        self.assertEqual(agents, [{"id": "001"}, {"id": "002"}])

        # Verify authentication occurred once
        mock_token.assert_called_once()

        # Verify exactly 2 HTTP requests were sent (Page 1 and Page 2)
        self.assertEqual(mock_get.call_count, 2)

        # Verify request headers & query params for offset=0
        mock_get.assert_any_call(
            "https://wazuh.example.com/agents",
            headers={
                "Authorization": "Bearer jwt-token",
                "Content-Type": "application/json",
            },
            params={
                "limit": 500,
                "offset": 0,
                "select": ["name"],
                "q": "status=active",
            },
            verify=False,
            timeout=60,
        )

        # Verify offset updated to 500 on second request
        mock_get.assert_any_call(
            "https://wazuh.example.com/agents",
            headers={
                "Authorization": "Bearer jwt-token",
                "Content-Type": "application/json",
            },
            params={
                "limit": 500,
                "offset": 500,
                "select": ["name"],
                "q": "status=active",
            },
            verify=False,
            timeout=60,
        )

    @patch.object(WazuhClient, "_query_agents")
    def test_get_all(self, mock_query):
        """
        WHAT IT TESTS:
            Verifies `get_all()` acts as a direct pass-through wrapper around `_query_agents()`.

        HOW IT WORKS:
            Mocks `_query_agents` and asserts it is called without arguments.

        WHY IT PREVENTS BUGS:
            Ensures public interface contracts remain stable when calling unconstrained agent queries.
        """
        mock_query.return_value = [{"id": "001"}]

        result = self.client.get_all()

        self.assertEqual(result, [{"id": "001"}])
        mock_query.assert_called_once_with()

    @patch.object(WazuhClient, "_query_agents")
    def test_get_servers_for_os(self, mock_query):
        """
        WHAT IT TESTS:
            Verifies `get_servers_for_os()` formats the Wazuh query string correctly AND parses/extracts
            UUIDs from OpenStack server names using regular expressions.

        HOW IT WORKS:
            Mocks `_query_agents` to return sample server names (some valid OpenStack names, some malformed).

        WHY IT PREVENTS BUGS:
            1. Verifies exact query parameters (`group!=kolla;group!=quattor`) are preserved to exclude hypervisors.
            2. Ensures regex correctly extracts UUID suffixes and silently filters out non-matching names.
        """
        # Mock raw Wazuh API return data with valid and invalid OpenStack server names
        mock_query.return_value = [
            {
                "name": "host-192-168-231-139.openstacklocal-001682d2-79a2-41b9-af7f-c553f7d67b0d"
            },
            {
                "name": "host-192-168-231-140.openstacklocal-aabbccdd-1234-5678-90ab-cdef12345678"
            },
            {"name": "malformed-server-name-without-uuid"},
        ]

        server_ids = self.client.get_servers_for_os(
            os_name="ubuntu", os_version="22.04"
        )

        # Verify extracted UUIDs match
        expected_ids = [
            "001682d2-79a2-41b9-af7f-c553f7d67b0d",
            "aabbccdd-1234-5678-90ab-cdef12345678",
        ]
        self.assertEqual(server_ids, expected_ids)

        # Verify underlying _query_agents was called with the exact required query string
        expected_query = "os.platform=ubuntu;os.major=22.04;status=active;group!=kolla;group!=quattor"
        mock_query.assert_called_once_with(values=["name"], query=expected_query)
