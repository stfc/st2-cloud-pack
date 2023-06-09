from datetime import timedelta, datetime

from enums.query.query_presets import QueryPresets, QueryPresetsDateTime
from openstack_query.preset_handlers.preset_handler_base import PresetHandlerBase

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class PresetHandlerDateTime(PresetHandlerBase):
    def __init__(self):
        super().__init__()

        self._FILTER_FUNCTIONS = {
            QueryPresetsDateTime.OLDER_THAN: self._prop_older_than,
            QueryPresetsDateTime.YOUNGER_THAN: self._prop_younger_than,
            QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: self._prop_older_than_or_equal_to,
            QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: self._prop_younger_than_or_equal_to,
        }

    @staticmethod
    def _get_current_time():
        return datetime.now()

    def _get_timestamp_in_seconds(
        self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: float = 0
    ):
        if all(arg == 0 for arg in [days, hours, minutes, seconds]):
            raise MissingMandatoryParamError(
                "requires at least 1 argument for function to be non-zero"
            )

        current_time = self._get_current_time().timestamp()
        prop_time_in_seconds = timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        ).total_seconds()

        return current_time - prop_time_in_seconds

    def _prop_older_than(
        self,
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        prop_timestamp = datetime.strptime(prop, prop_timestamp_fmt).timestamp()
        given_timestamp = self._get_timestamp_in_seconds(days, hours, minutes, seconds)

        return prop_timestamp > given_timestamp

    def _prop_younger_than_or_equal_to(
        self,
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        return not self._prop_older_than(
            prop, days, hours, minutes, seconds, prop_timestamp_fmt
        )

    def _prop_younger_than(
        self,
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        prop_datetime = datetime.strptime(prop, prop_timestamp_fmt).timestamp()
        return prop_datetime < self._get_timestamp_in_seconds(
            days, hours, minutes, seconds
        )

    def _prop_older_than_or_equal_to(
        self,
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        return not self._prop_younger_than(
            prop, days, hours, minutes, seconds, prop_timestamp_fmt
        )
