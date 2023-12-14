from typing import Union
from datetime import datetime

from enums.query.query_presets import QueryPresetsDateTime

from custom_types.openstack_query.aliases import PresetPropMappings

from openstack_query.time_utils import TimeUtils
from openstack_query.handlers.client_side_handler import ClientSideHandler

# pylint: disable=too-many-arguments,too-few-public-methods


class ClientSideHandlerDateTime(ClientSideHandler):
    """
    Client Side handler for Date Time related queries.
    This class stores a dictionary which maps a Date Time preset/prop pairs to a filter function
    Filter functions which map to QueryPresetsDateTime are defined here
    """

    def __init__(self, preset_prop_mappings: PresetPropMappings):
        filter_mappings = {
            QueryPresetsDateTime.OLDER_THAN: self._prop_older_than,
            QueryPresetsDateTime.YOUNGER_THAN: self._prop_younger_than,
            QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: self._prop_older_than_or_equal_to,
            QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: self._prop_younger_than_or_equal_to,
        }
        super().__init__(filter_mappings, preset_prop_mappings)

    @staticmethod
    def _prop_older_than(
        prop: Union[str, None],
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        Filter function which returns True if property older than a relative amount of time since current time.

        :param prop: prop value to check against - in UTC time
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        if prop is None:
            return False
        prop_timestamp = datetime.strptime(prop, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        given_timestamp = TimeUtils.get_timestamp_in_seconds(
            days, hours, minutes, seconds
        )

        return prop_timestamp > given_timestamp

    @staticmethod
    def _prop_younger_than_or_equal_to(
        prop: Union[str, None],
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        Filter function which returns True if property younger than or equal to a relative amount of time since
        current time
        :param prop: prop value to check against - in UTC time
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        if prop is None:
            return False
        prop_timestamp = datetime.strptime(prop, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        given_timestamp = TimeUtils.get_timestamp_in_seconds(
            days, hours, minutes, seconds
        )
        return not prop_timestamp > given_timestamp

    @staticmethod
    def _prop_younger_than(
        prop: Union[str, None],
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        Filter function which returns True if property younger than a relative amount of time since current time
        :param prop: prop value to check against - in UTC time
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        if prop is None:
            return False
        prop_datetime = datetime.strptime(prop, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        return prop_datetime < TimeUtils.get_timestamp_in_seconds(
            days, hours, minutes, seconds
        )

    @staticmethod
    def _prop_older_than_or_equal_to(
        prop: Union[str, None],
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        Filter function which returns True if property older than or equal to a relative amount of time since current
        time
        :param prop: prop value to check against - in UTC time
        :param days: (Optional) relative number of days since current time to compare against
        :param hours: (Optional) relative number of hours since current time to compare against
        :param minutes: (Optional) relative number of minutes since current time to compare against
        :param seconds: (Optional) relative number of seconds since current time to compare against

        By default, all time args are set to 0, i.e. now. Setting this to 10 seconds would mean 10 seconds in the past.
        You must give at least one non-zero argument (days, hours, minutes, seconds) otherwise a
        MissingMandatoryArgument exception will be thrown
        """
        if prop is None:
            return False
        prop_datetime = datetime.strptime(prop, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        return not prop_datetime < TimeUtils.get_timestamp_in_seconds(
            days, hours, minutes, seconds
        )
