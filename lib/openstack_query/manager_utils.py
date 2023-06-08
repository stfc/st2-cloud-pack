from typing import Optional, Set, Any, Dict, List, Union

from enum.query.server_properties import ServerProperties
from enums.query.query_output_option import QueryOutputOption

from structs.query.preset_details import PresetDetails

from openstack_query.server.query_server import QueryServer
from openstack_query.openstack_query_wrapper import OpenstackQueryWrapper


def build_and_run_query(
    cloud_account: str,
    query_obj: OpenstackQueryWrapper,
    preset: Optional[PresetDetails] = None,
    properties_to_select: Optional[Set[ServerProperties]] = None,
    group_by: Optional[ServerProperties] = None,
    sort_by: Optional[ServerProperties] = None,
    output_type: QueryOutputOption = QueryOutputOption.TO_STR,
) -> Union[str, List[Any]]:
    query_obj = populate_query(query_obj, preset, properties_to_select)
    query_obj.run(cloud_account)

    # TODO sort_by group_by

    out = get_query_output(query_obj, output_type)
    return out


def populate_query(
    query_obj: OpenstackQueryWrapper,
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
    query: OpenstackQueryWrapper,
    output_type: QueryOutputOption,
) -> Union[List[Any], str]:
    return {
        QueryOutputOption.TO_STR: query.to_string,
        QueryOutputOption.TO_HTML: query.to_html,
        QueryOutputOption.TO_LIST: query.to_list,
    }.get(output_type, None)()
