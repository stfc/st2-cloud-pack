from typing import List, Dict, Tuple
from openstackquery import ServerQuery, FlavorQuery

def find_servers_on_hv(hypervisor_name: str) -> Dict[str, Tuple[int,int]]:
    """
    Returns all the servers on a HV and groups them by flavor id
    :param hypervisor_name: the name of the hypervisor
    """

    # Find VMs that have been on a hypervisor
    server_query = ServerQuery()

    server_query.where("equal_to",
                       "hypervisor_name",
                       value=hypervisor_name)

    server_query.group_by("flavor_id")

    server_query.run("dev",
                     as_admin=True,
                     all_projects=True)

    if not server_query.to_props():
        return {}

    return {flavor_id:len(server_list) for flavor_id, server_list in server_query.to_objects()}


def get_flavor_characteristics(cloud_account: str,
                               flavor_id_list: List[str]) -> Dict[str, Tuple[int,int]]:
    """
    Returns VCPU and RAM information for each flavor id in a list provided
    :param cloud_account: string represents cloud account to use
    :param flavor_id_list: list of flavor ids
    """
    flavor_query = FlavorQuery()

    flavor_query.select("flavor_id",
                        "vcpu", 
                        "ram")

    flavor_query.where("any_in",
                       "flavor_id",
                       values=flavor_id_list)

    flavor_query.run(cloud_account)
    return {flavor["flavor_id"]:(flavor["vcpu"], flavor["ram"]) for flavor in flavor_query.to_props()}

