from unittest.mock import MagicMock, NonCallableMock
import pytest

from enums.cloud_domains import CloudDomains
from openstack_query.query_blocks.query_executer import QueryExecuter
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with a mocked runner and prop enum class
    """
    mock_prop_enum_cls = MockProperties
    mock_runner_cls = MagicMock()
    query_executer = QueryExecuter(mock_prop_enum_cls, mock_runner_cls)
    query_executer._results_container = MagicMock()
    return query_executer


def test_results_container(instance):
    """
    Tests that results container property works as expected
    """
    mock_results_container = instance._results_container
    assert instance.results_container == mock_results_container


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


@pytest.mark.parametrize(
    "mock_cloud_account, expected_cloud_account_str",
    [(CloudDomains.PROD, "prod"), ("domain", "domain")],
)
def test_run_query(mock_cloud_account, expected_cloud_account_str, instance):
    """
    Tests that run_query method works as expected
    simply calls runner.run() and saves result in raw_results
    """
    instance.client_side_filters = MagicMock()
    instance.server_side_filters = MagicMock()

    instance.run_query(
        cloud_account=mock_cloud_account,
        from_subset="some-subset",
        **{"arg1": "val1", "arg2": "val2"}
    )

    instance.results_container.store_query_results.assert_called_once_with(
        instance.runner.run.return_value
    )

    instance.runner.run.assert_called_once_with(
        cloud_account=expected_cloud_account_str,
        client_side_filters=instance.client_side_filters,
        server_side_filters=instance.server_side_filters,
        from_subset="some-subset",
        **{"arg1": "val1", "arg2": "val2"}
    )


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
