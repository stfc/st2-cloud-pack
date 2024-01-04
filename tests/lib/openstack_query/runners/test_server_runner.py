from unittest.mock import MagicMock, NonCallableMock, call, patch

import openstack.exceptions
import pytest

from openstack_query.runners.server_runner import ServerRunner

from openstack.exceptions import ResourceNotFound
from exceptions.parse_query_error import ParseQueryError


@pytest.fixture(name="instance")
def instance_fixture(mock_marker_prop_func):
    """
    Returns an instance to run tests with
    """
    return ServerRunner(marker_prop_func=mock_marker_prop_func)


def test_parse_meta_params_ambiguous(instance):
    """
    Tests parse_meta_params method when given both from_project and all_project arguments
    should raise an error
    """
    with pytest.raises(ParseQueryError):
        instance.parse_meta_params(
            NonCallableMock(),
            from_projects=["project_id1", "project_id2"],
            all_projects=True,
        )


def test_parse_meta_params_with_from_projects_no_admin(instance):
    """
    Tests parse_meta_params method with no as_admin given
    method should raise error because from_projects won't work without admin being set
    """
    with pytest.raises(ParseQueryError):
        instance.parse_meta_params(
            NonCallableMock(),
            from_projects=["project_id1", "project_id2"],
            as_admin=False,
        )


def test_parse_meta_params_with_no_admin(instance):
    """
    Tests parse_meta_params method with no as_admin given
    method should return meta params with projects set to a singleton list containing
    only the current scoped project id
    """
    mock_connection = MagicMock()
    res = instance.parse_meta_params(
        mock_connection,
        as_admin=False,
    )
    assert not set(res.keys()).difference({"projects"})
    assert res["projects"] == [mock_connection.current_project_id]


def test_parse_meta_params_with_all_projects_no_admin(instance):
    """
    Tests parse_meta_params with no as_admin given
    method should raise error because all_projects won't work without admin being set
    """
    with pytest.raises(ParseQueryError):
        instance.parse_meta_params(NonCallableMock(), all_projects=True, as_admin=False)


def test_parse_meta_params_with_from_projects_as_admin(instance):
    """
    Tests parse_meta_params with valid from_project argument and as_admin
    method should iteratively call find_project() to find each project in list and return outputs
    """

    mock_project_identifiers = ["project_id1", "project_id2"]
    mock_connection = MagicMock()
    mock_connection.identity.find_project.side_effect = [
        {"id": "id1"},
        {"id": "id2"},
    ]
    res = instance.parse_meta_params(
        mock_connection,
        from_projects=mock_project_identifiers,
        all_projects=False,
        as_admin=True,
    )
    mock_connection.identity.user_projects.assert_called_once_with(
        mock_connection.current_user_id
    )
    mock_connection.identity.find_project.assert_has_calls(
        [
            call("project_id1", ignore_missing=False),
            call("project_id2", ignore_missing=False),
        ]
    )
    assert not set(res.keys()).difference({"projects", "all_tenants"})
    assert not set(res["projects"]).difference({"id1", "id2"})


def test_parse_meta_params_with_all_projects_as_admin(instance):
    """
    Tests parse_meta_params with all_projects and as_admin set
    method should return meta params with only all_tenants set to true
    """
    mock_connection = MagicMock()
    res = instance.parse_meta_params(mock_connection, all_projects=True, as_admin=True)
    assert not set(res.keys()).difference({"all_tenants"})


def test_parse_meta_params_with_only_as_admin(instance):
    """
    Tests parse_meta_params with only as_admin set
    method should return meta params with all_tenants and projects set to output of user_projects
    """
    mock_connection = MagicMock()
    mock_connection.identity.user_projects.return_value = [
        "user-project1",
        "user-project2",
    ]
    mock_connection.identity.find_project.side_effect = [
        {"id": "id1"},
        {"id": "id2"},
    ]
    res = instance.parse_meta_params(mock_connection, as_admin=True)
    mock_connection.identity.find_project.assert_has_calls(
        [
            call("user-project1", ignore_missing=False),
            call("user-project2", ignore_missing=False),
        ]
    )
    mock_connection.identity.user_projects.assert_called_once_with(
        mock_connection.current_user_id
    )
    assert not set(res.keys()).difference({"projects", "all_tenants"})
    assert not set(res["projects"]).difference({"id1", "id2"})


def test_parse_meta_params_with_invalid_project_identifier(instance):
    """
    Tests parse_meta_params method with invalid from_project argument
    method should raise ParseQueryError when an invalid project identifier is given
    (or when project cannot be found)
    """
    mock_project_identifiers = ["project_id3"]
    mock_connection = MagicMock()
    mock_connection.identity.find_project.side_effect = [ResourceNotFound()]
    with pytest.raises(ParseQueryError):
        instance.parse_meta_params(
            mock_connection,
            from_projects=mock_project_identifiers,
            as_admin=True,
        )


def test_parse_meta_params_with_invalid_permissions(instance):
    """
    Tests parse_meta_params with invalid admin creds
    method should raise ParseQueryError when find_project fails with ForbiddenException
    """
    mock_project_identifiers = ["project_id3"]
    mock_connection = MagicMock()
    mock_connection.identity.find_project.side_effect = [
        openstack.exceptions.ForbiddenException()
    ]
    with pytest.raises(ParseQueryError):
        instance.parse_meta_params(
            mock_connection,
            from_projects=mock_project_identifiers,
            as_admin=True,
        )


def test_run_query_project_meta_arg_preset_duplication(instance):
    """
    Tests that an error is raised when run_query is called with filter kwargs which contains project_id and with
    meta_params that also contain projects - i.e there's a mismatch in which projects to search
    """
    with pytest.raises(ParseQueryError):
        instance.run_query(
            NonCallableMock(),
            filter_kwargs={"project_id": "proj1"},
            projects=["proj2", "proj3"],
        )


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_with_meta_arg_projects_with_server_side_queries(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests run_query method when meta arg projects given method should for each project:
        - update filter kwargs to include "project_id": <id of project>
        - run _run_paginated_query with updated filter_kwargs
    """
    mock_run_paginated_query.side_effect = [
        ["server1", "server2"],
        ["server3", "server4"],
    ]
    mock_filter_kwargs = {"arg1": "val1"}

    projects = ["project-id1", "project-id2"]
    mock_connection = MagicMock()
    res = instance.run_query(
        mock_connection,
        filter_kwargs=mock_filter_kwargs,
        projects=projects,
    )

    for project in projects:
        mock_run_paginated_query.assert_any_call(
            mock_connection.compute.servers,
            mock_marker_prop_func,
            {"project_id": project, **mock_filter_kwargs},
        )

    assert res == ["server1", "server2", "server3", "server4"]


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_meta_arg_all_tenants_no_projects(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests run_query method when meta arg all_tenants given
    """
    mock_run_paginated_query.return_value = ["server1", "server2"]
    mock_connection = MagicMock()

    res = instance.run_query(mock_connection, filter_kwargs={}, all_tenants=True)
    mock_run_paginated_query.assert_called_once_with(
        mock_connection.compute.servers,
        mock_marker_prop_func,
        {"all_tenants": True},
    )
    assert res == ["server1", "server2"]


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_with_meta_arg_projects_with_no_server_queries(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests run_query method when meta arg projects given
    method should for each project run without any filter kwargs
    """
    mock_run_paginated_query.side_effect = [
        ["server1", "server2"],
        ["server3", "server4"],
    ]
    projects = ["project-id1", "project-id2"]
    mock_connection = MagicMock()

    res = instance.run_query(mock_connection, filter_kwargs={}, projects=projects)

    for project in projects:
        mock_run_paginated_query.assert_any_call(
            mock_connection.compute.servers,
            mock_marker_prop_func,
            {"project_id": project},
        )

    assert res == ["server1", "server2", "server3", "server4"]
