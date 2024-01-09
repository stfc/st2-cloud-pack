from unittest.mock import MagicMock, NonCallableMock, patch
import pytest

from openstack_query.runners.image_runner import ImageRunner
from exceptions.parse_query_error import ParseQueryError


@pytest.fixture(name="instance")
def instance_fixture(mock_marker_prop_func):
    """
    Returns an instance to run tests with
    """
    return ImageRunner(marker_prop_func=mock_marker_prop_func)


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


def test_parse_meta_params_with_all_projects_no_admin(instance):
    """
    Tests parse_meta_params with no as_admin given
    method should raise error because all_projects won't work without admin being set
    """
    with pytest.raises(ParseQueryError):
        instance.parse_meta_params(NonCallableMock(), all_projects=True, as_admin=False)


def test_parse_meta_params_with_all_projects(instance):
    """
    Tests parse_meta_params with all_projects and as_admin set
    method should return empty meta-params
    """
    mock_connection = MagicMock()
    res = instance.parse_meta_params(mock_connection, all_projects=True, as_admin=True)
    assert res == {}


@patch("openstack_query.runners.runner_utils.RunnerUtils.parse_projects")
def test_parse_meta_params_with_from_projects_as_admin(mock_parse_projects, instance):
    """
    Tests parse_meta_params with valid from_projects argument and as_admin = True
    method should call RunnerUtils.parse_projects to get project_ids and populate meta-param dictionary
    should also set all_tenants = True
    """
    mock_connection = MagicMock()
    mock_from_projects = NonCallableMock()
    res = instance.parse_meta_params(
        mock_connection, from_projects=mock_from_projects, as_admin=True
    )

    mock_parse_projects.assert_called_once_with(mock_connection, mock_from_projects)

    assert list(res.keys()) == ["projects"]
    assert res["projects"] == mock_parse_projects.return_value


@patch("openstack_query.runners.runner_utils.RunnerUtils.parse_projects")
def test_parse_meta_params_with_no_args(mock_parse_projects, instance):
    """
    Tests parse_meta_params with no args
    method should call RunnerUtils.parse_projects on current project_id and populate meta-param dictionary
    """

    mock_connection = MagicMock()
    res = instance.parse_meta_params(mock_connection)

    mock_parse_projects.assert_called_once_with(
        mock_connection, [mock_connection.current_project_id]
    )

    assert list(res.keys()) == ["projects"]
    assert res["projects"] == mock_parse_projects.return_value


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_with_meta_arg_projects_with_server_side_queries(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests run_query method when meta arg projects given method should for each project:
        - update filter kwargs to include "owner": <id of project>
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
            mock_connection.compute.images,
            mock_marker_prop_func,
            {"owner": project, **mock_filter_kwargs},
        )

    assert res == ["server1", "server2", "server3", "server4"]


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_no_meta_params(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests run_query method no meta-params given and no filter_kwargs given
    """
    mock_run_paginated_query.return_value = ["server1", "server2"]
    mock_connection = MagicMock()

    res = instance.run_query(mock_connection, filter_kwargs=None)

    mock_run_paginated_query.assert_called_once_with(
        mock_connection.compute.images,
        mock_marker_prop_func,
        {},
    )
    assert res == ["server1", "server2"]
