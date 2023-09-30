from unittest.mock import patch, NonCallableMock
import pytest

from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)
from enums.query.query_presets import QueryPresetsDateTime
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


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
def run_prop_test_case_fixture():
    """
    Fixture which runs a test case for a given client_side_handler function and
    a set of test arguments
    """

    prop_str = NonCallableMock()
    days, hours, mins, secs = (
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
    )

    def _run_prop_test_case(filter_method, mock_prop_timestamp, mock_given_timestamp):
        """
        Runs the test case with mocks to ensure the prop time handling works as expected
        Does not assert the final result, that is for the test case to do
        """

        with patch(
            "openstack_query.time_utils.TimeUtils.get_timestamp_in_seconds"
        ) as mock_time_get_timestamp:
            with patch(
                "openstack_query.handlers.client_side_handler_datetime.datetime"
            ) as mock_datetime:
                mock_datetime.strptime.return_value.timestamp.return_value = (
                    mock_prop_timestamp  # Prop timestamp
                )
                mock_time_get_timestamp.return_value = (
                    mock_given_timestamp  # The user's selected timeframe
                )
                result = filter_method(prop_str, days, hours, mins, secs)

        mock_datetime.strptime.return_value.timestamp.assert_called_once_with()
        mock_time_get_timestamp.assert_called_once_with(days, hours, mins, secs)
        return result

    return _run_prop_test_case


def test_prop_older_than_with_actual_older(instance, run_prop_test_case):
    """
    Tests that function prop_older_than functions expectedly
    Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
    """
    assert run_prop_test_case(instance._prop_older_than, 300, 200)


def test_prop_older_than_with_actual_younger(instance, run_prop_test_case):
    """
    Tests that function prop_older_than functions expectedly
    Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
    """
    assert not run_prop_test_case(instance._prop_older_than, 100, 200)


def test_prop_younger_than(instance, run_prop_test_case):
    """
    Tests that function prop_older_than functions expectedly
    Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
    """
    assert run_prop_test_case(instance._prop_younger_than, 100, 200)


def test_prop_younger_than_with_actual_older(instance, run_prop_test_case):
    """
    Tests that function prop_older_than functions expectedly
    Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
    """
    assert not run_prop_test_case(instance._prop_younger_than, 300, 200)


def test_prop_younger_than_or_equal_to(instance):
    """
    Tests that function prop_younger_than_or_equal_to functions expectedly by inverting older than
    """
    prop, days, hours, mins, secs = (
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
    )
    with patch.object(instance, "_prop_older_than") as mock_prop_older_than:
        mock_prop_older_than.return_value = False

        assert instance._prop_younger_than_or_equal_to(prop, days, hours, mins, secs)
        mock_prop_older_than.assert_called_once_with(prop, days, hours, mins, secs)


def test_prop_older_than_or_equal_to(instance):
    """
    Tests that function prop_older_than_or_equal_to functions expectedly by
    inverting the younger than function
    """
    prop, days, hours, mins, secs = (
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
        NonCallableMock(),
    )
    with patch.object(instance, "_prop_younger_than") as mock_prop_younger_than:
        mock_prop_younger_than.return_value = False

        assert instance._prop_older_than_or_equal_to(prop, days, hours, mins, secs)
        mock_prop_younger_than.assert_called_once_with(prop, days, hours, mins, secs)
