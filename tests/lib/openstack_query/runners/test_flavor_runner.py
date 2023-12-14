from unittest.mock import MagicMock, NonCallableMock, patch
import pytest

from openstack_query.runners.flavor_runner import FlavorRunner


@pytest.fixture(name="instance")
def instance_fixture(mock_marker_prop_func):
    """
    Returns an instance to run tests with
    """
    return FlavorRunner(marker_prop_func=mock_marker_prop_func)


def test_parse_query_params(instance):
    """
    tests that parse_query_params returns empty dict - FlavorQuery accepts no meta-params currently
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
        "flavor1",
        "flavor2",
        "flavor3",
    ]
    mock_filter_kwargs = None
    mock_connection = MagicMock()

    res = instance.run_query(
        mock_connection,
        filter_kwargs=mock_filter_kwargs,
    )

    mock_run_paginated_query.assert_called_once_with(
        mock_connection.compute.flavors,
        mock_marker_prop_func,
        {"details": True},
    )
    assert res == mock_user_list
