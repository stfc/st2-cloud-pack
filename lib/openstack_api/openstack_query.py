import datetime
from typing import Any, Callable, List


class OpenstackQuery:
    @staticmethod
    def apply_query(items: List, query_func: Callable[[Any], bool]):
        """
        Removes items from a list by running a given query function
        :param items: List of items to query e.g. list of servers
        :param query_func: Query function that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given query
        """
        for item in items:
            if not query_func(item):
                items.remove(item)

    @staticmethod
    def datetime_before_x_days(
        value: str, days, date_time_format: str = "%Y-%m-%dT%H:%M:%SZ"
    ):
        """
        Function to get if openstack resource is older than a given
        number of days
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            days (int): number of days treshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        return OpenstackQuery.datetime_older_than_offset(
            value,
            datetime.timedelta(days=int(days)).total_seconds(),
            date_time_format,
        )

    @staticmethod
    def datetime_older_than_offset(
        value: str,
        time_offset_in_seconds: int,
        date_time_format: str = "%Y-%m-%dT%H:%M:%SZ",
    ):
        """
        Helper function to get if openstack resource is older than a
        given number of seconds
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            time_offset_in_seconds (int): number of seconds threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        offset_timestamp = (
            datetime.datetime.now()
        ).timestamp() - time_offset_in_seconds
        value_datetime = datetime.datetime.strptime(value, date_time_format).timestamp()
        return offset_timestamp > value_datetime
