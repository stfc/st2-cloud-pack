import pytest

from enums.query.query_presets import QueryPresetsString
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


# pylint:disable=protected-access


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Prepares an instance to be used in tests
    """
    _filter_function_mappings = {
        preset: [MockProperties.PROP_1] for preset in QueryPresetsString
    }
    return ClientSideHandlerString(_filter_function_mappings)


def test_check_supported_all_presets(instance):
    """
    Tests that client_side_handler_string supports all string QueryPresets
    """
    assert (
        instance.check_supported(preset, MockProperties.PROP_1)
        for preset in QueryPresetsString
    )


@pytest.mark.parametrize(
    "regex_string, test_prop, expected",
    [
        # "Numeric digits only",
        ("[0-9]+", "123", True),
        # "Alphabetic characters only",
        ("[A-Za-z]+", "abc", True),
        # "No alphabetic characters",
        ("[A-Za-z]+", "123", False),
        # "Alphabetic and numeric characters",
        ("[A-Za-z0-9]+", "abc123", True),
        # "Empty string, no match",
        ("[0-9]+", "", False),
    ],
)
def test_prop_matches_regex(regex_string, test_prop, expected, instance):
    """
    Tests that method prop_matches_regex functions expectedly - with valid regex patterns
    Returns True if test_prop matches given regex pattern regex_string
    """
    assert instance._prop_matches_regex(test_prop, regex_string) == expected
