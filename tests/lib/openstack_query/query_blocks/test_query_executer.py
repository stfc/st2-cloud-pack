from unittest.mock import MagicMock, patch
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
    return QueryExecuter(mock_prop_enum_cls, mock_runner_cls)


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


def test_parse_func(instance):
    """
    Tests that parse_func property works as expected
    """
    mock_parse_func = MagicMock()
    instance.parse_func = mock_parse_func
    assert instance.parse_func == mock_parse_func


def test_output_func(instance):
    """
    Tests that output_func property method works as expected
    """
    mock_output_func = MagicMock()
    instance.output_func = mock_output_func
    assert instance.output_func == mock_output_func


def test_get_output_list_input(instance):
    """
    Tests that get_output method works as expected - when given a list
    Should output the results of calling function stored in output_func attribute with given list
    """
    mock_out = [1, 2, 3]
    instance._output_func = lambda _: mock_out
    output = instance.get_output(["mock-result1"])
    assert output == mock_out


def test_get_output_dict_input(instance):
    """
    Tests that get_output method works as expected - when given a grouped output (dictionary)
    Should output a dictionary, with values being the output of calling output_func with each group
    """
    mock_out = [1, 2, 3]
    expected_out = {"group1": mock_out, "group2": mock_out}
    instance._output_func = lambda _: mock_out
    output = instance.get_output(
        {"group1": ["mock-results"], "group2": ["mock-results2"]}
    )
    assert output == expected_out


def test_get_output_no_output_func(instance):
    """
    Tests that get_output method works as expected - when given no ouptut_func
    Should output an empty list
    """
    instance._output_func = None
    output = instance.get_output(["mock-results1"])
    assert output == []


@patch("openstack_query.query_blocks.query_executer.QueryExecuter.get_output")
def test_run_query_without_parse_func(mock_get_output, instance):
    """
    Tests that run_query works as expected - not parsing result
    Should call runner.run() and return a tuple of runner.run result and get_output result
    """

    instance._client_side_filter_func = MagicMock()
    instance._server_side_filters = MagicMock()
    instance._parse_func = None

    res1, res2 = instance.run_query(
        cloud_account=CloudDomains.PROD,
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    instance.runner.run.assert_called_once_with(
        cloud_account="prod",
        client_side_filter_func=instance._client_side_filter_func,
        server_side_filters=instance._server_side_filters,
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    mock_get_output.assert_called_once_with(instance.runner.run.return_value)
    assert res1 == instance.runner.run.return_value
    assert res2 == mock_get_output.return_value


@patch("openstack_query.query_blocks.query_executer.QueryExecuter.get_output")
def test_run_query_with_parse_func(mock_get_output, instance):
    """
    Tests that run_query works as expected - parsing result
    Should call runner.run() and then parse_func, and then output a tuple of
    parse_func result and get_output result
    """
    instance._client_side_filter_func = MagicMock()
    instance._server_side_filters = MagicMock()

    mock_parse_func = MagicMock()
    instance._parse_func = mock_parse_func

    res1, res2 = instance.run_query(
        cloud_account=CloudDomains.PROD,
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    instance.runner.run.assert_called_once_with(
        cloud_account="prod",
        client_side_filter_func=instance._client_side_filter_func,
        server_side_filters=instance._server_side_filters,
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    mock_parse_func.assert_called_once_with(instance.runner.run.return_value)
    mock_get_output.assert_called_once_with(mock_parse_func.return_value)

    assert res1 == mock_parse_func.return_value
    assert res2 == mock_get_output.return_value


@patch("openstack_query.query_blocks.query_executer.QueryExecuter.get_output")
def test_run_query_with_string_as_domain(mock_get_output, instance):
    """
    Tests that run_query works as expected - not parsing result, with a string as cloud account
    Should call runner.run() and return a tuple of runner.run result and get_output result
    """

    instance._client_side_filter_func = MagicMock()
    instance._server_side_filters = MagicMock()
    instance._parse_func = None

    res1, res2 = instance.run_query(
        cloud_account="test-account",
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    instance.runner.run.assert_called_once_with(
        cloud_account="test-account",
        client_side_filter_func=instance._client_side_filter_func,
        server_side_filters=instance._server_side_filters,
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    mock_get_output.assert_called_once_with(instance.runner.run.return_value)
    assert res1 == instance.runner.run.return_value
    assert res2 == mock_get_output.return_value
