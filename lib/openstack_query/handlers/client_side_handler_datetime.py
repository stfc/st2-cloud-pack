from datetime import datetime

from enums.query.query_presets import QueryPresetsDateTime

from custom_types.openstack_query.aliases import PresetToValidPropsMap

from openstack_query.utils import get_timestamp_in_seconds
from openstack_query.handlers.client_side_handler import ClientSideHandler


class ClientSideHandlerDateTime(ClientSideHandler):
    """
    Client Side handler for Date Time related queries.
    This class stores a dictionary which maps a Date Time preset/prop pairs to a filter function
    Filter functions which map to QueryPresetsDateTime are defined here
    """

    def __init__(self, filter_function_mappings: PresetToValidPropsMap):
        super().__init__(filter_function_mappings)

        self._FILTER_FUNCTIONS = {
            QueryPresetsDateTime.OLDER_THAN: self._prop_older_than,
            QueryPresetsDateTime.YOUNGER_THAN: self._prop_younger_than,
            QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: self._prop_older_than_or_equal_to,
            QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: self._prop_younger_than_or_equal_to,
        }

    def _prop_older_than(
        self,
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        """
        Filter function which returns True if property older than a relative amount of time since current time.

        :param prop: prop value to check against
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against
        :param prop_timestamp_fmt: (Optional) timestamp format of prop value (default: yyyy-MM-ddTHH:mm:ssZ)

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        prop_timestamp = datetime.strptime(prop, prop_timestamp_fmt).timestamp()
        given_timestamp = get_timestamp_in_seconds(days, hours, minutes, seconds)

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
        """
        Filter function which returns True if property younger than or equal to a relative amount of time since current time
        :param prop: prop value to check against
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against
        :param prop_timestamp_fmt: (Optional) timestamp format of prop value (default: yyyy-MM-ddTHH:mm:ssZ)

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
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
        """
        Filter function which returns True if property younger than a relative amount of time since current time
        :param prop: prop value to check against
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against
        :param prop_timestamp_fmt: (Optional) timestamp format of prop value (default: yyyy-MM-ddTHH:mm:ssZ)

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        prop_datetime = datetime.strptime(prop, prop_timestamp_fmt).timestamp()
        return prop_datetime < get_timestamp_in_seconds(days, hours, minutes, seconds)

    def _prop_older_than_or_equal_to(
        self,
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        """
        Filter function which returns True if property older than or equal to a relative amount of time since current
        time
        :param prop: prop value to check against
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against
        :param prop_timestamp_fmt: (Optional) timestamp format of prop value (default: yyyy-MM-ddTHH:mm:ssZ)

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        return not self._prop_younger_than(
            prop, days, hours, minutes, seconds, prop_timestamp_fmt
        )
