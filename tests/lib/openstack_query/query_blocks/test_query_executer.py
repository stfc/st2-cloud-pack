from unittest.mock import MagicMock, NonCallableMock, patch, call
import pytest

from openstack_query.query_blocks.query_executer import QueryExecuter
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(scope="function", name="mock_connection_cls")
def mock_connection_cls_fixture():
    """
    Returns a mocked OpenstackConnection class
    """
    return MagicMock()


@pytest.fixture(name="instance")
def instance_fixture(mock_connection_cls):
    """
    Returns an instance with a mocked runner and prop enum class
    """
    mock_prop_enum_cls = MockProperties
    mock_runner_cls = MagicMock()
    with patch("openstack_query.query_blocks.query_executer.ResultsContainer"):
        return QueryExecuter(mock_prop_enum_cls, mock_runner_cls, mock_connection_cls)


def test_client_side_filter_func(instance):
    """
    Tests that client_side_filter_func property works as expected
    """
    mock_client_filter = MagicMock()
    instance.client_side_filter_func = mock_client_filter
    assert instance.client_side_filter_func == mock_client_filter


def test_server_side_filters(instance):
    """
    Tests that server_side_filters property works as expected
    """
    mock_client_filter = MagicMock()
    instance.server_side_filters = mock_client_filter
    assert instance.server_side_filters == mock_client_filter


def test_apply_forwarded_results(instance):
    """
    Test apply_forwarded_results method - should forward to results_container
    and set has_forwarded_results flag to True
    """
    mock_link_prop = NonCallableMock()
    mock_results = NonCallableMock()
    instance.apply_forwarded_results(mock_link_prop, mock_results)
    instance.results_container.apply_forwarded_results.assert_called_once_with(
        mock_link_prop, mock_results
    )
    assert instance.has_forwarded_results


@pytest.fixture(name="run_with_openstacksdk_runner")
def run_with_openstacksdk_runner_fixture(instance, mock_connection_cls):
    """
    Fixture to run run_with_openstacksdk() test cases with different args
    """

    @patch("openstack_query.runners.runner_utils.RunnerUtils.apply_client_side_filters")
    def _run_with_openstacksdk_runner(
        mock_server_side_filters,
        use_client_side_filters,
        mock_apply_client_side_filters,
    ):
        """
        method to run_with_openstacksdk() test case with provided input values
        The individual methods that are called in run must be patched out by the test function
        prior to this and any asserts need to be done by the test function
        """
        mock_cloud_account = NonCallableMock()
        mock_kwargs = {"arg1": "val1", "arg2": "val2"}

        mock_meta_params = {"meta-arg1": "val1", "meta-arg2": "val2"}
        instance.runner.parse_meta_params.return_value = mock_meta_params

        mock_run_query_out = NonCallableMock()
        instance.runner.run_query.return_value = [mock_run_query_out]

        mock_conn = mock_connection_cls.return_value.__enter__.return_value

        mock_client_side_filters = None
        if use_client_side_filters:
            mock_client_side_filters = NonCallableMock()

        instance.run_with_openstacksdk(
            cloud_account=mock_cloud_account,
            client_side_filters=mock_client_side_filters,
            server_side_filters=mock_server_side_filters,
            **mock_kwargs,
        )

        mock_connection_cls.assert_called_once_with(mock_cloud_account)

        instance.runner.parse_meta_params.assert_called_once_with(
            mock_conn,
            **mock_kwargs,
        )

        if mock_server_side_filters:
            instance.runner.run_query.assert_has_calls(
                [
                    call(mock_conn, mock_filter, **mock_meta_params)
                    for mock_filter in mock_server_side_filters
                ]
            )
            query_out = [mock_run_query_out for _ in mock_server_side_filters]

        else:
            instance.runner.run_query.assert_called_once_with(
                mock_conn, None, **mock_meta_params
            )
            query_out = [mock_run_query_out]

        if use_client_side_filters:
            mock_apply_client_side_filters.assert_called_once_with(
                query_out, mock_client_side_filters
            )
            query_out = mock_apply_client_side_filters.return_value
        instance.results_container.store_query_results.assert_called_once_with(
            query_out
        )

    return _run_with_openstacksdk_runner


def test_run_with_openstacksdk_one_server_filter(run_with_openstacksdk_runner):
    """
    Tests run_with_openstacksdk with one server filter no client filters
    """
    run_with_openstacksdk_runner(
        [{"filter1": "val1"}],
        False,
    )


def test_run_with_openstacksdk_one_server_and_client_filter(
    run_with_openstacksdk_runner,
):
    """
    Tests run_with_openstacksdk with one server filter and client filters
    """
    run_with_openstacksdk_runner(
        [{"filter1": "val1"}],
        True,
    )


def test_run_with_openstacksdk_multi_server_and_client_filters(
    run_with_openstacksdk_runner,
):
    """
    Tests run_with_openstacksdk with multiple server filters and client filters
    """
    run_with_openstacksdk_runner(
        [{"filter1": "val1"}, {"filter2": "val2"}],
        True,
    )


def test_run_with_openstacksdk_multi_server_filters(run_with_openstacksdk_runner):
    """
    Tests run_with_openstacksdk with multiple server filters and no client filters
    """
    run_with_openstacksdk_runner(
        [{"filter1": "val1"}, {"filter2": "val2"}],
        False,
    )


def test_run_with_openstacksdk_no_filters(run_with_openstacksdk_runner):
    """
    Tests run_with_openstacksdk with no server filters
    """
    run_with_openstacksdk_runner(None, False)


@patch("openstack_query.runners.runner_utils.RunnerUtils.apply_client_side_filters")
def test_with_subset(mock_apply_client_side_filters, instance):
    """
    Tests run_with_subset
    """
    mock_subset = NonCallableMock()
    mock_client_filters = NonCallableMock()
    instance.run_with_subset(mock_subset, mock_client_filters)
    instance.runner.parse_subset.assert_called_once_with(mock_subset)

    mock_apply_client_side_filters.assert_called_once_with(
        instance.runner.parse_subset.return_value, mock_client_filters
    )

    instance.results_container.store_query_results.assert_called_once_with(
        mock_apply_client_side_filters.return_value
    )
