from unittest.mock import patch

import pytest
from apis.openstack_query_api.server_queries import (
    find_servers_with_errored_vms,
    find_servers_with_image,
    group_servers_by_user_id,
    list_to_regex_pattern,
)


def test_list_to_regex_pattern():
    """
    Tests list_to_regex_pattern() function
    Creates regex pattern from list
    """
    mock_list = ["img1", "img2", "img3"]
    res = list_to_regex_pattern(mock_list)
    assert res == "(.*img1|.*img2|.*img3)"


@patch("apis.openstack_query_api.server_queries.ServerQuery")
def test_find_servers_with_errored_vms_valid(mock_server_query):
    """
    Tests find_servers_with_errored_vms() function with valid inputs
    """
    mock_server_query_obj = mock_server_query.return_value

    res = find_servers_with_errored_vms(
        "test-cloud-account", -1, ["project1", "project2"]
    )

    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_server_query_obj.select.assert_called_once_with("id", "name", "addresses")

    mock_server_query_obj.append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", ["name"]
    )
    assert res == mock_server_query_obj


@patch("apis.openstack_query_api.server_queries.ServerQuery")
def test_find_servers_with_errored_vms_valid_age(mock_server_query):
    """
    Tests find_servers_with_errored_vms() function when filtering by minimum server age
    """
    mock_server_query_obj = mock_server_query.return_value

    res = find_servers_with_errored_vms(
        "test-cloud-account", 10, ["project1", "project2"]
    )

    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_server_query_obj.select.assert_called_once_with("id", "name", "addresses")

    mock_server_query_obj.append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", ["name"]
    )
    assert res == mock_server_query_obj


@patch("apis.openstack_query_api.server_queries.ImageQuery")
@patch("apis.openstack_query_api.server_queries.list_to_regex_pattern")
def test_find_servers_with_image_valid(
    mock_list_to_regex,
    mock_image_query,
):
    """
    Tests find_servers_with_images() function
    Should run a complex ImageQuery query - chaining into servers and appending project name
    """
    mock_image_query_obj = mock_image_query.return_value
    mock_server_query_obj = mock_image_query_obj.then.return_value

    res = find_servers_with_image(
        "test-cloud-account", ["img1", "img2"], ["project1", "project2"]
    )
    mock_image_query.assert_called_once()
    mock_list_to_regex.assert_called_once_with(["img1", "img2"])
    mock_image_query_obj.where.assert_called_once_with(
        "matches_regex",
        "name",
        value=mock_list_to_regex.return_value,
    )

    mock_image_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_image_query_obj.sort_by.assert_called_once_with(
        ("id", "ascending"), ("name", "ascending")
    )
    mock_image_query_obj.to_props.assert_called_once()
    mock_image_query_obj.then.assert_called_once_with(
        "SERVER_QUERY", keep_previous_results=True
    )

    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_server_query_obj.select.assert_called_once_with("id", "name", "addresses")
    mock_server_query_obj.append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", ["name"]
    )
    assert res == mock_server_query_obj


@patch("apis.openstack_query_api.server_queries.ImageQuery")
@patch("apis.openstack_query_api.server_queries.list_to_regex_pattern")
def test_find_servers_with_image_invalid_images(
    mock_list_to_regex,
    mock_image_query,
):
    """
    Tests that find_servers_with_images() raises an error when supplied with an invalid image name
    """

    mock_image_query_obj = mock_image_query.return_value
    mock_image_query_obj.to_props.return_value = None

    with pytest.raises(RuntimeError):
        find_servers_with_image("test-cloud-account", ["invalid-img"])

    mock_image_query.assert_called_once()
    mock_image_query_obj.where.assert_called_once_with(
        "matches_regex",
        "name",
        value=mock_list_to_regex.return_value,
    )

    mock_image_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=None,
        all_projects=True,
    )
    mock_image_query_obj.sort_by.assert_called_once_with(
        ("id", "ascending"), ("name", "ascending")
    )
    mock_image_query_obj.to_props.assert_called_once()


@patch("apis.openstack_query_api.server_queries.QueryAPI")
def test_group_by_user_id(mock_server_query):
    """
    Tests group_servers_by_user_id() function
    """
    mock_server_query_obj = mock_server_query.return_value
    mock_grouped_query_obj = mock_server_query_obj.group_by.return_value
    res = group_servers_by_user_id(mock_server_query_obj)
    mock_server_query_obj.group_by.assert_called_once_with("user_id")
    assert res == mock_grouped_query_obj
