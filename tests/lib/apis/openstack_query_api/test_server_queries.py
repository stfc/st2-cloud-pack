from unittest.mock import patch

import pytest
from apis.openstack_query_api.server_queries import find_servers_with_flavors


@patch("apis.openstack_query_api.server_queries.FlavorQuery")
def test_find_servers_with_flavor_valid(mock_flavor_query):
    """
    Tests find_servers_with_flavors() function
    should run a complex FlavorQuery query - chaining into servers, then users and return final query
    """
    mock_flavor_query_obj = mock_flavor_query.return_value
    mock_server_query_obj = mock_flavor_query_obj.then.return_value

    res = find_servers_with_flavors(
        "test-cloud-account", ["flavor1", "flavor2"], ["project1", "project2"]
    )

    mock_flavor_query.assert_called_once()
    mock_flavor_query_obj.where.assert_any_call(
        "any_in",
        "flavor_name",
        values=["flavor1", "flavor2"],
    )
    mock_flavor_query_obj.run.assert_called_once_with("test-cloud-account")
    mock_flavor_query_obj.sort_by.assert_called_once_with(("flavor_id", "asc"))
    mock_flavor_query_obj.to_props.assert_called_once()

    mock_flavor_query_obj.then.assert_called_once_with(
        "SERVER_QUERY", keep_previous_results=True
    )
    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_server_query_obj.select.assert_called_once_with(
        "server_id",
        "server_name",
        "addresses",
    )

    mock_server_query_obj.append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", ["project_name"]
    )

    mock_server_query_obj.group_by.assert_called_once_with("user_id")
    assert res == mock_server_query_obj


@patch("apis.openstack_query_api.server_queries.FlavorQuery")
def test_find_servers_with_flavor_invalid_flavor(mock_flavor_query):
    """
    Tests that find_servers_with_flavors fails when provided invalid flavor name
    """
    mock_flavor_query_obj = mock_flavor_query.return_value
    mock_flavor_query_obj.to_props.return_value = None

    with pytest.raises(RuntimeError):
        find_servers_with_flavors("test-cloud-account", ["invalid-flavor"])

    mock_flavor_query.assert_called_once()
    mock_flavor_query_obj.where.assert_any_call(
        "any_in",
        "flavor_name",
        values=["invalid-flavor"],
    )
    mock_flavor_query_obj.run.assert_called_once_with("test-cloud-account")
    mock_flavor_query_obj.sort_by.assert_called_once_with(("flavor_id", "asc"))
    mock_flavor_query_obj.to_props.assert_called_once()
