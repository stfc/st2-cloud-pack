from unittest.mock import MagicMock, patch, call
import pytest

from openstack_query.query_blocks.results_container import ResultsContainer
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="setup_instance_with_results")
def setup_instance_with_results_fixture():
    """
    Returns an instance of ResultContainer with mocked results
    """

    def _setup_instance_with_results(mock_results):
        val = ResultsContainer(prop_enum_cls=MockProperties)
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
    instance.to_objects()


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
