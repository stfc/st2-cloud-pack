from unittest.mock import MagicMock, patch
import pytest
from openstack_query.query_executer import QueryExecuter
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with a mocked runner and prop enum class
    """
    mock_prop_enum_cls = MockProperties
    mock_runner = MagicMock()
    return QueryExecuter(mock_prop_enum_cls, mock_runner)


def test_set_filters(instance):
    """
    Tests that set_filters setter method works as expected
    """

    mock_client_filter = MagicMock()
    mock_server_side_filter = MagicMock()
    instance.set_filters(mock_client_filter, mock_server_side_filter)
    assert instance._client_side_filter_func == mock_client_filter
    assert instance._server_side_filters == mock_server_side_filter


def test_set_parse_func(instance):
    """
    Tests that set_parse_func setter method works as expected
    """
    mock_parser_func = MagicMock()
    instance.set_parse_func(mock_parser_func)
    assert instance._parser_func == mock_parser_func


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


@patch("openstack_query.query_executer.QueryExecuter.get_output")
def test_run_query_without_parser_func(mock_get_output, instance):
    """
    Tests that run_query works as expected - not parsing result
    Should call runner.run() and return a tuple of runner.run result and get_output result
    """

    instance._client_side_filter_func = MagicMock()
    instance._server_side_filters = MagicMock()
    instance._parser_func = None

    res1, res2 = instance.run_query(
        cloud_account="PROD", from_subset=["res1", "res2", "res3"], **{"arg1": "val1"}
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


@patch("openstack_query.query_executer.QueryExecuter.get_output")
def test_run_query_with_parser_func(mock_get_output, instance):
    """
    Tests that run_query works as expected - parsing result
    Should call runner.run() and then parser_func, and then output a tuple of
    parser_func result and get_output result
    """
    instance._client_side_filter_func = MagicMock()
    instance._server_side_filters = MagicMock()

    mock_parser_func = MagicMock()
    instance._parser_func = mock_parser_func

    res1, res2 = instance.run_query(
        cloud_account="PROD", from_subset=["res1", "res2", "res3"], **{"arg1": "val1"}
    )

    instance.runner.run.assert_called_once_with(
        cloud_account="prod",
        client_side_filter_func=instance._client_side_filter_func,
        server_side_filters=instance._server_side_filters,
        from_subset=["res1", "res2", "res3"],
        **{"arg1": "val1"}
    )

    mock_parser_func.assert_called_once_with(instance.runner.run.return_value)
    mock_get_output.assert_called_once_with(mock_parser_func.return_value)

    assert res1 == mock_parser_func.return_value
    assert res2 == mock_get_output.return_value
