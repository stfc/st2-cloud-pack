from unittest.mock import Mock, patch

from apis.wazuh_api.wazuh_query_agents import _query_agents, wazuh_list_servers_by_os


# pylint: disable=protected-access
# pylint: disable=unused-argument
@patch("apis.wazuh_api.wazuh_query_agents.requests.get")
def test_query_agents_pagination(mock_get):
    """
    WHAT IT TESTS:
        Verifies `_query_agents` loops through paginated API results until an empty page is returned.

    HOW IT WORKS:
        Mocks `requests.get` using `side_effect` with 2 responses:
        Page 1 with items and Page 2 empty.

    WHY IT PREVENTS BUGS:
        Guarantees offset increments (0 -> 500), pagination headers/tokens are attached,
        and the loop terminates correctly on empty responses without causing infinite loops.
    """
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

    second_response = Mock()
    second_response.raise_for_status.return_value = None
    second_response.json.return_value = {"data": {"affected_items": []}}

    responses = [first_response, second_response]
    request_params = []

    def mock_request(*args, **kwargs):
        # Store a copy because `_query_agents` mutates the same params dictionary.
        request_params.append(kwargs["params"].copy())
        return responses.pop(0)

    mock_get.side_effect = mock_request

    agents = _query_agents(
        "jwt-token",
        "https://wazuh.example.com",
        values=["name"],
        query="status=active",
    )

    # Verify aggregated data
    assert agents == [{"id": "001"}, {"id": "002"}]

    # Verify exactly 2 HTTP requests were sent
    assert mock_get.call_count == 2

    # Verify the first request
    assert request_params[0] == {
        "limit": 500,
        "offset": 0,
        "select": ["name"],
        "q": "status=active",
    }

    # Verify the second request used the updated offset
    assert request_params[1] == {
        "limit": 500,
        "offset": 500,
        "select": ["name"],
        "q": "status=active",
    }


@patch("apis.wazuh_api.wazuh_query_agents._query_agents")
def test_wazuh_list_servers_by_os(mock_query):
    """
    WHAT IT TESTS:
        Verifies `wazuh_list_servers_by_os()` formats the Wazuh query string correctly
        and extracts UUIDs from OpenStack server names.

    HOW IT WORKS:
        Mocks `_query_agents` to return sample server names, including malformed names.

    WHY IT PREVENTS BUGS:
        Verifies the exact query parameters and ensures valid UUIDs are extracted.
    """
    wazuh_account = Mock()
    wazuh_account.url = "https://wazuh.example.com"
    wazuh_account.get_wazuh_token.return_value = "jwt-token"

    mock_query.return_value = [
        {
            "name": (
                "host-192-168-231-139.openstacklocal-"
                "001682d2-79a2-41b9-af7f-c553f7d67b0d"
            )
        },
        {
            "name": (
                "host-192-168-231-140.openstacklocal-"
                "aabbccdd-1234-5678-90ab-cdef12345678"
            )
        },
        {"name": "malformed-server-name-without-uuid"},
    ]

    server_ids = wazuh_list_servers_by_os(
        wazuh_account=wazuh_account,
        os_name="ubuntu",
        os_version="22.04",
    )

    expected_ids = [
        "001682d2-79a2-41b9-af7f-c553f7d67b0d",
        "aabbccdd-1234-5678-90ab-cdef12345678",
    ]
    assert server_ids == expected_ids

    wazuh_account.get_wazuh_token.assert_called_once_with()

    expected_query = "os.platform=ubuntu;os.major=22.04;status=active;group!=kolla"
    mock_query.assert_called_once_with(
        "jwt-token",
        "https://wazuh.example.com",
        values=["name"],
        query=expected_query,
    )
