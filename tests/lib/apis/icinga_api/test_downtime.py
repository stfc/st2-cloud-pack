import json
from unittest.mock import MagicMock, patch

import pytest
from requests import HTTPError
from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError

from apis.icinga_api.enums.icinga_objects import IcingaObject
from apis.icinga_api.downtime import remove_downtime, schedule_downtime
from apis.icinga_api.structs.downtime_details import DowntimeDetails


@patch("apis.icinga_api.downtime.requests.post")
def test_schedule_host_fixed_downtime_success(mock_post):
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="example_host",
        start_time=1725955200,
        end_time=1725958800,
        comment="Scheduled maintenance",
        is_fixed=True,
        duration=3600,
    )
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response

    schedule_downtime(icinga_account, details)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

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
        "all_services": True,
    }

    assert payload == expected_payload


@patch("apis.icinga_api.downtime.requests.post")
def test_schedule_service_fixed_downtime_success(mock_post):
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.SERVICE,
        object_name="example_service",
        start_time=1725955200,
        end_time=1725958800,
        comment="Scheduled maintenance",
        is_fixed=True,
        duration=3600,
    )
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response

    schedule_downtime(icinga_account, details)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

    _, kwargs = mock_post.call_args
    payload = json.loads(kwargs["data"])

    expected_payload = {
        "type": "Service",
        "filter": 'service.name=="example_service"',
        "author": "StackStorm",
        "comment": "Scheduled maintenance",
        "start_time": 1725955200,
        "end_time": 1725958800,
        "fixed": True,
        "duration": None,
        "all_services": False,
    }

    assert payload == expected_payload


@patch("apis.icinga_api.downtime.requests.post")
def test_schedule_downtime_request_fail(mock_post):
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="missing_host",
        start_time=1725955200,
        end_time=1725958800,
        comment="Scheduled maintenance",
        is_fixed=True,
        duration=3600,
    )
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError("Not Found")
    mock_post.return_value = mock_response

    with pytest.raises(HTTPError):
        schedule_downtime(icinga_account, details)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("apis.icinga_api.downtime.requests.post")
def test_schedule_flexible_downtime_success(mock_post):
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="example_host",
        start_time=1725955200,
        end_time=1725958800,
        duration=3600,
        comment="Scheduled maintenance",
        is_fixed=False,
    )
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response

    schedule_downtime(icinga_account, details)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

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
        "all_services": True,
    }

    assert payload == expected_payload


def test_missing_schedule_downtime_object_name():
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="",
        start_time=1725955200,
        end_time=1725958800,
        duration=3600,
        comment="Scheduled maintenance",
        is_fixed=True,
    )

    with pytest.raises(MissingMandatoryParamError):
        schedule_downtime(icinga_account, details)


def test_missing_schedule_downtime_start_time():
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="example_host",
        start_time=None,
        end_time=1725958800,
        duration=3600,
        comment="Scheduled maintenance",
        is_fixed=True,
    )

    with pytest.raises(MissingMandatoryParamError):
        schedule_downtime(icinga_account, details)


def test_missing_schedule_downtime_end_time():
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="example_host",
        start_time=1725958800,
        end_time=None,
        duration=3600,
        comment="Scheduled maintenance",
        is_fixed=True,
    )

    with pytest.raises(MissingMandatoryParamError):
        schedule_downtime(icinga_account, details)


def test_missing_schedule_downtime_comment():
    icinga_account = MagicMock()
    details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name="example_host",
        start_time=1725955200,
        end_time=1725958800,
        duration=3600,
        comment="",
        is_fixed=True,
    )

    with pytest.raises(MissingMandatoryParamError):
        schedule_downtime(icinga_account, details)


@patch("apis.icinga_api.downtime.requests.post")
def test_remove_downtime_success(mock_post):
    icinga_account = MagicMock()

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response

    remove_downtime(
        icinga_account,
        object_type=IcingaObject.HOST,
        object_name="example_host",
    )

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

    _, kwargs = mock_post.call_args
    payload = json.loads(kwargs["data"])

    expected_payload = {
        "type": "Host",
        "filter": 'host.name=="example_host"',
        "author": "StackStorm",
    }

    assert payload == expected_payload


@patch("apis.icinga_api.downtime.requests.post")
def test_remove_downtime_request_fail(mock_post):
    icinga_account = MagicMock()

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError("Not Found")
    mock_post.return_value = mock_response

    with pytest.raises(HTTPError):
        remove_downtime(
            icinga_account,
            object_type=IcingaObject.HOST,
            object_name="missing_host",
        )

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


def test_missing_remove_downtime_object_name():
    icinga_account = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        remove_downtime(
            icinga_account,
            object_type=IcingaObject.HOST,
            object_name="",
        )
