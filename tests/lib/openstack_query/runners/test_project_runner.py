from unittest.mock import MagicMock, patch
import pytest

from openstack_query.runners.project_runner import ProjectRunner
from openstack.identity.v3.project import Project
from exceptions.parse_query_error import ParseQueryError

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture(mock_connection):
    """
    Returns an instance to run tests with
    """
    mock_marker_prop_func = MagicMock()
    return ProjectRunner(
        marker_prop_func=mock_marker_prop_func, connection_cls=mock_connection
    )


def test_parse_query_params_raise_error(instance, mock_openstack_connection):
    """
    tests that parse_query_params raises error - ProjectQuery accepts no meta-params currently
    """

    with pytest.raises(ParseQueryError):
        instance._parse_meta_params(
            mock_openstack_connection, **{"arg1": "val1", "arg2": "val2"}
        )


@patch("openstack_query.runners.project_runner.ProjectRunner._run_paginated_query")
def test_run_query_no_server_filters(
    mock_run_paginated_query, instance, mock_openstack_connection
):
    """
    Tests that _run_query method works expectedly with no server-side filters
    """
    mock_user_list = mock_run_paginated_query.return_value = [
        "project1",
        "project2",
        "project3",
    ]
    mock_filter_kwargs = None
    res = instance._run_query(
        mock_openstack_connection,
        filter_kwargs=mock_filter_kwargs,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_openstack_connection.identity.projects, {}
    )
    assert res == mock_user_list


def test_run_query_with_id_in_filter(instance, mock_openstack_connection):
    """
    Tests that _run_query method works expectedly with 'id' in server-side filters
    """

    mock_filter_kwargs = {"id": "project_id1"}
    res = instance._run_query(
        mock_openstack_connection,
        filter_kwargs=mock_filter_kwargs,
    )

    mock_openstack_connection.identity.find_project.assert_called_once_with(
        "project_id1", ignore_missing=True
    )

    assert res == [mock_openstack_connection.identity.find_project.return_value]


def test_parse_subset(instance):
    """
    Tests _parse_subset works expectedly
    method simply checks each value in 'subset' param is of the Flavor type and returns it
    """

    # with one item
    mock_project_1 = MagicMock()
    mock_project_1.__class__ = Project
    res = instance._parse_subset([mock_project_1])
    assert res == [mock_project_1]

    # with two items
    mock_project_2 = MagicMock()
    mock_project_2.__class__ = Project
    res = instance._parse_subset([mock_project_1, mock_project_2])
    assert res == [mock_project_1, mock_project_2]


def test_parse_subset_invalid(instance):
    """
    Tests _parse_subset works expectedly
    method raises error when provided value which is not of Flavor type
    """
    invalid_project = "invalid-project-obj"
    with pytest.raises(ParseQueryError):
        instance._parse_subset([invalid_project])
