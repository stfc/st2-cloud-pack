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
    query_executer = QueryExecuter(mock_prop_enum_cls, mock_runner_cls)
    query_executer._results = MagicMock()
    return query_executer


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


def test_raw_results(instance):
    """
    Tests that raw_results property method works as expected
    """
    mock_raw_results = MagicMock()
    instance.raw_results = mock_raw_results
    assert instance.raw_results == mock_raw_results


def test_get_output_list_input(instance):
    """
    Tests that get_output method works as expected - when given a list
    Should output the results of calling function stored in output_func attribute with given list
    """
    mock_out = [1, 2, 3]

    def output_func(_):
        return mock_out

    output = instance.get_output(output_func, ["mock-result1"])
    assert output == mock_out


def test_get_output_dict_input(instance):
    """
    Tests that get_output method works as expected - when given a grouped output (dictionary)
    Should output a dictionary, with values being the output of calling output_func with each group
    """
    mock_out = [1, 2, 3]
    expected_out = {"group1": mock_out, "group2": mock_out}

    def output_func(_):
        return mock_out

    output = instance.get_output(
        output_func, {"group1": ["mock-results"], "group2": ["mock-results2"]}
    )
    assert output == expected_out


def test_get_output_no_output_func(instance):
    """
    Tests that get_output method works as expected - when given no ouptut_func
    Should output an empty list
    """
    instance._output_func = None
    output = instance.get_output(None, ["mock-results1"])
    assert output == []


def test_run_query(instance):
    """
    Tests that run_query method works as expected
    simply calls runner.run() and saves result in raw_results
    """
    instance.client_side_filters = MagicMock()
    instance.server_side_filters = MagicMock()

    instance.run_query(
        cloud_account=CloudDomains.PROD,
        from_subset="some-subset",
        **{"arg1": "val1", "arg2": "val2"}
    )

    instance.result_container.set_from_query_results.assert_called_once_with(
        instance.runner.run.return_value
    )

    instance.runner.run.assert_called_once_with(
        cloud_account="prod",
        client_side_filters=instance.client_side_filters,
        server_side_filters=instance.server_side_filters,
        from_subset="some-subset",
        **{"arg1": "val1", "arg2": "val2"}
    )


def test_run_query_with_string_domain(instance):
    """
    Tests that run_query method works as expected
    simply calls runner.run() and saves result in raw_results
    """
    instance.client_side_filters = MagicMock()
    instance.server_side_filters = MagicMock()

    instance.run_query(
        cloud_account="domain",
        from_subset="some-subset",
        **{"arg1": "val1", "arg2": "val2"}
    )

    instance.result_container.set_from_query_results.assert_called_once_with(
        instance.runner.run.return_value
    )

    instance.runner.run.assert_called_once_with(
        cloud_account="domain",
        client_side_filters=instance.client_side_filters,
        server_side_filters=instance.server_side_filters,
        from_subset="some-subset",
        **{"arg1": "val1", "arg2": "val2"}
    )


def test_parse_results_no_parse_func(instance):
    """
    Tests that parse_results method works as expected
    should return list of openstack objects and output of get_output()
    """
    results = [("res1", {}), ("res2", {})]
    instance.result_container.output.return_value = results

    with patch(
        "openstack_query.query_blocks.query_executer.QueryExecuter.get_output"
    ) as mock_get_output:
        res1, res2 = instance.parse_results(None, "output_func")

    instance.result_container.output.assert_called_once()
    assert res1 == ["res1", "res2"]
    mock_get_output.assert_called_once_with("output_func", results)
    assert res2 == mock_get_output.return_value


def test_parse_results_with_parse_func_with_grouping(instance):
    """
    Tests that parse_results method works as expected
    should return grouped openstack resources, and get_output() output tuple
    """
    results = [("res1", {}), ("res2", {}), ("res3", {})]
    parsed_results = {"group1": [("res1", {})], "group2": [("res2", {}), ("res3", {})]}
    parse_func = MagicMock()
    parse_func.return_value = parsed_results
    instance.result_container.output.return_value = results

    output_func = "output_func"

    with patch(
        "openstack_query.query_blocks.query_executer.QueryExecuter.get_output"
    ) as mock_get_output:
        res1, res2 = instance.parse_results(parse_func, output_func)

    instance.result_container.output.assert_called_once()
    parse_func.assert_called_once_with(instance.result_container.output.return_value)
    assert res1 == {"group1": ["res1"], "group2": ["res2", "res3"]}

    mock_get_output.assert_called_once_with("output_func", parsed_results)
    assert res2 == mock_get_output.return_value


def test_parse_results_with_parse_func_no_grouping(instance):
    """
    Tests that parse_results method works as expected
    should return openstack resources list, and get_output() output tuple
    """
    results = [("res1", {}), ("res2", {}), ("res3", {})]
    parsed_results = [("res3", {}), ("res2", {}), ("res1", {})]

    parse_func = MagicMock()
    parse_func.return_value = parsed_results
    instance.result_container.output.return_value = results

    output_func = "output_func"

    with patch(
        "openstack_query.query_blocks.query_executer.QueryExecuter.get_output"
    ) as mock_get_output:
        res1, res2 = instance.parse_results(parse_func, output_func)

    instance.result_container.output.assert_called_once()
    parse_func.assert_called_once_with(instance.result_container.output.return_value)
    assert res1 == ["res3", "res2", "res1"]

    mock_get_output.assert_called_once_with("output_func", parsed_results)
    assert res2 == mock_get_output.return_value
