from unittest.mock import NonCallableMock, MagicMock
import pytest

from enums.query.query_presets import QueryPresetsString
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Prepares an instance to be used in tests
    """
    _filter_function_mappings = {
        preset: [MockProperties.PROP_1] for preset in QueryPresetsString
    }
    return ClientSideHandlerString(_filter_function_mappings)


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
def test_prop_matches_regex(regex_string, test_prop, expected, run_prop_test_case):
    """
    Tests that method prop_matches_regex functions expectedly - with valid regex patterns
    Returns True if test_prop matches given regex pattern regex_string
    """
    assert (
        run_prop_test_case(QueryPresetsString.MATCHES_REGEX, test_prop, regex_string)
        == expected
    )
