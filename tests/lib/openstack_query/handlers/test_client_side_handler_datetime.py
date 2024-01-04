from unittest.mock import patch, NonCallableMock, MagicMock, call
import pytest

from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)
from enums.query.query_presets import QueryPresetsDateTime
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with a mocked filter function mappings
    """

    # sets filter function mappings so that PROP_1 is valid for all client_side
    _filter_function_mappings = {
        preset: [MockProperties.PROP_1] for preset in QueryPresetsDateTime
    }
    return ClientSideHandlerDateTime(_filter_function_mappings)


@pytest.fixture(name="run_prop_test_case")
def run_prop_test_case_fixture(instance):
    """
    fixture to run a test cases for each client-side filter function
    """

    @patch("openstack_query.time_utils.TimeUtils.get_timestamp_in_seconds")
    @patch("openstack_query.handlers.client_side_handler_datetime.datetime")
    def _run_prop_test_case(
        preset_to_test, prop_value, to_compare, mock_datetime, mock_get_timestamp
    ):
        """
        runs a test case by calling get_filter_func for datetime handler
        with a given preset, prop return value and value to compare against.
        """

        # we mock and set the timestamp return values manually since it's difficult testing datetime
        mock_datetime.strptime.return_value.timestamp.return_value = prop_value
        mock_get_timestamp.return_value = to_compare

        # mock the kwargs - they won't be used
        days, hours, mins, secs = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        mock_kwargs = {"days": days, "hours": hours, "minutes": mins, "seconds": secs}

        prop_func = MagicMock()
        filter_func = instance.get_filter_func(
            preset_to_test, MockProperties.PROP_1, prop_func, mock_kwargs
        )

        mock_obj = NonCallableMock()
        res = filter_func(mock_obj)

        prop_func.assert_called_once_with(mock_obj)
        mock_datetime.strptime.assert_has_calls(
            [call(prop_func.return_value, "%Y-%m-%dT%H:%M:%SZ"), call().timestamp()]
        )
        mock_get_timestamp.assert_called_once_with(days, hours, mins, secs)

        return res

    return _run_prop_test_case


def test_check_supported_all_presets(instance):
    """
    Tests that client_side_handler_datetime supports all DateTime QueryPresets
    """
    assert all(
        instance.check_supported(preset, MockProperties.PROP_1)
        for preset in QueryPresetsDateTime
    )


def test_prop_older_than(run_prop_test_case):
    """
    Tests prop_older_than client-side-filter with different values
    This essentially compares two numbers (number of seconds) and if the prop value is higher, it returns True
    """
    for i, expected in [(200, True), (400, False), (300, False)]:
        assert run_prop_test_case(QueryPresetsDateTime.OLDER_THAN, 300, i) == expected


def test_prop_younger_than(run_prop_test_case):
    """
    Tests younger_than client-side-filter with different values
    This essentially compares two numbers (number of seconds) and if the prop value is lower, it returns True
    """
    for i, expected in [(200, False), (400, True), (300, False)]:
        assert run_prop_test_case(QueryPresetsDateTime.YOUNGER_THAN, 300, i) == expected


def test_prop_younger_than_or_equal_to(run_prop_test_case):
    """
    Tests prop_younger_than_or_equal_to client-side-filter with different values
    Same as prop_younger_than, but if equal will also return True
    """
    for i, expected in [(200, False), (400, True), (300, True)]:
        assert (
            run_prop_test_case(QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO, 300, i)
            == expected
        )


def test_prop_older_than_or_equal_to(run_prop_test_case):
    """
    Tests prop_older_than_or_equal_to client-side-filter with different values
    Same as prop_older_than, but if equal will also return True
    """
    for i, expected in [(200, True), (400, False), (300, True)]:
        assert (
            run_prop_test_case(QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO, 300, i)
            == expected
        )
