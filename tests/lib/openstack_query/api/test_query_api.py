from unittest.mock import MagicMock, NonCallableMock
import pytest

from openstack_query.api.query_api import QueryAPI

from exceptions.parse_query_error import ParseQueryError
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance to run tests with
    """
    return QueryAPI(query_components=MagicMock())


@pytest.fixture(name="run_with_test_case")
def run_with_test_case_fixture(instance):
    """
    Fixture for running run() with various test arguments
    """

    def _run_with_test_case(data_subset, mock_kwargs):
        """
        Runs a test case for the run() method
        """
        mock_query_results = ("object-list", "property-list")
        instance.executer.run_query.return_value = mock_query_results

        if not mock_kwargs:
            mock_kwargs = {}

        res = instance.run("test-account", data_subset, **mock_kwargs)
        instance.executer.run_query.assert_called_once_with(
            cloud_account="test-account", from_subset=data_subset, **mock_kwargs
        )

        # test that data is marshalled correctly to executer
        assert (
            instance.executer.client_side_filters
            == instance.builder.client_side_filters
        )
        assert (
            instance.executer.server_side_filters
            == instance.builder.server_side_filters
        )
        assert instance.executer.parse_func == instance.parser.run_parser
        assert instance.executer.output_func == instance.output.generate_output
        assert res == instance

    return _run_with_test_case


def test_select_invalid(instance):
    """
    Tests select method works expectedly - with no inputs
    method raises ParseQueryError when given no properties
    """
    with pytest.raises(ParseQueryError):
        instance.select()


def test_select_with_one_prop(instance):
    """
    Tests select method works expectedly - with one prop
    method should forward prop to parse_select in QueryOutput object
    """
    mock_query_output = MagicMock()
    instance.output = mock_query_output

    res = instance.select(MockProperties.PROP_1)
    mock_query_output.parse_select.assert_called_once_with(
        MockProperties.PROP_1, select_all=False
    )
    assert res == instance


def test_select_with_many_props(instance):
    """
    Tests select method works expectedly - with multiple prop
    method should forward props to parse_select in QueryOutput object
    """
    mock_query_output = MagicMock()
    instance.output = mock_query_output

    res = instance.select(MockProperties.PROP_1, MockProperties.PROP_2)
    mock_query_output.parse_select.assert_called_once_with(
        MockProperties.PROP_1, MockProperties.PROP_2, select_all=False
    )
    assert res == instance


def test_select_all(instance):
    """
    Tests select all method works expectedly
    method should call parse_select in QueryOutput object
    """
    mock_query_output = MagicMock()
    instance.output = mock_query_output
    res = instance.select_all()
    mock_query_output.parse_select.assert_called_once_with(select_all=True)
    assert res == instance


def test_where_no_kwargs(instance):
    """
    Tests that where method works expectedly
    method should forward to parse_where in QueryBuilder object - with no kwargs given
    """
    mock_query_builder = MagicMock()
    instance.builder = mock_query_builder

    res = instance.where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
    mock_query_builder.parse_where.assert_called_once_with(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1, {}
    )
    assert res == instance


def test_where_with_kwargs(instance):
    """
    Tests that where method works expectedly
    method should forward to parse_where in QueryBuilder object - with kwargs given
    """
    mock_query_builder = MagicMock()
    instance.builder = mock_query_builder
    res = instance.where(
        MockQueryPresets.ITEM_2, MockProperties.PROP_2, arg1="val1", arg2="val2"
    )
    mock_query_builder.parse_where.assert_called_once_with(
        MockQueryPresets.ITEM_2,
        MockProperties.PROP_2,
        {"arg1": "val1", "arg2": "val2"},
    )
    assert res == instance


def test_run_with_optional_params(run_with_test_case):
    """
    Tests that run method works expectedly - with subset meta_params kwargs
    method should get client_side and server_side filters and forward them to query runner object

    """
    run_with_test_case(data_subset=["obj1", "obj2", "obj3"], mock_kwargs=None)


def test_run_with_kwargs(run_with_test_case):
    """
    Tests that run method works expectedly - with subset kwargs
    method should get client_side and server_side filters and forward them to query runner object

    """
    run_with_test_case(data_subset=None, mock_kwargs={"arg1": "val1", "arg2": "val2"})


def test_run_with_nothing(run_with_test_case):
    """
    Tests that run method works expectedly - with subset kwargs
    method should get client_side and server_side filters and forward them to query runner object

    """
    run_with_test_case(None, None)


def test_run_with_kwargs_and_subset(run_with_test_case):
    """
    Tests that run method works expectedly - with subset kwargs
    method should get client_side and server_side filters and forward them to query runner object

    """
    run_with_test_case(
        data_subset=["obj1", "obj2", "obj3"],
        mock_kwargs={"arg1": "val1", "arg2": "val2"},
    )


def test_to_list_as_objects_false(instance):
    """
    Tests that to_list method functions expectedly
    method should return _query_results attribute when as_objects is false
    """
    # pylint: disable=protected-access
    mock_query_results = NonCallableMock()
    instance._query_results = mock_query_results
    assert instance.to_list() == mock_query_results


def test_to_list_as_objects_true(instance):
    """
    Tests that to_list method functions expectedly
    method should return _query_results_as_objects attribute when as_objects is true
    """
    # pylint: disable=protected-access
    mock_query_results_as_obj = NonCallableMock()
    instance._query_results_as_objects = mock_query_results_as_obj
    assert instance.to_list(as_objects=True) == mock_query_results_as_obj


def test_to_string(instance):
    """
    Tests that to_string method functions expectedly
    method should call QueryOutput object to_string() and return results
    """
    mock_query_output = MagicMock()
    instance.output = mock_query_output
    instance.output.to_string.return_value = "string-out"
    assert instance.to_string() == "string-out"


def test_to_html(instance):
    """
    Tests that to_html method functions expectedly
    method should call QueryOutput object to_html() and return results
    """
    mock_query_output = MagicMock()
    instance.output = mock_query_output
    instance.output.to_html.return_value = "html-out"
    assert instance.to_html() == "html-out"


def test_sort_by(instance):
    """
    Tests that sort_by method functions expectedly
    method should call QueryParser object parse_sort_by() and return results
    """
    mock_sort_by = [("some-prop-enum", False), ("some-prop-enum-2", True)]
    instance.sort_by(*mock_sort_by)
    instance.parser.parse_sort_by.assert_called_once_with(*mock_sort_by)


def test_group_by(instance):
    """
    Tests that group_by method functions expectedly
    method should call QueryParser object parse_group_by() and return results
    """
    mock_group_by = "some-prop-enum"
    mock_group_ranges = {"group1": ["val1", "val2"], "group2": ["val3"]}
    mock_include_ungrouped_results = False
    instance.parser.group_by = None

    instance.group_by(mock_group_by, mock_group_ranges, mock_include_ungrouped_results)
    instance.parser.parse_group_by.assert_called_once_with(
        mock_group_by, mock_group_ranges, mock_include_ungrouped_results
    )


def test_group_by_already_set(instance):
    """
    Tests that group_by method functions expectedly
    Should raise error when attempting to set group by when already set
    """
    instance.parser.group_by_prop = "prop1"
    with pytest.raises(ParseQueryError):
        instance.group_by("prop2")
