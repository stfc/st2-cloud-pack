from unittest.mock import MagicMock, NonCallableMock, patch
import pytest
from apis.openstack_query_api.server_queries import find_server_with_flavors, group_by


@patch("apis.openstack_query_api.server_queries.FlavorQuery")
def test_find_server_with_flavors_valid(mock_flavor_query):
    mock_flavor_query_obj = mock_flavor_query.return_value
    mock_server_query_obj = mock_flavor_query_obj.then.return_value
    # Mock to_props for flavor query to return a non-empty list
    mock_flavor_query_obj.to_props.return_value = [{"flavor_id": "id1"}]
    # Mock to_props for server query to return an empty list, to check no error is raised
    mock_server_query_obj.to_props.return_value = None
    res = find_server_with_flavors(
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
    mock_server_query_obj.to_props.assert_called_once()
    mock_server_query_obj.append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", ["project_name"]
    )
    # Check that group_by is NOT called
    assert mock_server_query_obj.group_by.call_count == 0
    assert res == mock_server_query_obj


@patch("apis.openstack_query_api.server_queries.FlavorQuery")
def test_find_server_with_flavors_no_projects(mock_flavor_query):
    mock_flavor_query_obj = mock_flavor_query.return_value
    mock_server_query_obj = mock_flavor_query_obj.then.return_value
    # Mock to_props for flavor query to return a non-empty list
    mock_flavor_query_obj.to_props.return_value = [{"flavor_id": "id1"}]
    # Mock to_props for server query to return an empty list, to check no error is raised
    mock_server_query_obj.to_props.return_value = None
    find_server_with_flavors(
        "test-cloud-account", ["flavor1", "flavor2"], from_projects=None
    )
    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=None,
        all_projects=True,
    )


@patch("apis.openstack_query_api.server_queries.FlavorQuery")
def test_find_server_with_flavors_invalid_flavor(mock_flavor_query):
    mock_flavor_query_obj = mock_flavor_query.return_value
    # Mock to_props for flavor query to return None (no flavors found)
    mock_flavor_query_obj.to_props.return_value = None
    with pytest.raises(RuntimeError) as excinfo:
        find_server_with_flavors("test-cloud-account", ["invalid-flavor"])
    assert "None of the Flavors provided invalid-flavor were found" in str(
        excinfo.value
    )
    mock_flavor_query_obj.to_props.assert_called_once()
    # Check server query is never executed
    assert mock_flavor_query_obj.then.call_count == 0


def test_group_by():
    mock_query = MagicMock()
    label = NonCallableMock()
    res = group_by(mock_query, label)
    mock_query.group_by.assert_called_once_with(label)
    assert res == mock_query.group_by.return_value
