import copy
from unittest.mock import MagicMock, patch, call, NonCallableMock
import pytest

from openstack_query.query_blocks.results_container import ResultsContainer
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="setup_instance_with_results")
def setup_instance_with_results_fixture():
    """
    Fixture to get setup an instance of ResultsContainer with a set of mock results
    """

    @patch("openstack_query.query_blocks.results_container.Result")
    def _setup_instance(results, mock_result_obj):
        """
        sets up a ResultsContainer storing set of results given
        """
        instance = ResultsContainer(prop_enum_cls=MockProperties)
        mock_result_obj.side_effect = results
        instance.store_query_results(query_results=results)
        mock_result_obj.assert_has_calls(
            [call(MockProperties, i, instance.DEFAULT_OUT) for i in results]
        )
        return instance

    return _setup_instance


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


def test_apply_forwarded_result_empty():
    """
    Test apply_forwarded_results when no results set - do nothing
    """
    instance = ResultsContainer(NonCallableMock())
    instance.apply_forwarded_results(NonCallableMock(), NonCallableMock())
    assert instance.to_props() == []


def mock_result(get_prop_return):
    """
    Helper function to mock a Result object with a mocked value to return when get_prop() is called
    """
    mock_prop = MagicMock()
    mock_prop.get_prop.return_value = get_prop_return
    return mock_prop


@pytest.fixture(name="apply_forwarded_result_runner")
def apply_forwarded_result_runner_fixture(setup_instance_with_results):
    """
    Fixture to setup and run a test case for testing apply_forwarded_result method
    """

    def _apply_forwarded_result_runner(
        mock_set_results, mock_forwarded_results, expected_updated_call_args
    ):
        """runs apply forwarded result runner test case"""

        result_mocks = [mock_result(res) for res in mock_set_results]

        instance = setup_instance_with_results(result_mocks)
        mock_link_prop = NonCallableMock()
        instance.apply_forwarded_results(mock_link_prop, mock_forwarded_results)
        for result in result_mocks:
            result.get_prop.assert_called_once_with(mock_link_prop)

        for mock, exp in zip(result_mocks, expected_updated_call_args):
            mock.update_forwarded_properties.assert_called_once_with(exp)

        return result_mocks

    return _apply_forwarded_result_runner


def test_apply_forwarded_result_many_to_one(apply_forwarded_result_runner):
    """
    test apply_forwarded_results with results already set,
    where multiple forwarded outputs map to one openstack object.
    should take the first item from matching list and assign it,
    deleting it from the forwarded dict
    """

    mock_forwarded_results = {
        "val1": ["forward-props1", "forward-props2"],
        "val2": ["forward-props3", "forward-props4"],
    }
    expected_updated_call_args = [
        "forward-props1",
        "forward-props3",
        "forward-props2",
        "forward-props4",
    ]
    apply_forwarded_result_runner(
        ["val1", "val2", "val1", "val2"],
        mock_forwarded_results,
        expected_updated_call_args,
    )

    # test that forward_results dict is mutated removing values already assigned
    # keeping at least one value at the end
    assert mock_forwarded_results == {
        "val1": ["forward-props2"],
        "val2": ["forward-props4"],
    }


def test_apply_forwarded_result_one_to_many(apply_forwarded_result_runner):
    """
    test apply_forwarded_results with results already set,
    where one forwarded output map to many openstack objects.
    should take the first item from matching list and assign it and should not delete it
    """

    mock_forwarded_results = {"val1": ["forward-props1"], "val2": ["forward-props2"]}
    copy_forward_results = copy.deepcopy(mock_forwarded_results)

    expected_updated_call_args = [
        "forward-props1",
        "forward-props1",
        "forward-props2",
        "forward-props2",
    ]
    apply_forwarded_result_runner(
        ["val1", "val1", "val2", "val2"],
        mock_forwarded_results,
        expected_updated_call_args,
    )

    # mock_forwarded_results should not mutate
    assert mock_forwarded_results == copy_forward_results


def test_apply_forwarded_result_not_found(setup_instance_with_results):
    """
    Test apply_forwarded_results when no forwarded results are found for stored result
    should get updated with default values for forwarded values
    """
    mock_forwarded_results = {"val1": [{"prop1": "val1"}]}
    result_obj = mock_result("invalid-val")
    instance = setup_instance_with_results([result_obj])
    instance.DEFAULT_OUT = "Not Found"

    mock_link_prop = NonCallableMock()
    instance.apply_forwarded_results(mock_link_prop, mock_forwarded_results)

    result_obj.get_prop.assert_called_once_with(mock_link_prop)
    result_obj.update_forwarded_properties({"prop1": "Not Found"})
