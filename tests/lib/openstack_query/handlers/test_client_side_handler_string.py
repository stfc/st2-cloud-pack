from unittest.mock import patch, NonCallableMock

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
    "regex_string, test_prop",
    [
        # "Numeric digits only",
        ("[0-9]+", "123"),
        # "Alphabetic characters only",
        ("[A-Za-z]+", "abc"),
        # "No alphabetic characters",
        ("[A-Za-z]+", "123"),
        # "Alphabetic and numeric characters",
        ("[A-Za-z0-9]+", "abc123"),
        # "Empty string, no match",
        ("[A-Za-z]+", ""),
    ],
)
@patch("re.match")
@patch("re.compile")
def test_prop_matches_regex_valid(
    mock_regex_compile, mock_regex_match, regex_string, test_prop, instance
):
    """
    Tests that method prop_matches_regex functions expectedly - with valid regex patterns
    Returns True if test_prop matches given regex pattern regex_string
    """
    mock_compile = NonCallableMock()
    mock_regex_match.return_value = test_prop
    mock_regex_compile.return_value = mock_compile
    instance._prop_matches_regex(test_prop, regex_string)
    mock_regex_match.assert_called_once_with(mock_compile, test_prop)
    mock_regex_compile.assert_called_once_with(regex_string)
