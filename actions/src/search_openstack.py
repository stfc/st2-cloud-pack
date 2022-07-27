from tabulate import tabulate

from openstack_action import OpenstackAction
from queryopenstack.query import query


class SearchOpenstack(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # different methods of searching openstack
        self.func = {
            # pylint: disable=line-too-long
            "search_openstack": lambda cloud_account, search_by, query_preset, get_html, search_criteria=None, properties_to_select=None, sort_by_criteria=None, **kwargs: self.output_results(
                query_result=self.get_preset(
                    cloud_account=cloud_account,
                    search_by=search_by,
                    query_preset=query_preset,
                    criteria_list=search_criteria,
                    properties_list=properties_to_select,
                    sort_by_list=sort_by_criteria,
                    **kwargs
                ),
                get_html=get_html,
            ),
            # pylint: disable=line-too-long
            "search_servers_per_user": lambda cloud_account, query_preset, get_html, search_criteria=None, properties_to_select=None, sort_by_criteria=None, **kwargs: self.search_servers_per_user(
                query_result=self.get_preset(
                    cloud_account=cloud_account,
                    search_by="server",
                    query_preset=query_preset,
                    criteria_list=search_criteria,
                    properties_list=properties_to_select,
                    sort_by_list=sort_by_criteria,
                    **kwargs
                ),
                get_html=get_html,
            ),
        }

    @staticmethod
    # pylint: disable=too-many-arguments
    def get_preset(
        cloud_account: str,
        search_by,
        query_preset,
        criteria_list,
        properties_list,
        sort_by_list,
        **kwargs
    ):
        """
        A number of predefined presets for searching openstack
        :param cloud_account: The account from the clouds configuration to use
        :param search_by: openstack objects to search for
        :param query_preset: preset name to use
        :param criteria_list: list of extra criteria
        :param properties_list: list of properties to find for openstack object
        :param sort_by_list: field to sort results openstack_resource
        :param kwargs: other properties
        :return: dict/None - query results
        """

        # if no preset selected - use generic query method
        if query_preset == "no_preset":
            return query(
                cloud_account=cloud_account,
                openstack_resource=search_by,
                properties_list=properties_list,
                criteria_list=criteria_list,
                sort_by_list=sort_by_list,
                console_output=False,
                save=False,
                save_path="",
            )

        # search openstack_resource ID presets (works for all openstack objects)
        func = {
            "id_in": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                cloud_account=cloud_account,
                openstack_resource=search_by,
                properties_list=properties_list,
                criteria_list=[["id", list(kwargs["ids"])]].extend(criteria_list)
                if criteria_list
                else [["id", list(kwargs["ids"])]],
                sort_by_list=sort_by_list,
                console_output=False,
                save=False,
                save_path="",
            ),
            "id_not_in": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                cloud_account=cloud_account,
                openstack_resource=search_by,
                properties_list=properties_list,
                criteria_list=[["not_id", list(kwargs["ids"])]].extend(criteria_list)
                if criteria_list
                else [["not_id", list(kwargs["ids"])]],
                sort_by_list=sort_by_list,
                console_output=False,
                save=False,
                save_path="",
            ),
        }.get(query_preset, None)

        # search openstack_resource Name presets (works for all openstack objects with associated names)
        if not func and search_by != "ip_addr":
            func = {
                "name_in": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                    cloud_account=cloud_account,
                    openstack_resource=search_by,
                    properties_list=properties_list,
                    criteria_list=[
                        ["name"]
                        + [
                            name if name[:7] != "https://" else name[7:]
                            for name in kwargs["names"]
                        ]
                    ].extend(criteria_list)
                    if criteria_list
                    else [
                        ["name"]
                        + [
                            name if name[:7] != "https://" else name[7:]
                            for name in kwargs["names"]
                        ]
                    ],
                    sort_by_list=sort_by_list,
                    console_output=False,
                    save=False,
                    save_path="",
                ),
                "name_not_in": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                    cloud_account=cloud_account,
                    openstack_resource=search_by,
                    properties_list=properties_list,
                    criteria_list=[
                        ["not_name"]
                        + [
                            name if name[:7] != "https://" else name[7:]
                            for name in kwargs["names"]
                        ]
                    ].extend(criteria_list)
                    if criteria_list
                    else [
                        ["not_name"]
                        + [
                            name if name[:7] != "https://" else name[7:]
                            for name in kwargs["names"]
                        ]
                    ],
                    sort_by_list=sort_by_list,
                    console_output=False,
                    save=False,
                    save_path="",
                ),
                "name_contains": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                    cloud_account=cloud_account,
                    openstack_resource=search_by,
                    properties_list=properties_list,
                    criteria_list=[
                        ["name_contains", name] for name in kwargs["name_snippets"]
                    ].extend(criteria_list)
                    if criteria_list
                    else [["name_contains", name] for name in kwargs["name_snippets"]],
                    sort_by_list=sort_by_list,
                    console_output=False,
                    save=False,
                    save_path="",
                ),
                # pylint: disable=line-too-long
                "name_not_contains": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                    cloud_account=cloud_account,
                    openstack_resource=search_by,
                    properties_list=properties_list,
                    criteria_list=[
                        ["name_not_contains", name] for name in kwargs["name_snippets"]
                    ].extend(criteria_list)
                    if criteria_list
                    else [
                        ["name_not_contains", name] for name in kwargs["name_snippets"]
                    ],
                    sort_by_list=sort_by_list,
                    console_output=False,
                    save=False,
                    save_path="",
                ),
            }.get(query_preset, None)

        # more specific presets which are unique to specific openstack object
        if not func:
            func = (
                {
                    "server": {
                        # pylint: disable=line-too-long
                        "server_error_and_shutoff": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[["status", "SHUTOFF", "ERROR"]].extend(
                                criteria_list
                            )
                            if criteria_list
                            else [["status", "SHUTOFF", "ERROR"]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "server_shutoff": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[["status", "SHUTOFF"]].extend(criteria_list)
                            if criteria_list
                            else [["status", "SHUTOFF"]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "server_error": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[["status", "ERROR"]].extend(criteria_list)
                            if criteria_list
                            else [["status", "ERROR"]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "server_older_than": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[["older_than", kwargs["days"]]].extend(
                                criteria_list
                            )
                            if criteria_list
                            else [["older_than", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "server_younger_than": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[["not_older_than", kwargs["days"]]].extend(
                                criteria_list
                            )
                            if criteria_list
                            else [["not_older_than", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "server_last_updated_before": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[
                                ["last_updated_before", kwargs["days"]]
                            ].extend(criteria_list)
                            if criteria_list
                            else [["last_updated_before", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "server_last_updated_after": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="server",
                            properties_list=properties_list,
                            criteria_list=[
                                ["last_updated_after", kwargs["days"]]
                            ].extend(criteria_list)
                            if criteria_list
                            else [["last_updated_after", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                    },
                    "ip_addr": {
                        # pylint: disable=line-too-long
                        "in_projects": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="ip_addr",
                            properties_list=properties_list,
                            criteria_list=[
                                ["project_id"] + list(kwargs["project_ids"])
                            ].extend(criteria_list)
                            if criteria_list
                            else [["project_id"] + list(kwargs["project_ids"])],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "ip_addr_older_than": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="ip_addr",
                            properties_list=properties_list,
                            criteria_list=[["older_than", kwargs["days"]]].extend(
                                criteria_list
                            )
                            if criteria_list
                            else [["older_than", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "ip_addr_younger_than": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="ip_addr",
                            properties_list=properties_list,
                            criteria_list=[["not_older_than", kwargs["days"]]].extend(
                                criteria_list
                            )
                            if criteria_list
                            else [["not_older_than", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "ip_addr_last_updated_before": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="ip_addr",
                            properties_list=properties_list,
                            criteria_list=[
                                ["last_updated_before", kwargs["days"]]
                            ].extend(criteria_list)
                            if criteria_list
                            else [["last_updated_before", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "ip_addr_last_updated_after": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="ip_addr",
                            properties_list=properties_list,
                            criteria_list=[
                                ["last_updated_after", kwargs["days"]]
                            ].extend(criteria_list)
                            if criteria_list
                            else [["last_updated_after", kwargs["days"]]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                    },
                    "host": {
                        # pylint: disable=line-too-long
                        "host_enabled": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="host",
                            properties_list=properties_list,
                            criteria_list=[["status", "enabled"]].extend(criteria_list)
                            if criteria_list
                            else [["status", "enabled"]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                        "host_disabled": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="host",
                            properties_list=properties_list,
                            criteria_list=[["status", "disabled"]].extend(criteria_list)
                            if criteria_list
                            else [["status", "disabled"]],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        ),
                    },
                    "project": {
                        # pylint: disable=line-too-long
                        "description_contains": lambda cloud_account, properties_list, criteria_list, sort_by_list, **kwargs: query(
                            cloud_account=cloud_account,
                            openstack_resource="project",
                            properties_list=properties_list,
                            criteria_list=[
                                ["description_contains", description]
                                for description in kwargs["description_snippets"]
                            ].extend(criteria_list)
                            if criteria_list
                            else [
                                ["description_contains", description]
                                for description in kwargs["description_snippets"]
                            ],
                            sort_by_list=sort_by_list,
                            console_output=False,
                            save=False,
                            save_path="",
                        )
                    },
                }
                .get(search_by, {})
                .get(query_preset, None)
            )

        # run the query and return the results
        return (
            func(cloud_account, properties_list, criteria_list, sort_by_list, **kwargs)
            if func
            else None
        )

    @staticmethod
    def output_results(query_result, get_html=False):
        """
        Output the resulting query results
        :param query_result: dict of query results
        :param get_html: True if output required in html table format else output plain text table
        :return: Status (Bool), String (html or plaintext table of results)
        """
        if query_result:
            headers = query_result[0].keys()
            rows = [row.values() for row in query_result]
            return True, tabulate(
                rows, headers, tablefmt="html" if get_html else "grid"
            )

        return False, "No data found"

    # pylint: disable=missing-function-docstring
    def search_servers_per_user(self, query_result, get_html=False):
        if not query_result:
            return False, "No data found"
        user_server_dict = {}
        for server in query_result:
            user_email = server["user_email"]
            if user_email in user_server_dict:
                user_server_dict[user_email].append(server)
            else:
                user_server_dict[user_email] = [server]

        if "not found" in user_server_dict:
            print("Following Servers found with no associated Email")
            print(self.output_results(user_server_dict["not found"], False))
            del user_server_dict["not found"]

        for email, servers in user_server_dict.items():
            _, output = self.output_results(servers, get_html)
            user_server_dict[email] = output

        return True, user_server_dict
