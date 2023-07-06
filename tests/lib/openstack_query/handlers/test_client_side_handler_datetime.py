import unittest
from datetime import datetime
from unittest.mock import patch
from parameterized import parameterized

from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)

from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from enums.query.query_presets import QueryPresetsDateTime


@patch(
    "openstack_query.time_utils.TimeUtils.get_current_time",
    return_value=datetime(2023, 6, 4, 10, 30, 0),
)
class ClientSideHandlerDateTimeTests(unittest.TestCase):
    """
    Run various tests to ensure that ClientSideHandlerDateTime class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        # sets filter function mappings so that PROP_1 is valid for all client_side
        _FILTER_FUNCTION_MAPPINGS = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsDateTime
        }
        self.instance = ClientSideHandlerDateTime(_FILTER_FUNCTION_MAPPINGS)

        self.test_cases = {
            "older_by_1_day": {
                "prop": "2023-06-04T10:30:00Z",
                "days": 1,
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
            },
            "older_by_12_hours": {
                "prop": "2023-06-04T10:30:00Z",
                "days": 0,
                "hours": 12,
                "minutes": 0,
                "seconds": 0,
            },
            "older_by_0.5_seconds": {
                "prop": "2023-06-04T10:30:00Z",
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "seconds": 0.5,
            },
            "equal": {
                "prop": "2023-06-04T10:00:00Z",
                "days": 0,
                "hours": 0,
                "minutes": 30,
                "seconds": 0,
            },
            "younger_by_1_day": {
                "prop": "2023-06-02T10:30:00Z",
                "days": 1,
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
            },
            "younger_by_12_hours": {
                "prop": "2023-06-03T10:30:00Z",
                "days": 0,
                "hours": 12,
                "minutes": 0,
                "seconds": 0,
            },
            "younger_by_0.5_seconds": {
                "prop": "2023-06-03T10:29:59Z",
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "seconds": 0.5,
            },
        }

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsDateTime]
    )
    def test_check_supported_all_presets(self, mock_current_time, name, preset):
        """
        Tests that handler supports all generic query client_side
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            ("older_by_1_day", True),
            ("older_by_12_hours", True),
            ("older_by_0.5_seconds", True),
            ("equal", False),
            ("younger_by_1_day", False),
            ("younger_by_12_hours", False),
            ("younger_by_0.5_seconds", False),
        ]
    )
    def test_prop_older_than(self, mock_current_time, name, expected_out):
        kwargs = self.test_cases[name]
        out = self.instance._prop_older_than(**kwargs)
        assert out == expected_out

    @parameterized.expand(
        [
            ("older_by_1_day", True),
            ("older_by_12_hours", True),
            ("older_by_0.5_seconds", True),
            ("equal", True),
            ("younger_by_1_day", False),
            ("younger_by_12_hours", False),
            ("younger_by_0.5_seconds", False),
        ]
    )
    def test_prop_older_than_or_equal_to(self, mock_current_time, name, expected_out):
        kwargs = self.test_cases[name]
        out = self.instance._prop_older_than_or_equal_to(**kwargs)
        assert out == expected_out

    @parameterized.expand(
        [
            ("older_by_1_day", False),
            ("older_by_12_hours", False),
            ("older_by_0.5_seconds", False),
            ("equal", False),
            ("younger_by_1_day", True),
            ("younger_by_12_hours", True),
            ("younger_by_0.5_seconds", True),
        ]
    )
    def test_prop_younger_than(self, mock_current_time, name, expected_out):
        kwargs = self.test_cases[name]
        out = self.instance._prop_younger_than(**kwargs)
        assert out == expected_out

    @parameterized.expand(
        [
            ("older_by_1_day", False),
            ("older_by_12_hours", False),
            ("older_by_0.5_seconds", False),
            ("equal", True),
            ("younger_by_1_day", True),
            ("younger_by_12_hours", True),
            ("younger_by_0.5_seconds", True),
        ]
    )
    def test_prop_younger_than_or_equal_to(self, mock_current_time, name, expected_out):
        kwargs = self.test_cases[name]
        out = self.instance._prop_younger_than_or_equal_to(**kwargs)
        assert out == expected_out
