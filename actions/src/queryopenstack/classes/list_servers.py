import re
from typing import List

from openstack.exceptions import ResourceNotFound

from .list_items import ListItems


class ListServers(ListItems):
    """
    A class to list servers (VMs): Inherits from ListItems

    Attributes
    ----------
    criteria_func_dict: dict
        stores possible query criteria options -
        criteria name (key) : function to evaluate a criteria on server (value)
                function (bool) - evaluate 'server' properties against criteria
                overrides ListItems attribute

    property_func_dict: dict
        stores possible server property options
        property name (key) : function to retrieve property (value)
                function (string/int) - returns property value from a 'server' dictionary

    Methods
    --------
    had_illegal_connections(server):
        Checks if the server has illegal IP connections
        returns bool

    are_connections_legal(address_ips):
        Helper function to check illegal ip_addr connections, given a list of ips
        returns bool
    """

    def __init__(self, conn):
        """constructor class"""
        # Currently not working
        # super().__init__(conn, lambda: conn.list_servers(all_projects=True, filters={"limit":10000}))
        super().__init__(conn, self.get_all_servers)

        self.criteria_func_dict.update(
            {
                "status": lambda dict, args: dict["status"] in args,
                "not_status": lambda dict, args: dict["status"] not in args,
                "older_than": lambda dict, args: self.is_older_than_x_days(
                    dict["created_at"], days=args[0]
                ),
                "not_older_than": lambda dict, args: not self.is_older_than_x_days(
                    dict["created_at"], days=args[0]
                ),
                "last_updated_before": lambda dict, args: self.is_older_than_x_days(
                    dict["updated_at"], days=args[0]
                ),
                "last_updated_after": lambda dict, args: not self.is_older_than_x_days(
                    dict["updated_at"], days=args[0]
                ),
                "has_illegal_connections": lambda dict, args: self.had_illegal_connections(
                    dict["addresses"]
                ),
                "user_id": lambda dict, args: dict["user_id"] in args,
                "not_user_id": lambda dict, args: dict["user_id"] not in args,
                "user_name": lambda dict, args: self.conn.identity.find_user(
                    dict["user_id"]
                )["name"]
                in args,
                "not_user_name": lambda dict, args: self.conn.identity.find_user(
                    dict["user_id"]
                )["name"]
                not in args,
                "user_name_contains": lambda dict, args: any(
                    arg in self.conn.identity.find_user(dict["user_id"])["name"]
                    for arg in args
                ),
                "user_name_not_contains": lambda dict, args: any(
                    arg not in self.conn.identity.find_user(dict["user_id"])["name"]
                    for arg in args
                ),
                "host_id": lambda dict, args: dict["host_id"] in args,
                "not_host_id": lambda dict, args: dict["host_id"] not in args,
                "host_name": lambda dict, args: dict["hypervisor_hostname"] in args,
                "not_host_name": lambda dict, args: dict["hypervisor_hostname"]
                not in args,
                "host_name_contains": lambda dict, args: any(
                    arg in dict["hypervisor_hostname"] for arg in args
                ),
                "host_name_not_contains": lambda dict, args: any(
                    arg not in dict["hypervisor_hostname"] for arg in args
                ),
            }
        )

        self.property_func_dict = {
            "user_id": lambda a: a["user_id"],
            "user_name": lambda a: self.conn.identity.find_user(a["user_id"])["name"],
            "user_email": lambda a: self.conn.identity.find_user(a["user_id"])["email"],
            "host_id": lambda a: a["host_id"],
            "host_name": lambda a: a["hypervisor_hostname"],
            "server_id": lambda a: a["id"],
            "server_name": lambda a: a["name"],
            "server_status": lambda a: a["status"],
            "server_creation_date": lambda a: a["created_at"],
            "project_id": lambda a: a["location"]["project"]["id"],
            "project_name": lambda a: a["location"]["project"]["name"],
        }

    def get_all_servers(self) -> List:
        """
        Returns all servers across all projects
        :return: A list of all servers
        """
        all_projects = self.conn.list_projects()
        all_servers = []
        for proj in all_projects:
            try:
                servers = self.conn.list_servers(
                    filters={
                        "all_tenants": True,
                        "project_id": proj["id"],
                        "limit": 10000,
                    }
                )
                all_servers.extend(servers)
            except ResourceNotFound as err:
                print(repr(err))
        return all_servers

    def had_illegal_connections(self, address_dict):
        """
        Function to check if a server has illegal connections
            (if internal 172.16.. ips are mixed with other external ips e.g. 192.168.. & 130.246..)
            Parameters:
                server ({dict}): a dictionary representing the properties
                of a server within openstack

            Returns (bool): True if illegal connection, false if not
        """
        address_ips = []
        for key in address_dict.keys():
            for address in address_dict[key]:
                # address_ips.append(address)
                address_ips.append(address["addr"])
        return not self.are_connections_legal(address_ips)

    @staticmethod
    def are_connections_legal(address_ips):
        """
        Helper function to check if any illegal connection exist in a list of ips
            Parameters:
                address_ips ([string]): list of ips as strings
            Returns (bool): True if no illegal connections else False
        """
        if len(address_ips) == 1:
            return True

        # if list contains ip_addr beginning with 172.16 - all must contain 172.16
        # else allowed
        # turn a flag on when ip_addr other than 172.16 detected.
        # if then detected, flag as illegal

        i_flag = False
        for address in address_ips:
            if re.search("^172.16", address):
                if i_flag:
                    return False
            else:
                if not i_flag:
                    i_flag = True
        return True
