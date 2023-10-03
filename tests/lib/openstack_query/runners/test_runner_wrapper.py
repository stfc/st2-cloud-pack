from unittest.mock import MagicMock, patch
import pytest
from openstack_query.runners.runner_wrapper import RunnerWrapper

# pylint:disable=protected-access


@pytest.fixture(name="mock_page_func")
def mock_page_func_fixture():
    """
    Returns a stub function for mock_page_func
    """

    def _mock_page_func(mock_obj):
        """simple mock func which returns "id" key from given dict"""
        return mock_obj["id"]

    return _mock_page_func


@pytest.fixture(name="instance")
def instance_fixture(mock_connection, mock_page_func):
    """
    Returns an instance to run tests with
    """

    with patch.multiple(RunnerWrapper, __abstractmethods__=set()):
        return RunnerWrapper(
            marker_prop_func=mock_page_func, connection_cls=mock_connection
        )


@pytest.fixture(name="run_paginated_query_test")
def run_paginated_query_test_fixture(instance):
    """
    Fixture which runs a paginated query test case
    """

    def _run_paginated_query_test(number_iterations):
        """
        tests that run_paginated_query works expectedly - with one round or more of pagination
        mocked paginated call simulates the effect of retrieving a list of values up to a limit and then calling the
        same call again with a "marker" set to the last seen item to continue reading
        """
        pagination_order = []
        expected_out = []

        for i in range(0, number_iterations - 1):
            # Generate markers, it's a list of results with an ID
            marker = {"id": f"marker{i}"}
            expected_out.append(marker)
            pagination_order.append([marker])

        pagination_order.append([])

        mock_paginated_call = MagicMock()
        mock_paginated_call.side_effect = pagination_order
        instance._page_marker_prop_func = MagicMock(
            wraps=lambda resource: resource["id"]
        )

        # set round to 1, so new calls begins after returning one value
        instance._LIMIT_FOR_PAGINATION = 1
        instance._PAGINATION_CALL_LIMIT = 10

        mock_server_side_filters = {"arg1": "val1", "arg2": "val2"}
        res = instance._run_paginated_query(
            mock_paginated_call, mock_server_side_filters
        )
        assert res == expected_out

    return _run_paginated_query_test


# pylint:disable=too-many-arguments


@pytest.fixture(name="runner_run_test_case")
def runner_run_test_case_fixture(instance, mock_connection):
    """
    Fixture to run run() test cases with different args
    """

    def _runner_run_test_case(
        mock_client_side_filters,
        mock_server_side_filters,
        mock_from_subset,
        **mock_kwargs,
    ):
        """
        method to run run() test case with provided input values
        The individual methods that are called in run must be patched out by the test function
        prior to this and any asserts need to be done by the test function
        """

        # TODO this fixture needs editing
        _ = instance.run(
            cloud_account="test-account",
            client_side_filters=mock_client_side_filters,
            server_side_filters=mock_server_side_filters,
            from_subset=mock_from_subset,
            **mock_kwargs,
        )
        mock_connection.assert_called_once_with("test-account")


# TODO add run() tests and run_with_openstacksdk tests


def test_apply_client_side_filters_one_filter(instance):
    """
    Tests that apply_filter_func method functions expectedly
    with one filter function
    method should iteratively run single filter function on each
    item and return only those that filter_function returned True
    """
    mock_filters = MagicMock()
    mock_filters.side_effect = [False, True]

    mock_items = ["openstack-resource-1", "openstack-resource-2"]
    res = instance._apply_client_side_filters(mock_items, [mock_filters])
    assert ["openstack-resource-2"] == res


def test_apply_client_side_filters_multi_filter(instance):
    """
    Tests that apply_filter_func method functions expectedly
    - with  many filter functions
    method should iteratively run each filter function on each item and
    return only those that filter_function returned True
    """
    mock_filter1 = MagicMock()
    mock_filter1.side_effect = [False, False, True, True]

    mock_filter2 = MagicMock()
    mock_filter2.side_effect = [False, True, False, True]

    mock_items = [
        "openstack-resource-1",
        "openstack-resource-2",
        "openstack-resource-3",
        "openstack-resource-4",
    ]
    res = instance._apply_client_side_filters(mock_items, [mock_filter1, mock_filter2])
    assert ["openstack-resource-4"] == res


def test_run_pagination_query_gt_0(run_paginated_query_test):
    """
    Calls the testing case with various numbers of iterations
    to ensure pagination is working
    """
    for i in range(1, 3):
        run_paginated_query_test(i)
