import ast
from typing import Callable, Dict
import logging
import sys
from datetime import datetime
from openstack_api.openstack_connection import OpenstackConnection
from st2common.runners.base_action import Action
from post_ticket import post_ticket


class CheckActions(Action):

    # pylint: disable=arguments-differ
    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint: disable=too-many-arguments, too-many-locals
    def _check_project_loadbalancers(
        self, project: str, cloud: str, max_port: int, min_port: int, ip_prefix: str
    ):
        """
        Does the logic for security_groups_check, should not be invoked seperately.
        """

        with OpenstackConnection(cloud_name=cloud) as conn:
            sec_group = conn.list_security_groups(filters={"project_id": project})
        # pylint: disable=too-many-function-args

        bad_rules = self._bad_rules(max_port, min_port, ip_prefix, sec_group)
        rules_with_issues = self._check_if_applied(bad_rules, cloud, project)

        return rules_with_issues

    @staticmethod
    def _bad_rules(max_port, min_port, ip_prefix, sec_group):
        for group in sec_group:
            for rules in group["security_group_rules"]:
                # pylint: disable=line-too-long
                if (
                    rules["remote_ip_prefix"] == ip_prefix
                    and rules["port_range_max"] == max_port
                    and rules["port_range_min"] == min_port
                ):
                    return rules
        return {}

    @staticmethod
    def _check_if_applied(rules: Dict, cloud, project):
        rules_with_issues = []
        with OpenstackConnection(cloud_name=cloud) as conn:
            servers = conn.list_servers(
                filters={"all_tenants": True, "project_id": project}
            )

        for server in servers:

            with OpenstackConnection(cloud_name=cloud) as conn:
                applied = conn.list_server_security_groups(server.id)

            for serv_groups in applied:
                if serv_groups["id"] == rules["security_group_id"]:
                    print("Rule is applied")
                    rules_with_issues.append(
                        {
                            "dataTitle": {"id": server["id"]},
                            "dataBody": {
                                "proj_id": project,
                                "sec_id": serv_groups["id"],
                                "applied": "Yes",
                            },
                        }
                    )
                else:
                    rules_with_issues.append(
                        {
                            "dataTitle": {"id": server["id"]},
                            "dataBody": {
                                "proj_id": project,
                                "sec_id": serv_groups["id"],
                                "applied": "no",
                            },
                        }
                    )
                    print("Rule not applied to " + server["id"])
        return rules_with_issues

    def security_groups_check(
        self,
        cloud_account: str,
        max_port: int,
        min_port: int,
        ip_prefix: str,
        project_id=None,
        all_projects=False,
    ):
        """
        Starts the script to check projects, can choose to go through all projects or a single project.

        Params:
        Cloud (Required): The name of the cloud to open from clouds.yaml

        Requires one of:
            all_projects (optional): Boolean for checking all projects, defaults to False
            project (optional): ID of project to check
        """

        # all_servers.filter(location.project.id=project)

        # print(servers.get_all_servers())
        rules_with_issues = {
            "title": "Server {p[id]} has an incorrectly configured server group",
            "body": "Project id: {p[proj_id]}\nSecurity Group ID: {p[sec_id]}\n Is applied: {p[applied]}",
            "server_list": [],
        }

        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()

        else:
            projects = [{"id": project_id}]
        for project in projects:
            output = self._check_project_loadbalancers(
                project=project["id"],
                cloud=cloud_account,
                max_port=max_port,
                min_port=min_port,
                ip_prefix=ip_prefix,
            )
            rules_with_issues["server_list"].extend(output)

        return rules_with_issues

    def check_notify_snapshots(
        self, cloud_account: str, project_id=None, all_projects=False
    ):
        """
        Set off and return check for snapshots older than one month
        """
        # pylint: disable=line-too-long
        output = {
            "title": "Project {p[name]} has an old volume snapshot",
            "body": "The volume snapshot was last updated on: {p[updated]}\nSnapshot name: {p[name]}\nSnapshot id: {p[id]}\nProject id: {p[project_id]}",
            "server_list": [],
        }
        snapshots = []
        if all_projects:
            with OpenstackConnection(cloud_name=cloud_account) as conn:
                projects = conn.list_projects()
        else:
            projects = [{"id": project_id}]

        for project in projects:
            snapshots.extend(
                self.check_snapshots(project=project["id"], cloud_account=cloud_account)
            )
        with OpenstackConnection(cloud_name=cloud_account) as conn:
            for snapshot in snapshots:
                proj = conn.get_project(name_or_id=snapshot["project_id"])

                output["server_list"].append(
                    {"dataTitle": {"name": proj["name"]}, "dataBody": snapshot}
                )
            # Send email to notify users? projects don't have contact details :/

        return output

    @staticmethod
    def check_snapshots(cloud_account, project: str):
        """
        Check for snapshots that haven't been updated in more than a month.
        """
        snap_list = []
        with OpenstackConnection(cloud_name=cloud_account) as conn:
            volume_snapshots = conn.list_volume_snapshots(
                search_opts={"all_tenants": True, "project_id": project}
            )
        for snapshot in volume_snapshots:
            try:
                since_updated = datetime.strptime(
                    snapshot["updated_at"], "%Y-%m-%dT%H:%M:%S.%f"
                )
            except KeyError:
                since_updated = datetime.strptime(
                    snapshot["created_at"], "%Y-%m-%dT%H:%M:%S.%f"
                )
            if since_updated.month != datetime.now().month:
                try:
                    snap_list.append(
                        {
                            "name": snapshot["name"],
                            "id": snapshot["id"],
                            "updated": snapshot["updated_at"],
                            "project_id": snapshot[
                                "os-extended-snapshot-attributes:project_id"
                            ],
                        }
                    )
                except KeyError:
                    snap_list.append(
                        {
                            "name": snapshot["name"],
                            "id": snapshot["id"],
                            "updated": snapshot["created_at"],
                            "project_id": snapshot["location"]["project"]["id"],
                        }
                    )
        return snap_list

    @staticmethod
    def create_ticket(
        tickets_info, email: str, api_key: str, servicedesk_id, requesttype_id
    ):
        # pylint: disable=line-too-long
        """
        Function to create tickets in an atlassian project. The tickets_info value should be formatted as such:
        {
            "title": "This is the {p[title]}",
            "body": "This is the {p[body]}", #The {p[value]} is used by python formatting to insert the correct value in this spot, based off data passed in with server_list
            "server_list": [
                {
                    "dataTitle":{"title": "This replaces the {p[title]} value!"}, #These dictionary entries are picked up in create_ticket
                    "dataBody":{"body": "This replaces the {p[body]} value"}
                }
            ] This list can be arbitrarily long, it will be iterated and each element will create a ticket based off the title and body keys and modified with the info from dataTitle and dataBody. For an example on how to do this please see deleting_machines_check
        }
        """
        print(tickets_info)
        try:
            actual_tickets_info = tickets_info["result"]
        except TypeError:
            actual_tickets_info = ast.literal_eval(tickets_info)

        if len(actual_tickets_info["server_list"]) == 0:
            logging.info("No issues found")
            sys.exit()
        for ticket in actual_tickets_info["server_list"]:

            # pylint: disable=too-many-function-args
            issue = post_ticket(
                actual_tickets_info,
                ticket,
                servicedesk_id,
                requesttype_id,
                email,
                api_key,
            )

            if issue.status_code != 201:
                logging.error("Error creating issue %i", issue.status_code)
            elif issue.status_code == 201:
                logging.info("Created issue")
