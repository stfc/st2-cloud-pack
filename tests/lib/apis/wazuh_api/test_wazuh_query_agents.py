from unittest.mock import Mock, patch

import pytest

from apis.wazuh_api.wazuh_query_agents import (
    _query_agents,
    _wazuh_get_labels_for_agent,
    wazuh_get_server_id_from_label,
    wazuh_list_servers_by_os,
)


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


@patch("apis.wazuh_api.wazuh_query_agents.requests.get")
def test_wazuh_get_labels_for_agent(mock_get):
    """
    WHAT IT TESTS:
        Verifies `_wazuh_get_labels_for_agent()` queries the correct Wazuh endpoint
        and returns the labels associated with the requested agent.

    HOW IT WORKS:
        Mocks `requests.get` to return a Wazuh response containing multiple labels.

    WHY IT PREVENTS BUGS:
        Ensures the correct agent-specific labels endpoint is queried and the labels
        are extracted from the expected location in the API response.
    """
    response = Mock()
    response.json.return_value = {
        "data": {
            "labels": [
                {
                    "key": "openstack.uuid",
                    "value": "001682d2-79a2-41b9-af7f-c553f7d67b0d",
                },
                {"key": "environment", "value": "production"},
            ]
        }
    }
    mock_get.return_value = response

    labels = _wazuh_get_labels_for_agent(
        "jwt-token",
        "https://wazuh.example.com",
        "001",
    )

    # Verify labels are returned unchanged
    assert labels == [
        {"key": "openstack.uuid", "value": "001682d2-79a2-41b9-af7f-c553f7d67b0d"},
        {"key": "environment", "value": "production"},
    ]

    # Verify the correct Wazuh endpoint was queried
    mock_get.assert_called_once_with(
        "https://wazuh.example.com/agents/001/config/agent/labels",
        headers={
            "Authorization": "Bearer jwt-token",
            "Content-Type": "application/json",
        },
        verify=False,
        timeout=60,
    )


@patch("apis.wazuh_api.wazuh_query_agents._wazuh_get_labels_for_agent")
def test_wazuh_get_server_id_from_label(mock_get_labels):
    """
    WHAT IT TESTS:
        Verifies `wazuh_get_server_id_from_label()` extracts the OpenStack
        Server ID from the agent label named `openstack.uuid`.

    HOW IT WORKS:
        Mocks `_wazuh_get_labels_for_agent` to return multiple labels,
        including the OpenStack UUID label.

    WHY IT PREVENTS BUGS:
        Ensures the correct label is selected and its value is returned
        as the OpenStack Server ID.
    """
    mock_get_labels.return_value = [
        {"key": "environment", "value": "production"},
        {
            "key": "openstack.uuid",
            "value": "001682d2-79a2-41b9-af7f-c553f7d67b0d",
        },
    ]

    server_id = wazuh_get_server_id_from_label(
        "jwt-token",
        "https://wazuh.example.com",
        "001",
    )

    assert server_id == "001682d2-79a2-41b9-af7f-c553f7d67b0d"

    mock_get_labels.assert_called_once_with(
        "jwt-token",
        "https://wazuh.example.com",
        "001",
    )


@patch("apis.wazuh_api.wazuh_query_agents._wazuh_get_labels_for_agent")
def test_wazuh_get_server_id_from_label_missing(mock_get_labels):
    """
    WHAT IT TESTS:
        Verifies `wazuh_get_server_id_from_label()` raises `ValueError`
        when the agent does not contain an `openstack.uuid` label.

    HOW IT WORKS:
        Mocks `_wazuh_get_labels_for_agent` to return labels without
        the required OpenStack UUID label.

    WHY IT PREVENTS BUGS:
        Ensures agents without an OpenStack Server ID are explicitly detected
        rather than returning an incorrect or undefined value.
    """
    mock_get_labels.return_value = [
        {"key": "environment", "value": "production"},
        {"key": "role", "value": "server"},
    ]

    with pytest.raises(
        ValueError,
        match="No Server ID found for Agent ID 001",
    ):
        wazuh_get_server_id_from_label(
            "jwt-token",
            "https://wazuh.example.com",
            "001",
        )

    mock_get_labels.assert_called_once_with(
        "jwt-token",
        "https://wazuh.example.com",
        "001",
    )


@patch("apis.wazuh_api.wazuh_query_agents.wazuh_get_server_id_from_label")
@patch("apis.wazuh_api.wazuh_query_agents._query_agents")
def test_wazuh_list_servers_by_os(mock_query, mock_get_server_id):
    """
    WHAT IT TESTS:
        Verifies `wazuh_list_servers_by_os()` formats the Wazuh query string correctly
        and retrieves OpenStack Server IDs from the returned Wazuh agents.

    HOW IT WORKS:
        Mocks `_query_agents` to return sample Wazuh Agent IDs and mocks
        `wazuh_get_server_id_from_label` to return the corresponding Server IDs.
        One agent is configured without a Server ID.

    WHY IT PREVENTS BUGS:
        Verifies the exact query parameters, ensures Server IDs are retrieved from
        agent labels, and confirms agents without a Server ID are skipped.
    """
    wazuh_account = Mock()
    wazuh_account.wazuh_endpoint = "https://wazuh.example.com"
    wazuh_account.get_wazuh_token.return_value = "jwt-token"

    mock_query.return_value = [
        {"id": "001"},
        {"id": "002"},
        {"id": "003"},
    ]

    mock_get_server_id.side_effect = [
        "001682d2-79a2-41b9-af7f-c553f7d67b0d",
        "aabbccdd-1234-5678-90ab-cdef12345678",
        ValueError("No Server ID found for Agent ID 003"),
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

    assert mock_get_server_id.call_count == 3

    mock_get_server_id.assert_any_call(
        "jwt-token",
        "https://wazuh.example.com",
        "001",
    )
    mock_get_server_id.assert_any_call(
        "jwt-token",
        "https://wazuh.example.com",
        "002",
    )
    mock_get_server_id.assert_any_call(
        "jwt-token",
        "https://wazuh.example.com",
        "003",
    )
