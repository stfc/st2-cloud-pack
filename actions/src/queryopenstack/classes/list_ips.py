from .list_items import ListItems


class ListIps(ListItems):
    """
    A class to list float ips: Inherits from ListItems

    Attributes
    ----------
    criteria_func_dict: dict
        stores possible query criteria options -
        criteria name (key) : function to evaluate a criteria on ip_addr (value)
                function (bool) - evaluate 'ip_addr' properties against criteria
                overrides ListItems attribute

    property_func_dict: dict
        stores possible ip_addr property options
        property name (key) : function to retrieve property (value)
                function (string/int) - returns property value from a 'ip_addr' dictionary
    """

    def __init__(self, conn):
        """constructor class"""
        super().__init__(conn, conn.list_floating_ips)

        self.criteria_func_dict = {
            "status": lambda func_dict, args: func_dict["status"] in args,
            "not_status": lambda func_dict, args: func_dict["status"] not in args,
            "attached": lambda func_dict, args: func_dict["attached"] is True,
            "not_attached": lambda func_dict, args: func_dict["attached"] is False,
            "id": lambda func_dict, args: func_dict["id"] in args,
            "not_id": lambda func_dict, args: func_dict["id"] not in args,
            "project_id": lambda func_dict, args: func_dict["project_id"] in args,
            "not_project_id": lambda func_dict, args: func_dict["project_id"]
            not in args,
            "older_than": lambda func_dict, args: self.is_older_than_x_days(
                func_dict["created_at"], days=args[0]
            ),
            "not_older_than": lambda func_dict, args: not self.is_older_than_x_days(
                func_dict["created_at"], days=args[0]
            ),
            "project_name": lambda func_dict, args: self.conn.identity.find_project(
                func_dict["project_id"]
            )["name"]
            in args,
            "not project_name": lambda func_dict, args: self.conn.identity.find_project(
                func_dict["project_id"]
            )["name"]
            not in args,
            "project_name_contains": lambda func_dict, args: any(
                arg in self.conn.identity.find_project(func_dict["project_id"])["name"]
                for arg in args
            ),
            "project_name_not_contains": lambda func_dict, args: any(
                arg
                not in self.conn.identity.find_project(func_dict["project_id"])["name"]
                for arg in args
            ),
        }

        self.property_func_dict = {
            "ip_id": lambda a: a["id"],
            "ip_fixed_address": lambda a: a["fixed_ip_address"],
            "ip_floating_address": lambda a: a["floating_ip_address"],
            "ip_port_id": lambda a: a["port_id"],
            "ip_created_at": lambda a: a["created_at"],
            "project_id": lambda a: a["project_id"],
            "project_name": lambda a: self.conn.identity.find_project(a["project_id"])[
                "name"
            ],
        }
