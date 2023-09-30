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


@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._apply_client_side_filter")
@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._run_query")
@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._parse_meta_params")
def test_run_with_only_client_side_filter(
    mock_parse_meta_params,
    mock_run_query,
    mock_apply_client_side_filter,
    instance,
    mock_connection,
    mock_openstack_connection,
):
    """
    Tests that run method functions expectedly - with only client_side_filter_func set
    method should call run_query and run apply_client_side_filter and return results
    also tests with no meta-params set
    """

    mock_run_query.return_value = ["openstack-resource-1", "openstack-resource-2"]
    mock_apply_client_side_filter.return_value = ["openstack-resource-1"]

    mock_client_side_filter_func = MagicMock()
    mock_cloud_domain = MagicMock()

    res = instance.run(
        cloud_account=mock_cloud_domain,
        client_side_filter_func=mock_client_side_filter_func,
    )
    mock_connection.assert_called_once_with(mock_cloud_domain)

    mock_parse_meta_params.assert_not_called()
    mock_run_query.assert_called_once_with(mock_openstack_connection, None)

    mock_apply_client_side_filter.assert_called_once_with(
        ["openstack-resource-1", "openstack-resource-2"],
        mock_client_side_filter_func,
    )
    mock_client_side_filter_func.assert_not_called()
    assert ["openstack-resource-1"] == res


@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._run_query")
@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._parse_meta_params")
def test_run_with_server_side_filters(
    mock_parse_meta_params,
    mock_run_query,
    instance,
    mock_connection,
    mock_openstack_connection,
):
    """
    Tests that run method functions expectedly - with server_side_filters set
    method should call run_query and return results
    """
    mock_server_filters = {"server_filter1": "abc", "server_filter2": False}
    mock_run_query.return_value = ["openstack-resource-1"]
    instance._run_query = mock_run_query
    mock_client_side_filter_func = MagicMock()
    mock_user_domain = MagicMock()

    mock_parse_meta_params.return_value = {
        "parsed_arg1": "val1",
        "parsed_arg2": "val2",
    }

    res = instance.run(
        cloud_account=mock_user_domain,
        client_side_filter_func=mock_client_side_filter_func,
        server_side_filters=mock_server_filters,
        **{"arg1": "val1", "arg2": "val2"},
    )
    mock_connection.assert_called_once_with(mock_user_domain)

    mock_parse_meta_params.assert_called_once_with(
        mock_openstack_connection, **{"arg1": "val1", "arg2": "val2"}
    )

    mock_run_query.assert_called_once_with(
        mock_openstack_connection,
        mock_server_filters,
        **{"parsed_arg1": "val1", "parsed_arg2": "val2"},
    )

    # if we have server-side filters, don't use client_side_filters
    mock_client_side_filter_func.assert_not_called()
    assert res == ["openstack-resource-1"]


@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._parse_subset")
@patch("openstack_query.runners.runner_wrapper.RunnerWrapper._apply_client_side_filter")
def test_run_with_subset(
    mock_apply_filter_func,
    mock_parse_subset,
    instance,
    mock_connection,
    mock_openstack_connection,
):
    """
    Tests that run method functions expectedly - with meta param 'from_subset' set
    method should run parse_subset on 'from_subset' values and then apply_client_side_filter and return results
    """
    mock_parse_subset.return_value = [
        "parsed-openstack-resource-1",
        "parsed-openstack-resource-2",
    ]
    mock_apply_filter_func.return_value = ["parsed-openstack-resource-1"]
    mock_client_side_filter_func = MagicMock()
    mock_cloud_domain = MagicMock()

    res = instance.run(
        cloud_account=mock_cloud_domain,
        client_side_filter_func=mock_client_side_filter_func,
        from_subset=["openstack-resource-1", "openstack-resource-2"],
    )
    mock_connection.assert_any_call(mock_cloud_domain)

    mock_parse_subset.assert_called_once_with(
        mock_openstack_connection, ["openstack-resource-1", "openstack-resource-2"]
    )

    mock_apply_filter_func.assert_called_once_with(
        ["parsed-openstack-resource-1", "parsed-openstack-resource-2"],
        mock_client_side_filter_func,
    )
    assert res == ["parsed-openstack-resource-1"]


def test_apply_filter_func(instance):
    """
    Tests that apply_filter_func method functions expectedly
    method should iteratively run filter_func on each item and return only those that filter_function returned True
    """
    mock_client_side_filter_func = MagicMock()
    mock_client_side_filter_func.side_effect = [False, True]

    mock_items = ["openstack-resource-1", "openstack-resource-2"]

    res = instance._apply_client_side_filter(mock_items, mock_client_side_filter_func)
    assert ["openstack-resource-2"] == res


def test_run_pagination_query_gt_0(run_paginated_query_test):
    """
    Calls the testing case with various numbers of iterations
    to ensure pagination is working
    """
    for i in range(1, 3):
        run_paginated_query_test(i)
