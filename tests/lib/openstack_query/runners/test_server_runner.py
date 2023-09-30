from unittest.mock import MagicMock, call, patch
import pytest

from openstack_query.runners.server_runner import ServerRunner
from openstack.compute.v2.server import Server

from openstack.exceptions import ResourceNotFound
from exceptions.parse_query_error import ParseQueryError

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture(mock_connection):
    """
    Returns an instance to run tests with
    """
    mock_marker_prop_func = MagicMock()
    return ServerRunner(
        marker_prop_func=mock_marker_prop_func, connection_cls=mock_connection
    )


def test_parse_meta_params_with_from_projects(instance, mock_openstack_connection):
    """
    Tests _parse_meta_params method works expectedly - with valid from_project argument
    method should iteratively call find_project() to find each project in list and return outputs
    """

    mock_project_identifiers = ["project_id1", "project_id2"]
    mock_openstack_connection.identity.find_project.side_effect = [
        {"id": "id1"},
        {"id": "id2"},
    ]

    res = instance._parse_meta_params(
        mock_openstack_connection, mock_project_identifiers
    )
    mock_openstack_connection.identity.find_project.assert_has_calls(
        [
            call("project_id1", ignore_missing=False),
            call("project_id2", ignore_missing=False),
        ]
    )
    assert not set(res.keys()).difference({"projects"})
    assert not set(res["projects"]).difference({"id1", "id2"})


def test_parse_meta_params_with_invalid_project_identifier(
    instance, mock_openstack_connection
):
    """
    Tests _parse_meta_parms method works expectedly - with invalid from_project argument
    method should raise ParseQueryError when an invalid project identifier is given
    (or when project cannot be found)
    """
    mock_project_identifiers = ["project_id3"]
    mock_openstack_connection.identity.find_project.side_effect = [ResourceNotFound()]
    with pytest.raises(ParseQueryError):
        instance._parse_meta_params(mock_openstack_connection, mock_project_identifiers)


def test_run_query_project_meta_arg_preset_duplication(
    instance, mock_openstack_connection
):
    """
    Tests that an error is raised when run_query is called with filter kwargs which contains project_id and with
    meta_params that also contain projects - i.e there's a mismatch in which projects to search
    """
    with pytest.raises(ParseQueryError):
        instance._run_query(
            mock_openstack_connection,
            filter_kwargs={"project_id": "proj1"},
            projects=["proj2", "proj3"],
        )


@patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
def test_run_query_with_meta_arg_projects_with_server_side_queries(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests _run_query method works expectedly - when meta arg projects given
    method should for each project:
        - update filter kwargs to include "project_id": <id of project>
        - run _run_paginated_query with updated filter_kwargs
    """
    mock_run_paginated_query.side_effect = [
        ["server1", "server2"],
        ["server3", "server4"],
    ]
    mock_filter_kwargs = {"arg1": "val1"}

    projects = ["project-id1", "project-id2"]

    res = instance._run_query(
        mock_openstack_connection,
        filter_kwargs=mock_filter_kwargs,
        projects=projects,
    )

    for project in projects:
        mock_run_paginated_query.assert_any_call(
            mock_openstack_connection.compute.servers,
            {"all_tenants": True, "project_id": project, **mock_filter_kwargs},
        )

    assert res == ["server1", "server2", "server3", "server4"]


@patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
def test_run_query_with_meta_arg_projects_with_no_server_queries(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests _run_query method works expectedly - when meta arg projects given
    method should for each project run without any filter kwargs
    """
    mock_run_paginated_query.side_effect = [
        ["server1", "server2"],
        ["server3", "server4"],
    ]
    projects = ["project-id1", "project-id2"]
    res = instance._run_query(
        mock_openstack_connection, filter_kwargs={}, projects=projects
    )

    for project in projects:
        mock_run_paginated_query.assert_any_call(
            mock_openstack_connection.compute.servers,
            {"all_tenants": True, "project_id": project},
        )

    assert res == ["server1", "server2", "server3", "server4"]


@patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
def test_run_query_with_no_meta_args_no_kwargs(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests _run_query method works expectedly - no meta arg projects, no filter kwargs
    method should call run_paginated_query with all_tenants=True and no other filters
    """

    mock_run_paginated_query.side_effect = [["server1", "server2"]]
    mock_filter_kwargs = {}

    res = instance._run_query(
        mock_openstack_connection, filter_kwargs=mock_filter_kwargs
    )

    mock_run_paginated_query.asset_called_once_with(
        mock_openstack_connection.compute.servers, {"all_tenants": True}
    )
    assert res == ["server1", "server2"]


@patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
def test_run_query_with_no_meta_args_with_kwargs(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests _run_query method works expectedly - no meta arg projects, and with filter kwargs
    method should call run_paginated_query with all_tenants=True and pass through other filters
    """

    mock_run_paginated_query.side_effect = [["server1", "server2"]]
    mock_filter_kwargs = {"arg1": "val1"}

    res = instance._run_query(
        mock_openstack_connection, filter_kwargs=mock_filter_kwargs
    )

    mock_run_paginated_query.asset_called_once_with(
        mock_openstack_connection.compute.servers, {"all_tenants": True, "arg1": "val1"}
    )
    assert res == ["server1", "server2"]


def test_parse_subset(instance, mock_openstack_connection):
    """
    Tests _parse_subset works expectedly
    method simply checks each value in 'subset' param is of the Server type and returns it
    """

    # with one item
    mock_server_1 = MagicMock()
    mock_server_1.__class__ = Server
    res = instance._parse_subset(mock_openstack_connection, [mock_server_1])
    assert res == [mock_server_1]

    # with two items
    mock_server_2 = MagicMock()
    mock_server_2.__class__ = Server
    res = instance._parse_subset(
        mock_openstack_connection, [mock_server_1, mock_server_2]
    )
    assert res == [mock_server_1, mock_server_2]


def test_parse_subset_invalid(instance, mock_openstack_connection):
    """
    Tests _parse_subset works expectedly
    method raises error when provided value which is not of Server type
    """
    invalid_server = "invalid-server-obj"
    with pytest.raises(ParseQueryError):
        instance._parse_subset(mock_openstack_connection, [invalid_server])
