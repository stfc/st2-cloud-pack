from datetime import datetime, timedelta
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class TimeUtils:
    @staticmethod
    def get_current_time() -> datetime:
        return datetime.now()

    @staticmethod
    def get_timestamp_in_seconds(
        days: int = 0, hours: int = 0, minutes: int = 0, seconds: float = 0
    ) -> float:
        """
        Function which takes a number of days, hours, minutes, and seconds - and calculates the total seconds
        :param days: (Optional) number of days
        :param hours: (Optional) number of hours
        :param minutes: (Optional) number of minutes
        :param seconds: (Optional) number of seconds
        """
        if all(arg == 0 for arg in [days, hours, minutes, seconds]):
            raise MissingMandatoryParamError(
                "requires at least 1 argument for function to be non-zero"
            )

        current_time = TimeUtils.get_current_time().timestamp()
        prop_time_in_seconds = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        ).total_seconds()

        return current_time - prop_time_in_seconds

    @staticmethod
    def convert_to_timestamp(
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
    ) -> str:
        """
        Helper function to convert a relative time from current time into a timestamp
        :param days: (Optional) relative number of days since current time
        :param hours: (Optional) relative number of hours since current time
        :param minutes: (Optional) relative number of minutes since current time
        :param seconds: (Optional) relative number of seconds since current time
        """

        time_in_seconds = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        ).total_seconds()
        return datetime.fromtimestamp(
            TimeUtils.get_current_time().timestamp() - time_in_seconds
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
