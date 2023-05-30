from typing import List, Dict, Any, Union
from structs.query.query_details import QueryDetails
from structs.query.preset_details import PresetDetails

from enums.query.query_presets import QueryPresets
from enums.query.server.server_properties import ServerProperties

from openstack_query.query_server import QueryServer
import openstack_query.manager_utils as manager_utils


def search_all_servers(cloud_account: str,  query_details: QueryDetails) -> Union[str, List[Any]]:
    return manager_utils.run_query(
        cloud_account,
        None,
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )


def search_servers_older_than(
    cloud_account: str,
    query_details: QueryDetails,
    days: int,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
):
    return manager_utils.run_query(
        cloud_account,
        QueryServer(),
        PresetDetails(
            preset=QueryPresets.OLDER_THAN,
            prop=ServerProperties.SERVER_CREATION_DATE,
            args={
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'prop_timestamp_fmt': "%Y-%m-%dT%H:%M:%SZ"
            }
        ),
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )


def search_servers_younger_than(
    cloud_account: str,
    query_details: QueryDetails,
    days: int,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
):
    return manager_utils.run_query(
        cloud_account,
        QueryServer(),
        PresetDetails(
            preset=QueryPresets.YOUNGER_THAN,
            prop=ServerProperties.SERVER_CREATION_DATE,
            args={
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'prop_timestamp_fmt': "%Y-%m-%dT%H:%M:%SZ"
            }
        ),
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )


def search_servers_last_updated_before(
    cloud_account: str,
    query_details: QueryDetails,
    days: int,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
):
    return manager_utils.run_query(
        cloud_account,
        QueryServer(),
        PresetDetails(
            preset=QueryPresets.OLDER_THAN,
            prop=ServerProperties.SERVER_LAST_UPDATED_DATE,
            args={
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'prop_timestamp_fmt': "%Y-%m-%dT%H:%M:%SZ"
            }
        ),
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )


def search_servers_last_updated_after(
    cloud_account: str,
    query_details: QueryDetails,
    days: int,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
):
    return manager_utils.build_and_run_query(
        cloud_account,
        QueryServer(),
        PresetDetails(
            preset=QueryPresets.YOUNGER_THAN,
            prop=ServerProperties.SERVER_LAST_UPDATED_DATE,
            args={
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'prop_timestamp_fmt': "%Y-%m-%dT%H:%M:%SZ"
            }
        ),
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )


def search_servers_name_in(
    cloud_account: str,
    query_details: QueryDetails,
    names: List[str]
):
    return manager_utils.build_and_run_query(
        cloud_account,
        QueryServer(),
        PresetDetails(
            preset=QueryPresets.ANY_IN,
            prop=ServerProperties.SERVER_NAME,
            args={
                'values': names
            }
        ),
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )


def search_servers_name_not_in(
    cloud_account: str,
    query_details: QueryDetails,
    names: List[str]
):
    return manager_utils.run_query(
        cloud_account,
        QueryServer(),
        PresetDetails(
            preset=QueryPresets.NOT_ANY_IN,
            prop=ServerProperties.SERVER_NAME,
            args={
                'values': names
            }
        ),
        query_details.properties_to_select,
        query_details.group_by,
        query_details.sort_by,
    )
