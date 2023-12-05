from unittest.mock import NonCallableMock, MagicMock
import pytest

from exceptions.query_preset_mapping_error import QueryPresetMappingError
from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from enums.query.query_presets import QueryPresetsGeneric
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with a mocked filter function mappings
    """

    # sets filter function mappings so that PROP_1 is valid for all client_side
    _filter_function_mappings = {
        preset: [MockProperties.PROP_1] for preset in QueryPresetsGeneric
    }
    return ClientSideHandlerGeneric(_filter_function_mappings)


@pytest.fixture(name="run_prop_test_case")
def run_prop_test_case_fixture(instance):
    """
    fixture to run a test cases for each client-side filter function
    """

    def _run_prop_test_case(preset_to_test, prop_value, mock_kwargs):
        """
        runs a test case by calling get_filter_func for generic handler
        with a given preset, prop return value and value to compare against.
        """

        prop_func = MagicMock()
        prop_func.return_value = prop_value

        filter_func = instance.get_filter_func(
            preset_to_test, MockProperties.PROP_1, prop_func, mock_kwargs
        )

        mock_obj = NonCallableMock()
        res = filter_func(mock_obj)
        prop_func.assert_called_once_with(mock_obj)
        return res

    return _run_prop_test_case


@pytest.fixture(name="test_corpus")
def corpus_fixture():
    """
    Returns a set of arguments to test against
    """
    return [1, "foo", None, {"a": "b"}]


def test_check_supported_all_presets(instance):
    """
    Tests that client_side_handler_generic supports all generic QueryPresets
    """
    assert (
        instance.check_supported(preset, MockProperties.PROP_1)
        for preset in QueryPresetsGeneric
    )


def test_prop_equal_to(run_prop_test_case, test_corpus):
    """
    Tests that method prop_equal_to functions expectedly
    """
    for i in test_corpus:
        assert run_prop_test_case(QueryPresetsGeneric.EQUAL_TO, i, {"value": i})
        assert not run_prop_test_case(
            QueryPresetsGeneric.EQUAL_TO, i, {"value": "not_equal"}
        )


def test_prop_not_equal_to(run_prop_test_case, test_corpus):
    """
    Tests that method not_prop_equal_to functions expectedly
    """
    for i in test_corpus:
        assert run_prop_test_case(
            QueryPresetsGeneric.NOT_EQUAL_TO, i, {"value": "not_equal"}
        )
        assert not run_prop_test_case(QueryPresetsGeneric.NOT_EQUAL_TO, i, {"value": i})


def test_prop_any_in(run_prop_test_case):
    """
    Tests that method prop_any_in functions expectedly
    """
    assert run_prop_test_case(
        QueryPresetsGeneric.ANY_IN, "val3", {"values": ["val1", "val2", "val3"]}
    )
    assert not run_prop_test_case(
        QueryPresetsGeneric.ANY_IN, "val4", {"values": ["val1", "val2", "val3"]}
    )


def test_prop_any_in_empty_list(run_prop_test_case):
    """
    Tests that method prop_any_in when given empty list raise error
    """
    with pytest.raises(QueryPresetMappingError):
        run_prop_test_case(QueryPresetsGeneric.ANY_IN, "val3", {"values": []})


def test_prop_not_any_in(run_prop_test_case):
    """
    Tests that method prop_any_not_in functions expectedly
    """
    assert run_prop_test_case(
        QueryPresetsGeneric.NOT_ANY_IN, "val4", {"values": ["val1", "val2", "val3"]}
    )
    assert not run_prop_test_case(
        QueryPresetsGeneric.NOT_ANY_IN, "val3", {"values": ["val1", "val2", "val3"]}
    )


def test_prop_not_any_in_empty_list(run_prop_test_case):
    """
    Tests that method prop_any_not_in when given empty list raise error
    """
    with pytest.raises(QueryPresetMappingError):
        run_prop_test_case(QueryPresetsGeneric.NOT_ANY_IN, "val3", {"values": []})
