from openstack.connection import Connection

from .list_items import ListItems


class ListVolumes(ListItems):
    """
    A class to list volumes: Inherits from ListItems

    Attributes
    ----------
    criteria_func_dict: dict
        stores possible query criteria options -
        criteria name (key) : function to evaluate a criteria on volumes (value)
                function (bool) - evaluate 'volume' properties against criteria
                overrides ListItems attribute

    property_func_dict: dict
        stores possible volume property options
        property name (key) : function to retrieve property (value)
                function (string/int) - returns property value from a 'volume' dictionary
    """

    def __init__(self, conn: Connection):
        """constructor class"""
        super().__init__(conn, conn.list_volumes)

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
                func_dict["created_at"],
                days=args[0],
                date_time_format="%Y-%m-%dT%H:%M:%S.%f",
            ),
            "not_older_than": lambda func_dict, args: not self.is_older_than_x_days(
                func_dict["created_at"],
                days=args[0],
                date_time_format="%Y-%m-%dT%H:%M:%S.%f",
            ),
            "last_updated_before": lambda func_dict, args: self.is_older_than_x_days(
                func_dict["updated_at"],
                days=args[0],
                date_time_format="%Y-%m-%dT%H:%M:%S.%f",
            ),
            "last_updated_after": lambda func_dict, args: not self.is_older_than_x_days(
                func_dict["updated_at"],
                days=args[0],
                date_time_format="%Y-%m-%dT%H:%M:%S.%f",
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

        # Performs a check before accessing a user property in case the user
        # no longer exists (was a problem on dev)
        def find_user_property(item, prop):
            user = self.conn.identity.find_user(item["user_id"])
            if user:
                return user[prop]
            return None

        self.property_func_dict = {
            "volume_attachments": lambda a: a["attachments"],
            "volume_id": lambda a: a["id"],
            "volume_name": lambda a: a["name"],
            "volume_status": lambda a: a["status"],
            "volume_updated_at": lambda a: a["updated_at"],
            "volume_created_at": lambda a: a["created_at"],
            "volume_size": lambda a: a["size"],
            "project_id": lambda a: a["project_id"],
            "project_name": lambda a: self.conn.identity.find_project(a["project_id"])[
                "name"
            ],
            "user_id": lambda a: a["user_id"],
            "user_name": lambda a: find_user_property(a, "name"),
            "user_email": lambda a: find_user_property(a, "email"),
        }
