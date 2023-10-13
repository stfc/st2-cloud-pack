from unittest.mock import patch, MagicMock

import pytest

from openstack_query.api.query_objects import (
    UserQuery,
    ServerQuery,
    FlavorQuery,
    ProjectQuery,
    get_common,
)


@patch("openstack_query.api.query_objects.QueryFactory")
@patch("openstack_query.api.query_objects.QueryAPI")
def test_get_common(mock_query_api, mock_query_factory):
    """
    tests that function _get_common works
    should use QueryFactory to setup a query object with given mapping class
    """
    mock_query_mapping = MagicMock()
    res = get_common(mock_query_mapping)
    mock_query_factory.build_query_deps.assert_called_once_with(mock_query_mapping)
    mock_query_api.assert_called_once_with(
        mock_query_factory.build_query_deps.return_value
    )
    assert res == mock_query_api.return_value


@pytest.fixture(name="run_query_test_case")
def run_query_test_case_fixture():
    """
    Fixture to test each query function
    """

    def _run_query_test_case(mock_query_func, expected_mapping):
        """
        tests each given query_function calls get_common with expected mapping class
        """

        with patch("openstack_query.api.query_objects.get_common") as mock_get_common:
            res = mock_query_func()
            mock_get_common.assert_called_once_with(expected_mapping)
        assert res == mock_get_common.return_value

    return _run_query_test_case


def test_server_query(run_query_test_case):
    """
    tests that function ServerQuery works
    should call get_common with ServerMapping
    """
    with patch(
        "openstack_query.api.query_objects.ServerMapping"
    ) as mock_server_mapping:
        run_query_test_case(ServerQuery, mock_server_mapping)


def test_user_query(run_query_test_case):
    """
    tests that function UserQuery works
    should call get_common with UserMapping
    """
    with patch("openstack_query.api.query_objects.UserMapping") as mock_user_mapping:
        run_query_test_case(UserQuery, mock_user_mapping)


def test_flavor_query(run_query_test_case):
    """
    tests that function FlavorQuery works
    should call get_common with FlavorMapping
    """
    with patch(
        "openstack_query.api.query_objects.FlavorMapping"
    ) as mock_flavor_mapping:
        run_query_test_case(FlavorQuery, mock_flavor_mapping)


def test_project_query(run_query_test_case):
    """
    tests that function ProjectQuery works
    should call get_common with ProjectMapping
    """
    with patch(
        "openstack_query.api.query_objects.ProjectMapping"
    ) as mock_project_mapping:
        run_query_test_case(ProjectQuery, mock_project_mapping)
