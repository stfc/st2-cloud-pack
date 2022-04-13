from .list_items import ListItems


class ListUsers(ListItems):
    """
    A class to list users: Inherits from ListItems

    Attributes
    ----------
    criteria_func_dict: dict
        stores possible query criteria options -
        criteria name (key) : function to evaluate a criteria on user (value)
                function (bool) - evaluate 'user' properties against criteria
                overrides ListItems attribute

    property_func_dict: dict
        stores possible user property options
        property name (key) : function to retrieve property (value)
                function (string/int) - returns property value from a 'user' dictionary

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
        super().__init__(conn, conn.list_users)

        self.criteria_func_dict.update(
            {
                "enabled": lambda func_dict, args: func_dict["enabled"] is True,
                "not_enabled": lambda func_dict, args: func_dict["enabled"] is False,
            }
        )

        self.property_func_dict = {
            "user_id": lambda a: a["id"],
            "user_name": lambda a: a["name"],
            "user_email": lambda a: a["email"],
        }
