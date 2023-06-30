from typing import List, Any, Union


from enums.query.query_presets import (
    QueryPresetsDateTime,
    QueryPresetsString,
)
from enums.query.server_properties import ServerProperties

from openstack_query.queries.query_server import QueryServer
from openstack_query.managers.query_manager import QueryManager

from structs.query.query_output_details import QueryOutputDetails
from structs.query.query_preset_details import QueryPresetDetails


class ServerManager(QueryManager):
    """
    Manager for querying Openstack Server objects.
    """

    def __init__(self, cloud_account: str):
        QueryManager.__init__(self, query=QueryServer(), cloud_account=cloud_account)

    def search_all_servers(
        self, output_details: QueryOutputDetails
    ) -> Union[str, List[Any]]:
        """
        method that returns a list of all servers
        :param output_details: A dataclass containing config info on how results should be returned
        """
        return self._build_and_run_query(
            preset_details=None,
            output_details=output_details,
        )

    def search_servers_older_than_relative_to_now(
        self,
        output_details: QueryOutputDetails,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        method that returns a list of all servers older than a time relative to now
        :param output_details: A dataclass containing config info on how results should be returned
        :param days: number of days since current time
        :param hours: number of hours since current time
        :param minutes: number of minutes since current time
        :param seconds: number of seconds since current time
        """
        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.OLDER_THAN,
                prop=ServerProperties.SERVER_CREATION_DATE,
                args={
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "prop_timestamp_fmt": "%Y-%m-%dT%H:%M:%SZ",
                },
            ),
            output_details=output_details,
        )

    def search_servers_younger_than_relative_to_now(
        self,
        output_details: QueryOutputDetails,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        method that returns a list of all servers younger than a time relative to now
        :param output_details: A dataclass containing config info on how results should be returned
        :param days: number of days since current time
        :param hours: number of hours since current time
        :param minutes: number of minutes since current time
        :param seconds: number of seconds since current time
        """
        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.YOUNGER_THAN,
                prop=ServerProperties.SERVER_CREATION_DATE,
                args={
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "prop_timestamp_fmt": "%Y-%m-%dT%H:%M:%SZ",
                },
            ),
            output_details=output_details,
        )

    def search_servers_last_updated_before_relative_to_now(
        self,
        output_details: QueryOutputDetails,
        days: int,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        method that returns a list of all servers which were last updated before a time relative to now
        :param output_details: A dataclass containing config info on how results should be returned
        :param days: number of days since current time
        :param hours: number of hours since current time
        :param minutes: number of minutes since current time
        :param seconds: number of seconds since current time
        """
        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.OLDER_THAN,
                prop=ServerProperties.SERVER_LAST_UPDATED_DATE,
                args={
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "prop_timestamp_fmt": "%Y-%m-%dT%H:%M:%SZ",
                },
            ),
            output_details=output_details,
        )

    def search_servers_last_updated_after_relative_to_now(
        self,
        output_details: QueryOutputDetails,
        days: int,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """
        method that returns a list of all servers which were last updated after a time relative to now
        :param output_details: A dataclass containing config info on how results should be returned
        :param days: number of days since current time
        :param hours: number of hours since current time
        :param minutes: number of minutes since current time
        :param seconds: number of seconds since current time
        """
        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.YOUNGER_THAN,
                prop=ServerProperties.SERVER_LAST_UPDATED_DATE,
                args={
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "prop_timestamp_fmt": "%Y-%m-%dT%H:%M:%SZ",
                },
            ),
            output_details=output_details,
        )

    def search_servers_name_in(
        self, output_details: QueryOutputDetails, names: List[str]
    ):
        """
        method that returns a list of all servers which have a name in a given list
        :param output_details: A dataclass containing config info on how results should be returned
        :param names: a list of server names to check against
        """
        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.ANY_IN,
                prop=ServerProperties.SERVER_NAME,
                args={"values": names},
            ),
            output_details=output_details,
        )

    def search_servers_name_not_in(
        self, output_details: QueryOutputDetails, names: List[str]
    ):
        """
        method that returns a list of all servers which do not have a name matching any from a given list
        :param output_details: A dataclass containing config info on how results should be returned
        :param names: a list of server names to check against
        """
        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.NOT_ANY_IN,
                prop=ServerProperties.SERVER_NAME,
                args={"values": names},
            ),
            output_details=output_details,
        )