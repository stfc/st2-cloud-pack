import datetime
from typing import Any, Callable, Dict, List

import openstack
from tabulate import tabulate

from email_api.email_api import EmailApi
from openstack_api.dataclasses import (
    NonExistentCheckParams,
    NonExistentProjectCheckParams,
)
from openstack_api.openstack_connection import OpenstackConnection

from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.dataclasses import EmailQueryParams
from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount


class OpenstackQuery(OpenstackWrapperBase):

    # Various queries useful for openstack objects
    def query_datetime_before(self, prop: str, days: int):
        """
        Returns a query for checking if a datetime property is before a specified
        number of days in the past
        """
        return lambda a: self.datetime_before_x_days(a[prop], days)

    def query_datetime_after(self, prop: str, days: int):
        """
        Returns a query for checking if a datetime property is after a specified
        number of days in the past
        """
        return lambda a: not self.datetime_before_x_days(a[prop], days)

    def query_prop_in(self, prop: str, values: List[str]):
        """
        Returns a query for checking if a property value is within a list of values
        """
        return lambda a: a[prop] in values

    def query_prop_not_in(self, prop: str, values: List[str]):
        """
        Returns a query for checking if a property value is not within a list of values
        """
        return lambda a: a[prop] not in values

    def _query_if_prop_exists(
        self, prop: str, query_func: Callable[[Any], bool], default_result: bool
    ):
        """
        Returns the result of a query if the property actually exists, otherwise returns a default value
        useful when openstack parameters may be None e.g. a project description
        :param prop: Property of an openstack object to query e.g. id
        :param query_func: Query function to use if the property isn't None
        :param default_result: Boolean value to return for the query if the property is None
        """

        def check_func(item):
            if not item[prop] is None:
                return query_func(item)
            return default_result

        return check_func

    def query_prop_contains(self, prop: str, snippets: List[str]):
        """
        Returns a query for checking if a property value contains all the snippets given in
        a list
        """
        return self._query_if_prop_exists(
            prop, lambda a: all(snippet in a[prop] for snippet in snippets), False
        )

    def query_prop_not_contains(self, prop: str, snippets: List[str]):
        """
        Returns a query for checking if a property value does not contain all the snippets
        given in a list
        """
        return self._query_if_prop_exists(
            prop, lambda a: all(snippet not in a[prop] for snippet in snippets), True
        )

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(connection_cls)
        self._email_api = EmailApi()

    def apply_query(self, items: List, query_func: Callable[[Any], bool]) -> List:
        """
        Removes items from a list by running a given query function
        :param items: List of items to query e.g. list of servers
        :param query_func: Query function that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given query
        """
        return [item for item in items if query_func(item)]

    def apply_queries(
        self, items: List, query_funcs: List[Callable[[Any], bool]]
    ) -> List:
        """
        Removes items from a list by running a set of given query function
        :param items: List of items to query e.g. list of servers
        :param query_funcs: List of query functions that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given queries
        """
        result = items
        for query_func in query_funcs:
            result = self.apply_query(items=result, query_func=query_func)
        return result

    def datetime_before_x_days(
        self, value: str, days: int, date_time_format: str = "%Y-%m-%dT%H:%M:%SZ"
    ) -> bool:
        """
        Function to get if openstack resource is older than a given
        number of days
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            days (int): number of days threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        return self.datetime_older_than_offset(
            value,
            datetime.timedelta(days=days).total_seconds(),
            date_time_format,
        )

    def datetime_older_than_offset(
        self,
        value: str,
        time_offset_in_seconds: float,
        date_time_format: str = "%Y-%m-%dT%H:%M:%SZ",
    ) -> bool:
        """
        Helper function to get if openstack resource is older than a
        given number of seconds
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            time_offset_in_seconds (float): number of seconds threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        offset_timestamp = (
            datetime.datetime.now()
        ).timestamp() - time_offset_in_seconds
        value_datetime = datetime.datetime.strptime(value, date_time_format).timestamp()
        return offset_timestamp > value_datetime

    def parse_properties(
        self,
        items: List,
        properties_to_list: List[str],
        property_funcs: Dict[str, Callable[[Any], Any]],
    ) -> List[Dict]:
        """
        Generates a dictionary of queried properties from a list of openstack objects e.g. servers
        :param items: List of items to obtain properties from
        :param properties_to_list: List of properties to obtain from the items
        :param property_funcs: Query functions that return properties requested in 'properties_to_list'
        :return: List containing dictionaries of the requested properties obtained from the items
        """
        output = []
        for item in items:
            item_output = {}
            for prop in properties_to_list:
                # If the property func is listed then use that, otherwise assume can obtain from the object directly
                if prop in property_funcs:
                    property_value = property_funcs[prop](item)
                else:
                    try:
                        property_value = item[prop]
                    except AttributeError:
                        property_value = "Not found"

                item_output[prop] = property_value
            output.append(item_output)
        return output

    def generate_table(
        self, properties_dict: List[Dict[str, Any]], get_html: bool
    ) -> str:
        """
        Returns a table from the result of 'parse_properties'
        :param properties_dict: dict of query results
        :param get_html: True if output required in html table format else output plain text table
        :return: String (html or plaintext table of results)
        """
        headers = properties_dict[0].keys()
        rows = [row.values() for row in properties_dict]
        return tabulate(rows, headers, tablefmt="html" if get_html else "grid")

    def collate_results(
        self, properties_dict: List[Dict[str, Any]], key: str, get_html: bool
    ) -> Dict[str, str]:
        """
        Collates results from a dict based on a given property key and returns a dictionary of
        these keys with tables of the properties
        :param properties_dict: dict of query results
        :param key: key to collate by e.g. user_email
        :param get_html: True if output required in html table format else output plain text table
        :return: Dict[str, str] (each key containing html or plaintext table of results)
        """
        collated_dict = {}
        for item in properties_dict:
            key_value = item[key]
            if key_value in collated_dict:
                collated_dict[key_value].append(item)
            else:
                collated_dict[key_value] = [item]

        if None in collated_dict:
            print(f"The following items were found with no associated key '{key}'")
            print(self.generate_table(collated_dict[None], False))
            del collated_dict[None]

        for key_value, items in collated_dict.items():
            collated_dict[key_value] = self.generate_table(items, get_html)

        return collated_dict

    def get_default_property_funcs(
        self, object_type: str, cloud_account: str
    ) -> Dict[str, Callable[[Any], Any]]:
        """
        Returns a list of default property functions for use with 'parse_properties' above
        :param object_type: type of openstack object the functions will be used for e.g. server
        :param cloud_account: The account from the clouds configuration to use
        :return: Dict[str, Callable[[Any], Any]] functions that return properties from openstack
                 objects
        """

        def get_project_prop(project_id, prop):
            project = self._identity_api.find_project(cloud_account, project_id)
            if project:
                return project[prop]
            return None

        def get_user_prop(user_id, prop):
            user = self._identity_api.find_user_all_domains(cloud_account, user_id)
            if user:
                return user[prop]
            return None

        if object_type == "server":
            return {
                "user_email": lambda a: get_user_prop(a["user_id"], "email"),
                "user_name": lambda a: get_user_prop(a["user_id"], "name"),
            }
        if object_type == "floating_ip":
            return {
                "project_name": lambda a: get_project_prop(a["project_id"], "name"),
                "project_email": lambda a: self._identity_api.find_project_email(
                    cloud_account, a["project_id"]
                ),
            }
        if object_type == "project":
            return {
                "email": self._identity_api.get_project_email,
            }
        if object_type == "image":
            return {
                "project_name": lambda a: get_project_prop(a["owner"], "name"),
                "project_email": lambda a: self._identity_api.find_project_email(
                    cloud_account, a["owner"]
                ),
            }
        raise ValueError(f"Unsupported object type '{object_type}'")

    # pylint:disable=too-many-arguments
    def parse_and_output_table(
        self,
        cloud_account: str,
        items: List,
        object_type: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
    ):
        """
        Finds selected properties of a list of OpenStack resources and then generates tables for them
        grouping the results by a particular property if requested
        :param cloud_account: The account from the clouds configuration to use
        :param items: List of items to obtain properties from
        :param object_type: type of openstack object the functions will be used for e.g. server
        :param properties_to_select: The list of properties to select and output from the found servers
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        property_funcs = self.get_default_property_funcs(object_type, cloud_account)
        output = self.parse_properties(items, properties_to_select, property_funcs)

        if len(output) == 0:
            return None

        if group_by != "":
            output = self.collate_results(output, group_by, get_html)
        else:
            output = self.generate_table(output, get_html)

        return output

    def find_non_existent_objects(
        self,
        cloud_account: str,
        project_identifier: str,
        check_params: NonExistentCheckParams,
    ) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of projects along with a list of ids of non-existent openstack objects
        found within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param check_params: Parameters required for running the check
        :return: A dictionary containing the non-existent object ids and their projects
        """
        selected_projects = {}
        if project_identifier == "":
            projects = self._identity_api.list_projects(cloud_account)
        else:
            projects = [
                self._identity_api.find_mandatory_project(
                    cloud_account, project_identifier=project_identifier
                )
            ]

        with self._connection_cls(cloud_account) as conn:
            for project in projects:
                objects_in_project = check_params.object_list_func(conn, project)
                for obj in objects_in_project:
                    object_id = obj[check_params.object_id_param_name]
                    try:
                        check_params.object_get_func(conn, object_id)
                    except openstack.exceptions.ResourceNotFound:
                        if project.id in selected_projects:
                            selected_projects[project.id].append(object_id)
                        else:
                            selected_projects.update({project.id: [object_id]})
        return selected_projects

    def find_non_existant_object_projects(
        self,
        cloud_account: str,
        check_params: NonExistentProjectCheckParams,
    ) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of non-existent projects along with a list object ids that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :param check_params: Parameters required for running the check
        :return: A dictionary containing the non-existent projects and a list of object ids that refer to them
        """
        selected_projects = {}
        with self._connection_cls(cloud_account) as conn:
            all_objects = check_params.object_list_func(conn)
            for obj in all_objects:
                object_id = obj[check_params.object_id_param_name]
                project_id = obj[check_params.object_project_param_name]
                try:
                    conn.identity.get_project(project_id)
                except openstack.exceptions.ResourceNotFound:
                    if project_id in selected_projects:
                        selected_projects[project_id].append(object_id)
                    else:
                        selected_projects.update({project_id: [object_id]})
        return selected_projects

    # pylint:disable=too-many-arguments,too-many-locals
    def email_users(
        self,
        cloud_account: str,
        smtp_account: SMTPAccount,
        query_params: EmailQueryParams,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        email_params: EmailParams,
        **kwargs,
    ):
        """
        Finds all OpenStack resources matching a query and then sends emails to their users
        :param: cloud_account: The account from the clouds configuration to use
        :param: smtp_account (SMTPAccount): SMTP config
        :param: query_params: See EmailQueryParams
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: query_preset: The query to use when searching for OpenStack resources
        :param: message: Message to add to the body of emails sent
        :param: properties_to_select: The list of properties to select and output from the found resources
        :param: email_params: See EmailParams
        :param: kwargs: Additional parameters required for the query_preset chosen
        :raises ValueError: If action_params.required_email_property is not present in properties_to_select
        :raises ValueError: If project_identifier is empty and query_preset is not present in
                            action_params.valid_search_queries_no_project
        :return:
        """
        if query_params.required_email_property not in properties_to_select:
            raise ValueError(
                f"properties_to_select must contain '{query_params.required_email_property}'"
            )

        if query_preset not in query_params.valid_search_queries:
            raise ValueError(
                f"query_preset is invalid, must be one of {','.join(query_params.valid_search_queries)}"
            )

        # Ensure only a valid query preset is used when there is no project
        # (try and prevent mistakenly emailing loads of people)
        if project_identifier == "":
            if query_preset not in query_params.valid_search_queries_no_project:
                raise ValueError(
                    f"project_identifier needed for the query type '{query_preset}'"
                )

        openstack_objects = query_params.search_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        emails = self.parse_and_output_table(
            cloud_account=cloud_account,
            items=openstack_objects,
            object_type=query_params.object_type,
            properties_to_select=properties_to_select,
            group_by=query_params.required_email_property,
            get_html=email_params.send_as_html,
        )

        if emails is None:
            return "No emails to send"

        for key, value in emails.items():
            separator = "<br><br>" if email_params.send_as_html else "\n\n"
            emails[key] = f"{message}{separator}{value}"

        return self._email_api.send_emails(
            smtp_account=smtp_account,
            email_params=email_params,
            emails=emails,
        )
