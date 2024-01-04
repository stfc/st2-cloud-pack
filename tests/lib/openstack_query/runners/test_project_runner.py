from unittest.mock import MagicMock, NonCallableMock, patch
import pytest

from openstack_query.runners.project_runner import ProjectRunner


@pytest.fixture(name="instance")
def instance_fixture(mock_marker_prop_func):
    """
    Returns an instance to run tests with
    """
    return ProjectRunner(marker_prop_func=mock_marker_prop_func)


def test_parse_meta_params(instance):
    """
    tests that parse_query_params returns empty dict - ProjectQuery accepts no meta-params currently
    """
    assert (
        instance.parse_meta_params(
            NonCallableMock(), **{"arg1": "val1", "arg2": "val2"}
        )
        == {}
    )


@patch("openstack_query.runners.runner_utils.RunnerUtils.run_paginated_query")
def test_run_query_no_server_filters(
    mock_run_paginated_query, instance, mock_marker_prop_func
):
    """
    Tests that run_query method works expectedly with no server-side filters
    """
    mock_user_list = mock_run_paginated_query.return_value = [
        "project1",
        "project2",
        "project3",
    ]
    mock_filter_kwargs = None
    mock_connection = MagicMock()

    res = instance.run_query(
        mock_connection,
        filter_kwargs=mock_filter_kwargs,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_connection.identity.projects, mock_marker_prop_func, {}
    )
    assert res == mock_user_list


def test_run_query_with_id_in_filter(instance):
    """
    Tests that run_query method works expectedly with 'id' in server-side filters
    """

    mock_filter_kwargs = {"id": "project_id1"}
    mock_connection = MagicMock()

    res = instance.run_query(
        mock_connection,
        filter_kwargs=mock_filter_kwargs,
    )

    mock_connection.identity.find_project.assert_called_once_with(
        "project_id1", ignore_missing=True
    )

    assert res == [mock_connection.identity.find_project.return_value]
