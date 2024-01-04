from unittest.mock import NonCallableMock, MagicMock
import pytest

from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from enums.query.query_presets import QueryPresetsInteger
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with a mocked filter function mappings
    """

    # sets filter function mappings so that PROP_1 is valid for all client_side
    _filter_function_mappings = {
        preset: [MockProperties.PROP_1] for preset in QueryPresetsInteger
    }
    return ClientSideHandlerInteger(_filter_function_mappings)


@pytest.fixture(name="run_prop_test_case")
def run_prop_test_case_fixture(instance):
    """
    fixture to run a test cases for each client-side filter function
    """

    def _run_prop_test_case(preset_to_test, prop_value, filter_value):
        """
        runs a test case by calling get_filter_func for generic handler
        with a given preset, prop return value and value to compare against.
        """
        mock_kwargs = {"value": filter_value}
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


def test_check_supported_all_presets(instance):
    """
    Tests that client_side_handler_integer supports all integer QueryPresets
    """
    assert (
        instance.check_supported(preset, MockProperties.PROP_1)
        for preset in QueryPresetsInteger
    )


def test_prop_less_than(run_prop_test_case):
    """
    Tests that method prop_less_than functions expectedly
    Returns True if val1 is less than val2
    """
    for i, expected in (1, True), (2, False):
        assert run_prop_test_case(QueryPresetsInteger.LESS_THAN, i, 2) == expected


def test_prop_greater_than(run_prop_test_case):
    """
    Tests that method prop_greater_than functions expectedly
    Returns True if val1 is greater than val2
    """
    for i, expected in (1, False), (2, False), (3, True):
        assert run_prop_test_case(QueryPresetsInteger.GREATER_THAN, i, 2) == expected


def test_prop_less_than_or_equal_to(run_prop_test_case):
    """
    Tests that method prop_less_than_or_equal_to functions expectedly
    Returns True if val1 is less than or equal to val2
    """
    for i, expected in (1, True), (2, True), (3, False):
        assert (
            run_prop_test_case(QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO, i, 2)
            == expected
        )


def test_prop_greater_than_or_equal_to(run_prop_test_case):
    """
    Tests that method prop_greater_than_or_equal_to functions expectedly
    Returns True if val1 is greater than or equal to val2
    """
    for i, expected in (1, False), (2, True), (3, True):
        assert (
            run_prop_test_case(QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO, i, 2)
            == expected
        )
