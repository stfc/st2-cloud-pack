from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest
import pytz
from enums.icinga.icinga_objects import IcingaObject
from workflows.icinga_downtime import schedule_downtime, remove_downtime
from structs.icinga.downtime_details import DowntimeDetails


# pylint:disable=too-many-locals
@patch("workflows.icinga_downtime.downtime.schedule_downtime")
@pytest.mark.parametrize(
    "start_time, end_time, expected_start_timestamp, expected_end_timestamp",
    [
        ("01/12/24 12:00:00", "01/12/24 17:00:00", 1733054400, 1733072400),
        ("01/10/24 12:00:00", "01/10/24 17:00:00", 1727780400, 1727798400),
    ],  # 2nd test during BST
)
def test_schedule_fixed_downtime(
    mock_schedule_downtime,
    start_time,
    end_time,
    expected_start_timestamp,
    expected_end_timestamp,
):
    icinga_account = MagicMock()

    object_type = "Host"
    name = "example_host"
    comment = "Scheduled maintenance"
    is_fixed = True

    datetime_object = datetime.strptime(start_time, "%d/%m/%y %H:%M:%S")

    uk_timezone = pytz.timezone("Europe/London")
    local_time = uk_timezone.localize(datetime_object)
    utc_time = local_time.astimezone(pytz.utc)
    unix_timestamp = int(utc_time.timestamp())

    assert unix_timestamp == expected_start_timestamp

    schedule_downtime(
        icinga_account,
        object_type,
        name,
        start_time,
        end_time,
        comment,
        is_fixed,
    )

    expected_downtime_details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name=name,
        start_time=expected_start_timestamp,
        end_time=expected_end_timestamp,
        duration=expected_end_timestamp - expected_start_timestamp,
        comment=comment,
        is_fixed=is_fixed,
    )
    mock_schedule_downtime.assert_called_once_with(
        icinga_account=icinga_account, details=expected_downtime_details
    )


# pylint:disable=too-many-locals
@patch("workflows.icinga_downtime.downtime.schedule_downtime")
@pytest.mark.parametrize(
    "start_time, end_time, expected_start_timestamp, expected_end_timestamp",
    [
        ("01/12/24 12:00:00", "01/12/24 17:00:00", 1733054400, 1733072400),
        ("01/10/24 12:00:00", "01/10/24 17:00:00", 1727780400, 1727798400),
    ],  # 2nd test during BST
)
def test_schedule_flexible_downtime(
    mock_schedule_downtime,
    start_time,
    end_time,
    expected_start_timestamp,
    expected_end_timestamp,
):
    icinga_account = MagicMock()

    object_type = "Host"
    name = "example_host"
    duration = 3600  # 1 hour
    comment = "Scheduled maintenance"
    is_fixed = False

    datetime_object = datetime.strptime(start_time, "%d/%m/%y %H:%M:%S")

    uk_timezone = pytz.timezone("Europe/London")
    local_time = uk_timezone.localize(datetime_object)
    utc_time = local_time.astimezone(pytz.utc)
    unix_timestamp = int(utc_time.timestamp())

    assert unix_timestamp == expected_start_timestamp

    schedule_downtime(
        icinga_account,
        object_type,
        name,
        start_time,
        end_time,
        comment,
        is_fixed,
        duration,
    )

    expected_downtime_details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name=name,
        start_time=expected_start_timestamp,
        end_time=expected_end_timestamp,
        duration=duration,
        comment=comment,
        is_fixed=is_fixed,
    )
    mock_schedule_downtime.assert_called_once_with(
        icinga_account=icinga_account, details=expected_downtime_details
    )


@patch("workflows.icinga_downtime.downtime.remove_downtime")
def test_remove_downtime(mock_remove_downtime):
    icinga_account = MagicMock()

    object_type = "Host"
    name = "example_host"

    remove_downtime(icinga_account, object_type, name)

    mock_remove_downtime.assert_called_once_with(
        icinga_account=icinga_account,
        object_type=IcingaObject.HOST,
        object_name=name,
    )
