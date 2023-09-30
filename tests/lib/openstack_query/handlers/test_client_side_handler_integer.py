import pytest

from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from enums.query.query_presets import QueryPresetsInteger
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


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


def test_check_supported_all_presets(instance):
    """
    Tests that client_side_handler_integer supports all integer QueryPresets
    """
    assert (
        instance.check_supported(preset, MockProperties.PROP_1)
        for preset in QueryPresetsInteger
    )


def test_prop_less_than(instance):
    """
    Tests that method prop_less_than functions expectedly
    Returns True if val1 is less than val2
    """
    for i, expected in (1, True), (2, False):
        assert instance._prop_less_than(i, 2) == expected


def test_prop_greater_than(instance):
    """
    Tests that method prop_greater_than functions expectedly
    Returns True if val1 is greater than val2
    """
    for i, expected in (1, False), (2, False), (3, True):
        assert instance._prop_greater_than(i, 2) == expected


def test_prop_less_than_or_equal_to(instance):
    """
    Tests that method prop_less_than_or_equal_to functions expectedly
    Returns True if val1 is less than or equal to val2
    """
    for i, expected in (1, True), (2, True), (3, False):
        assert instance._prop_less_than_or_equal_to(i, 2) == expected


def test_prop_greater_than_or_equal_to(instance):
    """
    Tests that method prop_greater_than_or_equal_to functions expectedly
    Returns True if val1 is greater than or equal to val2
    """
    for i, expected in (1, False), (2, True), (3, True):
        assert instance._prop_greater_than_or_equal_to(i, 2) == expected
