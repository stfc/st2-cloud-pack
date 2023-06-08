from enum import Enum
from typing import Optional, Set, Any, List, Union

from enums.query.server_properties import ServerProperties
from enums.query.query_output_types import QueryOutputTypes

from structs.query.query_details import QueryDetails
from structs.query.preset_details import PresetDetails

from openstack_query.server.query_server import QueryServer
from openstack_query.query_wrapper import QueryWrapper

QueryReturn = Union[str, List[Any]]


def run_and_build_query(
    cloud_account: str,
    query_obj: QueryWrapper,
    query_details: QueryDetails,
    preset_details: PresetDetails,
):
    query_obj = populate_query(
        query_obj,
        preset_details=preset_details,
        properties_to_select=query_details.properties_to_select,
    )
    query_obj.run(cloud_account)
    return collate_query_results(
        query_obj,
        query_details.sort_by,
        query_details.group_by,
        query_details.output_type,
    )


def collate_query_results(
    query_obj: QueryWrapper,
    sort_by: Optional[Enum],
    group_by: Optional[Enum],
    output_type: QueryOutputTypes = QueryOutputTypes.TO_STR,
) -> QueryReturn:

    # TODO sort by and group by here

    return get_query_output(query_obj, output_type)


def populate_query(
    query_obj: QueryWrapper,
    preset_details: Optional[PresetDetails] = None,
    properties_to_select: Optional[Set[ServerProperties]] = None,
) -> QueryServer:
    if properties_to_select:
        query_obj.select(properties_to_select)
    else:
        query_obj.select_all()

    if preset_details:
        query_obj.where(preset_details.preset, preset_details.prop, preset_details.args)

    return query_obj


def get_query_output(
    query: QueryWrapper,
    output_type: QueryOutputTypes,
) -> QueryReturn:
    return {
        QueryOutputTypes.TO_STR: query.to_string,
        QueryOutputTypes.TO_HTML: query.to_html,
        QueryOutputTypes.TO_LIST: query.to_list,
    }.get(output_type, None)()
