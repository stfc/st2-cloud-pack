import json
from unittest.mock import MagicMock, patch

import pytest

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from icinga_api.downtime import remove_downtime, schedule_downtime
from structs.icinga.downtime_details import DowntimeDetails


class TestScheduleDowntime:
    @patch("icinga_api.downtime.requests.post")
    def test_schedule_fixed_downtime_success(self, mock_post):
        icinga_account = MagicMock()
        details = DowntimeDetails(
            object_type="Host",
            object_name="example_host",
            start_time=1725955200,
            duration=3600,
            comment="Scheduled maintenance",
            is_fixed=True,
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        status_code = schedule_downtime(icinga_account, details)

        assert status_code == 200
        mock_post.assert_called_once()

        _, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        expected_payload = {
            "type": "Host",
            "filter": 'host.name=="example_host"',
            "author": "StackStorm",
            "comment": "Scheduled maintenance",
            "start_time": 1725955200,
            "end_time": 1725958800,
            "fixed": True,
            "duration": None,
        }

        assert payload == expected_payload

    @patch("icinga_api.downtime.requests.post")
    def test_schedule_flexible_downtime_success(self, mock_post):
        icinga_account = MagicMock()
        details = DowntimeDetails(
            object_type="Host",
            object_name="example_host",
            start_time=1725955200,
            duration=3600,
            comment="Scheduled maintenance",
            is_fixed=False,
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        status_code = schedule_downtime(icinga_account, details)

        assert status_code == 200
        mock_post.assert_called_once()

        _, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        expected_payload = {
            "type": "Host",
            "filter": 'host.name=="example_host"',
            "author": "StackStorm",
            "comment": "Scheduled maintenance",
            "start_time": 1725955200,
            "end_time": 1725958800,
            "fixed": False,
            "duration": 3600,
        }

        assert payload == expected_payload

    def test_missing_schedule_downtime_object_name(self):
        icinga_account = MagicMock()
        details = DowntimeDetails(
            object_type="Host",
            object_name="",
            start_time=1725955200,
            duration=3600,
            comment="Scheduled maintenance",
            is_fixed=True,
        )

        with pytest.raises(MissingMandatoryParamError):
            schedule_downtime(icinga_account, details)

    def test_missing_schedule_downtime_start_time(self):
        icinga_account = MagicMock()
        details = DowntimeDetails(
            object_type="Host",
            object_name="example_host",
            start_time=None,
            duration=3600,
            comment="Scheduled maintenance",
            is_fixed=True,
        )

        with pytest.raises(MissingMandatoryParamError):
            schedule_downtime(icinga_account, details)

    def test_missing_schedule_downtime_duration(self):
        icinga_account = MagicMock()
        details = DowntimeDetails(
            object_type="Host",
            object_name="example_host",
            start_time=1725955200,
            duration=None,
            comment="Scheduled maintenance",
            is_fixed=True,
        )

        with pytest.raises(MissingMandatoryParamError):
            schedule_downtime(icinga_account, details)

    def test_missing_schedule_downtime_comment(self):
        icinga_account = MagicMock()
        details = DowntimeDetails(
            object_type="Host",
            object_name="example_host",
            start_time=1725955200,
            duration=3600,
            comment="",
            is_fixed=True,
        )

        with pytest.raises(MissingMandatoryParamError):
            schedule_downtime(icinga_account, details)


class TestRemoveDowntime:
    @patch("icinga_api.downtime.requests.post")
    def test_remove_downtime_success(self, mock_post):
        icinga_account = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        status_code = remove_downtime(
            icinga_account,
            object_type="Host",
            object_name="example_host",
        )

        assert status_code == 200
        mock_post.assert_called_once()

        _, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        expected_payload = {
            "type": "Host",
            "filter": 'host.name=="example_host"',
            "author": "StackStorm",
        }

        assert payload == expected_payload

    def test_missing_remove_downtime_object_name(self):
        icinga_account = MagicMock()
        with pytest.raises(MissingMandatoryParamError):
            remove_downtime(
                icinga_account,
                object_type="Host",
                object_name="",
            )