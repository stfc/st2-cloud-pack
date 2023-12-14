from unittest.mock import MagicMock
from openstack_query.runners.runner_utils import RunnerUtils


def run_paginated_query_test(number_iterations):
    """
    tests that run_paginated_query works expectedly - with one round or more of pagination
    mocked paginated call simulates the effect of retrieving a list of values up to a limit and then calling the
    same call again with a "marker" set to the last seen item to continue reading
    """
    mock_paginated_call = MagicMock()
    mock_marker_prop_func = MagicMock(wraps=lambda resource: resource["id"])
    mock_server_side_filter_set = {"arg1": "val1", "arg2": "val2"}

    pagination_order = []
    expected_out = []

    for i in range(0, number_iterations - 1):
        # Generate markers, it's a list of results with an ID
        marker = {"id": f"marker{i}"}
        expected_out.append(marker)
        pagination_order.append([marker])

    pagination_order.append([])

    mock_paginated_call.side_effect = pagination_order

    res = RunnerUtils.run_paginated_query(
        mock_paginated_call,
        mock_marker_prop_func,
        mock_server_side_filter_set,
        # set page_size to 1, so new calls begins after returning one value
        1,
        10,
    )
    assert res == expected_out


def test_run_pagination_query_gt_0():
    """
    Calls the testing case with various numbers of iterations
    to ensure pagination is working
    """
    for i in range(1, 3):
        run_paginated_query_test(i)


def test_apply_client_side_filters_one_item_one_filter_passes():
    """
    tests apply_client_side_filters method.
    Should run one filter on one item which should pass
    Should return same list as inputted
    """
    mock_filter_1 = MagicMock()
    mock_filter_1.return_value = True

    mock_item = MagicMock()
    assert RunnerUtils.apply_client_side_filters([mock_item], [mock_filter_1]) == [
        mock_item
    ]


def test_apply_client_side_filters_one_item_one_filter_fails():
    """
    tests apply_client_side_filters method.
    Should run one filter on one item which should fail
    Should return empty list
    """

    mock_filter_1 = MagicMock()
    mock_filter_1.return_value = False

    mock_item = MagicMock()
    assert RunnerUtils.apply_client_side_filters([mock_item], [mock_filter_1]) == []


def test_apply_client_side_filters_many_items_one_filter():
    """
    tests apply_client_side_filters method
    Should run one filter on each item, should return item that passes filter
    """

    mock_filter_1 = MagicMock()
    mock_filter_1.side_effect = [True, False]
    mock_item_1 = MagicMock()
    mock_item_2 = MagicMock()

    assert RunnerUtils.apply_client_side_filters(
        [mock_item_1, mock_item_2], [mock_filter_1]
    ) == [mock_item_1]


def test_apply_client_side_filters_many_items_many_filters():
    """
    tests apply_client_side_filters method
    Should run each filter on each item
    only first item which passes both filters should be returned
    """

    mock_item_1 = MagicMock()
    mock_item_2 = MagicMock()
    mock_item_3 = MagicMock()
    mock_item_4 = MagicMock()

    mock_filter_1 = MagicMock()
    mock_filter_2 = MagicMock()

    mock_filter_1.side_effect = [True, True, False, False]
    mock_filter_2.side_effect = [True, False, True, False]

    assert RunnerUtils.apply_client_side_filters(
        [mock_item_1, mock_item_2, mock_item_3, mock_item_4],
        [mock_filter_1, mock_filter_2],
    ) == [mock_item_1]
