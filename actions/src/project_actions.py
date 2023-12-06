from typing import Tuple, Optional, Dict, Callable, Union, List

from openstack.identity.v3.project import Project

from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_project import OpenstackProject
from openstack_api.openstack_query import OpenstackQuery
from structs.project_details import ProjectDetails
from st2common.runners.base_action import Action


class ProjectAction(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        # DI handled in OpenstackActionTestCase
        super().__init__(*args, config=config, **kwargs)
        self._identity_api: OpenstackIdentity = config.get(
            "openstack_identity_api", OpenstackIdentity()
        )
        self._project_api: OpenstackProject = config.get(
            "openstack_project_api", OpenstackProject()
        )
        self._query_api: OpenstackQuery = config.get(
            "openstack_query_api", OpenstackQuery()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches
        :param submodule: the method to run
        :param kwargs: Arguments to the method
        :return: The output from that method
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def project_delete(
        self, cloud_account: str, project_identifier: str, delete: bool
    ) -> Tuple[bool, str]:
        """
        Deletes a project
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: (Either) The project name to delete
        :param delete: When true will delete the project, when false will only return it to reduce
                       chances of accidental deletion
        :return: The result of the operation
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        project_string = self._query_api.parse_and_output_table(
            items=[project],
            property_funcs=self._project_api.get_query_property_funcs(cloud_account),
            properties_to_select=["id", "name", "description", "email"],
            group_by="",
            return_html=False,
        )

        if delete:
            delete_ok = self._identity_api.delete_project(
                cloud_account=cloud_account, project_identifier=project_identifier
            )
            # Currently, we only handle one error, other throws will propagate upwards
            message = f"The following project has been deleted:\n\n{project_string}"
            return delete_ok, message
        return (
            False,
            f"Tick the delete checkbox to delete the project:\n\n{project_string}",
        )

    def project_find(
        self, cloud_account: str, project_identifier: str
    ) -> Tuple[bool, Union[Project, str]]:
        """
        find and return a given project's properties
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or Openstack ID
        :return: status , Project object or error string
        """
        project = self._identity_api.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        output = project if project else "The project could not be found."
        return bool(project), output

    # pylint:disable=too-many-arguments
    def project_create(
        self,
        cloud_account: str,
        name: str,
        email: str,
        description: str,
        is_enabled: bool,
        immutable: bool,
        parent_id: str,
    ) -> Tuple[bool, Optional[Project]]:
        """
        Find and return a given project's properties. Expected
        to be called within a workflow and not directly
        :param cloud_account: The account from the clouds configuration to use
        :param name: Name of new project
        :param email: Contact email of new project
        :param description: Description for new project
        :param is_enabled: Set if new project enabled or disabled
        :param immutable: Set if new project is immutable or not
        :param parent_id: Set if new project has a parent id other than Default
        :return: status, optional project
        """
        details = ProjectDetails(
            name=name,
            email=email,
            description=description,
            is_enabled=is_enabled,
            immutable=immutable,
            parent_id=parent_id or None,
        )
        project = self._identity_api.create_project(
            cloud_account=cloud_account, project_details=details
        )
        return bool(project), project

    # pylint:disable=too-many-arguments
    def project_list(
        self,
        cloud_account: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        return_html: bool,
        **kwargs,
    ) -> str:
        """
        Finds all projects that match a particular query
        :param cloud_account: The account from the clouds configuration to use
        :param query_preset: The query to use when searching for projects
        :param properties_to_select: The list of properties to select and output from the found projects
        :param group_by: Property to group returned results - can be empty for no grouping
        :param return_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        return self._project_api.search(
            cloud_account=cloud_account,
            query_params=QueryParams(
                query_preset=query_preset,
                properties_to_select=properties_to_select,
                group_by=group_by,
                return_html=return_html,
            ),
            **kwargs,
        )

    def project_update(
        self,
        cloud_account: str,
        project_identifier: str,
        name: str,
        email: str,
        description: str,
        is_enabled: str,
        immutable: str,
    ) -> Tuple[bool, Optional[Project]]:
        """
        Find and update a given project's properties.
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or Openstack ID of the project to update
        :param name: Name of the project
        :param email: Contact email of the project
        :param description: Description of the project
        :param is_enabled: Enable or disable the project (takes values of unchanged, true or false)
        :param immutable: Make the project immutable or not (takes values of unchanged, true or false)
        :return: status, optional project
        """

        def convert_to_optional_bool(value: str) -> Optional[bool]:
            if value.casefold() == "true".casefold():
                return True
            if value.casefold() == "false".casefold():
                return False
            return None

        details = ProjectDetails(
            name=name,
            email=email,
            description=description,
            is_enabled=convert_to_optional_bool(is_enabled),
            immutable=convert_to_optional_bool(immutable),
        )
        project = self._identity_api.update_project(
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            project_details=details,
        )
        return bool(project), project
