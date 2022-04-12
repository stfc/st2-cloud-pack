from .list_items import ListItems


class ListProjects(ListItems):
    """
    A class to list projects: Inherits from ListItems

    Attributes
    ----------
    criteria_func_dict: dict
        stores possible query criteria options -
        criteria name (key) : function to evaluate a criteria on project (value)
                function (bool) - evaluate 'projects' properties against criteria
                overrides ListItems attribute

    property_func_dict: dict
        stores possible project property options
        property name (key) : function to retrieve property (value)
                function (string/int) - returns property value from a 'projects' dictionary
    """

    def __init__(self, conn):
        """constructor class"""
        super().__init__(conn, conn.list_projects)

        self.criteria_func_dict.update(
            {
                "enabled": lambda func_dict, args: func_dict["enabled"] is True,
                "not_enabled": lambda func_dict, args: func_dict["enabled"] is False,
                "description_contains": lambda func_dict, args: any(
                    arg in func_dict["description"] for arg in args
                ),
            }
        )

        self.property_func_dict = {
            "project_id": lambda a: a["id"],
            "project_name": lambda a: a["name"],
            "project_description": lambda a: a["description"],
        }
