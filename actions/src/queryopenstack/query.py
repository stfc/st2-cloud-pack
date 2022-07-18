from .classes.list_hosts import ListHosts
from .classes.list_ips import ListIps
from .classes.list_projects import ListProjects
from .classes.list_servers import ListServers
from .classes.list_users import ListUsers
from .utils import (
    create_openstack_connection,
    output_to_console,
    output_to_file,
    validate_input_list,
)


# pylint: disable=too-many-arguments,too-many-locals
def query(
    cloud_account,
    openstack_resource,
    properties_list,
    criteria_list,
    sort_by_list,
    console_output=False,
    save=False,
    save_path="~/Openstack_Logs/output.csv",
    openstack_conn=None,
):
    """
    Function to handle an openstack query

        Parameters:
            cloud_account (string): The account from the clouds configuration to use
            openstack_resource (string): openstack resource to search by
            properties_list ([string]): list of properties to get for each openstack resource found
            criteria_list ([string]): list of criteria/conditional arguments that make up the query
            sort_by_list ([string]): list of properties to sort the results by

        Optional Parameters:
            console_output (bool): flag to toggle print to console
            save (bool): flag to toggle save to txt file
            save_in (string): path to directory in which to save the txt file
            openstack_conn (openstack.connection.Connection object): user given openstack connection

        Returns:
            res ([{dict}]): list of dictionaries - query results
            (each dict in list representing a single compute resource)
            None: if query fails
    """

    # if no user defined openstack connection given - create default one
    if not openstack_conn:
        openstack_conn = create_openstack_connection(cloud_name=cloud_account)

    # validate openstack_resource
    list_class = {
        "user": ListUsers,
        "server": ListServers,
        "project": ListProjects,
        "ip_addr": ListIps,
        "host": ListHosts,
    }.get(openstack_resource, None)

    if not list_class:
        print(f"Search openstack_resource condition {openstack_resource} is invalid")
        return None

    list_obj = list_class(openstack_conn)

    # validate properties_list
    properties_to_use, invalid = validate_input_list(
        properties_list, list_obj.property_func_dict.keys()
    )
    if invalid:
        print(f"Following properties are not valid: {invalid}")
    if not properties_to_use:
        print("No properties given/valid - aborting")
        return None

    # validate criteria_list
    if criteria_list:
        criteria_names, invalid = validate_input_list(
            [criteria[0] for criteria in criteria_list],
            list_obj.criteria_func_dict.keys(),
        )
        if invalid:
            print(f"Following properties are not valid: \n {invalid}")
        criteria_to_use = [
            (criteria[0], criteria[1:])
            for criteria in criteria_list
            if criteria[0] in criteria_names
        ]
    else:
        criteria_to_use = []
    # validate sort_by_list
    sort_by_to_use, invalid = validate_input_list(
        sort_by_list, list_obj.property_func_dict.keys()
    )
    if invalid:
        print(f"Following sort_by are not valid: \n {invalid}")

    print(
        f"""Searching openstack_resource resouce: {openstack_resource}
Criteria Selected: {criteria_to_use}
Properties Selected: {properties_to_use}
Sort By Selected: {sort_by_to_use}"""
    )

    # get results
    items = list_obj.list_items(criteria_to_use)
    if items:
        res = list_obj.get_properties(items, properties_to_use)

        if sort_by_to_use:
            res = sorted(res, key=lambda a: tuple(a[arg] for arg in sort_by_to_use))
        if console_output:
            output_to_console(res)
        if save:
            output_to_file(save_path, res)

        return res
    return None
