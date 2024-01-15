from unittest.mock import MagicMock, patch, call, NonCallableMock
import pytest

from exceptions.query_chaining_error import QueryChainingError
from openstack_query.query_blocks.results_container import ResultsContainer
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="setup_instance_with_results")
def setup_instance_with_results_fixture():
    """
    Returns an instance of ResultContainer with mocked results
    """

    def _setup_instance_with_results(mock_results):
        val = ResultsContainer(prop_enum_cls=MockProperties)
        # pylint:disable=protected-access
        val._results = mock_results
        return val

    return _setup_instance_with_results


def test_to_props_results_empty(setup_instance_with_results):
    """
    Test to_props method when results are empty - return empty list
    """
    instance = setup_instance_with_results([])
    instance.to_props(MockProperties.PROP_1, MockProperties.PROP_2)


def test_to_props_not_parsed(setup_instance_with_results):
    """
    Test to_props method when results are not parsed
    """
    mock_res1 = MagicMock()
    mock_res2 = MagicMock()

    instance = setup_instance_with_results([mock_res1, mock_res2])
    res = instance.to_props(MockProperties.PROP_1, MockProperties.PROP_2)

    mock_res1.as_props.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2
    )

    mock_res2.as_props.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2
    )

    assert res == [mock_res1.as_props.return_value, mock_res2.as_props.return_value]


def test_to_props_parsed_to_list(setup_instance_with_results):
    """
    Test to_props method when results are parsed into a list
    """

    def mock_parse_func(results):
        """a parse func that doesn't do anything"""
        return results

    mock_res1 = MagicMock()
    mock_res2 = MagicMock()

    instance = setup_instance_with_results([mock_res1, mock_res2])
    instance.parse_results(mock_parse_func)

    res = instance.to_props(MockProperties.PROP_1, MockProperties.PROP_2)

    mock_res1.as_props.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2
    )

    mock_res2.as_props.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2
    )

    assert res == [mock_res1.as_props.return_value, mock_res2.as_props.return_value]


def test_to_props_parsed_and_grouped(setup_instance_with_results):
    """
    Test to_props method when results are parsed into a dict (grouped)
    """

    def mock_parse_func(results):
        """a parse func that returns a dictionary"""
        return {"group1": [results[0]], "group2": [results[1]]}

    mock_res1 = MagicMock()
    mock_res2 = MagicMock()

    instance = setup_instance_with_results([mock_res1, mock_res2])
    instance.parse_results(mock_parse_func)

    res = instance.to_props(MockProperties.PROP_1, MockProperties.PROP_2)

    mock_res1.as_props.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2
    )

    mock_res2.as_props.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2
    )

    assert res == {
        "group1": [mock_res1.as_props.return_value],
        "group2": [mock_res2.as_props.return_value],
    }


def test_to_objects_results_empty(setup_instance_with_results):
    """
    Test to_objects method when results are empty - return empty list
    """
    instance = setup_instance_with_results([])
    res = instance.to_objects()
    assert res == []


def test_to_objects_not_parsed(setup_instance_with_results):
    """
    Test to_objects method when results are not parsed
    """
    mock_res1 = MagicMock()
    mock_res2 = MagicMock()

    instance = setup_instance_with_results([mock_res1, mock_res2])
    res = instance.to_objects()

    mock_res1.as_object.assert_called_once()

    mock_res2.as_object.assert_called_once()

    assert res == [mock_res1.as_object.return_value, mock_res2.as_object.return_value]


def test_to_object_parsed_to_list(setup_instance_with_results):
    """
    Test to_object method when results are parsed into a list
    """

    def mock_parse_func(results):
        """a parse func that doesn't do anything"""
        return results

    mock_res1 = MagicMock()
    mock_res2 = MagicMock()

    instance = setup_instance_with_results([mock_res1, mock_res2])
    instance.parse_results(mock_parse_func)

    res = instance.to_objects()
    mock_res1.as_object.assert_called_once()
    mock_res2.as_object.assert_called_once()

    assert res == [mock_res1.as_object.return_value, mock_res2.as_object.return_value]


def test_to_object_parsed_and_grouped(setup_instance_with_results):
    """
    Test to_object method when results are parsed into a dict (grouped)
    """

    def mock_parse_func(results):
        """a parse func that returns a dictionary"""
        return {"group1": [results[0]], "group2": [results[1]]}

    mock_res1 = MagicMock()
    mock_res2 = MagicMock()

    instance = setup_instance_with_results([mock_res1, mock_res2])
    instance.parse_results(mock_parse_func)

    res = instance.to_objects()
    mock_res1.as_object.assert_called_once()
    mock_res2.as_object.assert_called_once()

    assert res == {
        "group1": [mock_res1.as_object.return_value],
        "group2": [mock_res2.as_object.return_value],
    }


@patch("openstack_query.query_blocks.results_container.Result")
def test_store_query_results(mock_results):
    """
    Test store_query_results method creates a Result mock object for each item given
    """
    mock_prop_enum_cls = NonCallableMock()
    instance = ResultsContainer(mock_prop_enum_cls)
    instance.store_query_results(["item1", "item2"])
    mock_results.side_effect = ["item1_obj", "item2_obj"]

    mock_results.assert_has_calls(
        [
            call(mock_prop_enum_cls, "item1", "Not Found"),
            call(mock_prop_enum_cls, "item2", "Not Found"),
        ]
    )


@patch(
    "openstack_query.query_blocks.results_container.ResultsContainer._get_forwarded_result"
)
def test_apply_forwarded_result(mock_get_forwarded_result, setup_instance_with_results):
    """
    Test apply_forwarded_results once results set
    """
    res1 = MagicMock()
    res2 = MagicMock()
    mock_link_prop = NonCallableMock()
    mock_forwarded_results = NonCallableMock()

    instance = setup_instance_with_results([res1, res2])
    instance.apply_forwarded_results(mock_link_prop, mock_forwarded_results)

    res1.get_prop.assert_called_once_with(mock_link_prop)
    res2.get_prop.assert_called_once_with(mock_link_prop)

    mock_get_forwarded_result.assert_has_calls(
        [
            call(res1.get_prop.return_value, mock_forwarded_results),
            call(res2.get_prop.return_value, mock_forwarded_results),
        ]
    )

    res1.update_forwarded_properties(mock_get_forwarded_result.return_value)
    res2.update_forwarded_properties(mock_get_forwarded_result.return_value)


def test_get_forwarded_results_many_to_one():
    """
    Tests get_forwarded_results static method, where forwarded results contains
    multiple instances in each group.
    should remove value from forwarded result from the group one at a time as
    it is encountered, except the last one
    """
    forwarded_values = {
        "grouped_value": ["value1", "value2", "value3"],
    }
    # pylint:disable=protected-access

    assert (
        ResultsContainer._get_forwarded_result("grouped_value", forwarded_values)
        == "value1"
    )
    assert (
        ResultsContainer._get_forwarded_result("grouped_value", forwarded_values)
        == "value2"
    )
    assert (
        ResultsContainer._get_forwarded_result("grouped_value", forwarded_values)
        == "value3"
    )
    assert len(forwarded_values["grouped_value"]) == 1


def test_get_forwarded_result_one_to_many():
    """
    Tests get_forwarded_results static method, where forwarded results contains
    one instance in each group.

    Should not remove forwarded result as there is only one item in each group.
    Duplicate calls with the same value should return the same result
    """
    forwarded_values = {
        "grouped_value1": ["value1"],
        "grouped_value2": ["value2"],
        "grouped_value3": ["value3"],
    }
    # pylint:disable=protected-access

    assert (
        ResultsContainer._get_forwarded_result("grouped_value1", forwarded_values)
        == "value1"
    )
    assert (
        ResultsContainer._get_forwarded_result("grouped_value1", forwarded_values)
        == "value1"
    )

    assert (
        ResultsContainer._get_forwarded_result("grouped_value2", forwarded_values)
        == "value2"
    )
    assert (
        ResultsContainer._get_forwarded_result("grouped_value2", forwarded_values)
        == "value2"
    )

    assert all(len(val) == 1 for val in forwarded_values.values())


def test_get_forwarded_result_empty():
    """
    Tests get_forwarded_results static method, where forwarded results are empty
    should return an empty dict
    """
    # pylint:disable=protected-access
    assert ResultsContainer._get_forwarded_result("grouped_value1", {}) == {}
