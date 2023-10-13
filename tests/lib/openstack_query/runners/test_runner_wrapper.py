from unittest.mock import MagicMock, patch, call
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
def runner_run_test_case_fixture(instance, mock_connection, mock_openstack_connection):
    """
    Fixture to run run() test cases with different args
    """

    def _runner_run_test_case(
        mock_client_side_filters=None,
        mock_server_side_filters=None,
        mock_from_subset=None,
        **mock_kwargs,
    ):
        """
        method to run run() test case with provided input values
        The individual methods that are called in run must be patched out by the test function
        prior to this and any asserts need to be done by the test function
        """

        with patch(
            "openstack_query.runners.runner_wrapper.RunnerWrapper._parse_subset"
        ) as mock_parse_subset:
            with patch(
                "openstack_query.runners.runner_wrapper.RunnerWrapper._run_with_openstacksdk"
            ) as mock_run_with_openstacksdk:
                with patch(
                    "openstack_query.runners.runner_wrapper.RunnerWrapper._apply_client_side_filters"
                ) as mock_apply_client_side_filters:
                    res = instance.run(
                        cloud_account="test-account",
                        client_side_filters=mock_client_side_filters,
                        server_side_filters=mock_server_side_filters,
                        from_subset=mock_from_subset,
                        **mock_kwargs,
                    )

        if mock_from_subset:
            mock_parse_subset.assert_called_once_with(subset=mock_from_subset)
            mock_run_with_openstacksdk.assert_not_called()

        else:
            mock_connection.assert_called_once_with("test-account")
            mock_run_with_openstacksdk.assert_called_once_with(
                conn=mock_openstack_connection,
                server_filters=mock_server_side_filters,
                **mock_kwargs,
            )
            mock_parse_subset.assert_not_called()

        query_out = mock_run_with_openstacksdk.return_value
        if mock_from_subset:
            query_out = mock_parse_subset.return_value

        if mock_client_side_filters:
            mock_apply_client_side_filters.assert_called_once_with(
                items=query_out, filters=mock_client_side_filters
            )
            query_out = mock_apply_client_side_filters.return_value

        assert res == query_out

    return _runner_run_test_case


def test_run_with_subset_no_client_filters(runner_run_test_case):
    """
    Tests run() method functions expectedly - given subset and no client filters
    """
    runner_run_test_case(
        mock_from_subset=["item1", "item2", "item3"],
    )


def test_run_with_subset_and_client_filter(runner_run_test_case):
    """
    Tests run() method functions expectedly - given subset and client filters
    """
    runner_run_test_case(
        mock_client_side_filters=["client-filter1", "client-filter2"],
        mock_from_subset=["item1", "item2", "item3"],
    )


def test_run_with_server_side_filter_no_client_filter(runner_run_test_case):
    """
    Tests run() method functions expectedly - given subset and kwargs, no client filters
    """
    runner_run_test_case(
        mock_server_side_filters=["server-filter1", "server-filter2"],
        mock_kwargs={"arg1": "val1", "arg2": "val2"},
    )


def test_run_with_server_side_filter_and_client_filter(runner_run_test_case):
    """
    Tests run() method functions expectedly - given subset and client filters
    """
    runner_run_test_case(
        mock_client_side_filters=["client-filter1", "client-filter2"],
        mock_server_side_filters=["server-filter1", "server-filter2"],
    )


def test_run_both_server_filter_and_subset(instance):
    """
    Tests run() method functions expectedly - given subset and server filters
    should raise an error
    """
    with pytest.raises(RuntimeError):
        instance.run(
            cloud_account="test_account",
            from_subset=["item1", "item2"],
            server_side_filters=["server-filter1", "server-filter2"],
        )


@pytest.fixture(name="run_with_openstacksdk_test_case")
def run_with_openstacksdk_test_case_fixture(instance, mock_connection):
    """
    Fixture to test _run_with_openstacksdk with different test cases
    """

    def _run_with_openstacksdk_test_case(mock_server_filters, **mock_kwargs):
        with patch(
            "openstack_query.runners.runner_wrapper.RunnerWrapper._parse_meta_params"
        ) as mock_parse_meta_params:
            with patch(
                "openstack_query.runners.runner_wrapper.RunnerWrapper._run_query"
            ) as mock_run_query:
                mock_parse_meta_params.return_value = {"parsed_arg1": "val1"}
                mock_run_query.return_value = ["query_outputs"]
                res = instance._run_with_openstacksdk(
                    conn=mock_connection,
                    server_filters=mock_server_filters,
                    **mock_kwargs,
                )

        mock_parse_meta_params.assert_called_once_with(mock_connection, **mock_kwargs)
        run_query_kwargs = mock_parse_meta_params.return_value

        # check that run_query has been called correctly for each mock filter given
        for mock_filter in mock_server_filters:
            mock_run_query.assert_any_call(
                mock_connection, mock_filter, **run_query_kwargs
            )
        # assert that result contains concatenated results of mock_run_query
        assert res == [
            i for i in mock_run_query.return_value for _ in mock_server_filters
        ]

    return _run_with_openstacksdk_test_case


def test_run_with_openstacksdk_one_filter_and_kwargs(run_with_openstacksdk_test_case):
    """
    Tests _run_with_openstacksdk works properly - with one filter, and with kwargs
    """
    run_with_openstacksdk_test_case(
        [{"filter1": "val1"}], **{"arg1": "val1", "arg2": "val2"}
    )


def test_run_with_openstacksdk_one_filter_no_kwargs(run_with_openstacksdk_test_case):
    """
    Tests _run_with_openstacksdk works properly - with one filter, and with no kwargs
    """
    run_with_openstacksdk_test_case([{"filter1": "val1"}])


def test_run_with_openstacksdk_two_filters_no_kwargs(run_with_openstacksdk_test_case):
    """
    Tests _run_with_openstacksdk works properly - with two filters, and with no kwargs
    """
    run_with_openstacksdk_test_case([{"filter1": "val1"}, {"filter2": "val2"}])


def test_run_with_openstacksdk_two_filters_and_kwargs(run_with_openstacksdk_test_case):
    """
    Tests _run_with_openstacksdk works properly - with two filters, and with kwargs
    """
    run_with_openstacksdk_test_case(
        [{"filter1": "val1"}, {"filter2": "val2"}], **{"arg1": "val1", "arg2": "val2"}
    )


@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._parse_meta_params")
@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._run_query")
def test_run_with_openstacksdk_no_filters(
    mock_run_query, mock_parse_meta_params, instance, mock_connection
):
    """
    Tests _run_with_openstacksdk works properly - with no filters
    run_query should be called with no filters
    """
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    mock_parse_meta_params.return_value = {"parsed-arg1": "val1"}
    mock_run_query.return_value = ["query-output"]
    res = instance._run_with_openstacksdk(
        conn=mock_connection, server_filters=None, **mock_kwargs
    )

    mock_parse_meta_params.assert_called_once_with(mock_connection, **mock_kwargs)

    mock_run_query.assert_called_once_with(
        mock_connection, None, **mock_parse_meta_params.return_value
    )
    assert res == mock_run_query.return_value


@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._apply_client_side_filter")
def test_apply_client_side_filters_one_filter(mock_apply_client_side_filter, instance):
    """
    Tests that apply_client_side_filters method functions expectedly
    with one filter function
    method call apply_client_side_filter once with single filter function
    """
    mock_filter = ["filter1"]
    mock_items = ["openstack-resource-1", "openstack-resource-2"]
    res = instance._apply_client_side_filters(mock_items, mock_filter)
    mock_apply_client_side_filter.assert_called_once_with(mock_items, mock_filter[0])
    assert mock_apply_client_side_filter.return_value == res


@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._apply_client_side_filter")
def test_apply_client_side_filters_multi_filter(
    mock_apply_client_side_filter, instance
):
    """
    Tests that apply_client_side_filters method functions expectedly
    with one filter function
    method call apply_client_side_filter for each filter given
    """
    mock_filter = ["filter1", "filter2"]
    mock_items = "mock-items"
    mock_apply_client_side_filter.side_effect = ["filter-out-1", "filter-out-2"]
    res = instance._apply_client_side_filters(mock_items, mock_filter)

    assert mock_apply_client_side_filter.call_args_list == [
        call(mock_items, mock_filter[0]),
        call("filter-out-1", mock_filter[1]),
    ]
    assert res == "filter-out-2"


def test_apply_client_side_filter_no_items(instance):
    """
    Tests that apply_client_side_filter method functions expectedly
    method should run given client_filter with no items
    """
    mock_client_filter = MagicMock()
    mock_items = []
    res = instance._apply_client_side_filter(mock_items, mock_client_filter)
    mock_client_filter.assert_not_called()
    assert res == []


def test_apply_client_side_filter_one_item(instance):
    """
    Tests that apply_client_side_filter method functions expectedly
    method should run given client_filter with one item
    """
    mock_client_filter = MagicMock()
    mock_items = ["item1"]
    res = instance._apply_client_side_filter(mock_items, mock_client_filter)
    mock_client_filter.assert_called_once_with("item1")
    assert res == [mock_client_filter.return_value]


def test_apply_client_side_filter_one_many_items(instance):
    """
    Tests that apply_client_side_filter method functions expectedly
    method should run given client_filter with many items
    """
    mock_client_filter = MagicMock()
    mock_client_filter.side_effect = ["out1", "out2"]
    mock_items = ["item1", "item2"]
    res = instance._apply_client_side_filter(mock_items, mock_client_filter)
    mock_client_filter.assert_has_calls([call("item1"), call("item2")])
    assert res == ["out1", "out2"]


def test_run_pagination_query_gt_0(run_paginated_query_test):
    """
    Calls the testing case with various numbers of iterations
    to ensure pagination is working
    """
    for i in range(1, 3):
        run_paginated_query_test(i)
