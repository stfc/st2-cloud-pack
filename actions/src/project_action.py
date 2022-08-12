from typing import Tuple, Optional, Dict, Callable, Union

from openstack.identity.v3.project import Project

from openstack_api.openstack_identity import OpenstackIdentity
from structs.project_details import ProjectDetails
from st2common.runners.base_action import Action


class ProjectAction(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        # DI handled in OpenstackActionTestCase
        super().__init__(*args, config=config, **kwargs)
        self._api: OpenstackIdentity = config.get("openstack_api", OpenstackIdentity())

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
        self, cloud_account: str, project_identifier: str
    ) -> Tuple[bool, str]:
        """
        Deletes a project
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: (Either) The project name to delete
        :return: The result of the operation
        """
        delete_ok = self._api.delete_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        # Currently, we only handle one error, other throws will propagate upwards
        err = "" if delete_ok else "The specified project was not found"
        return delete_ok, err

    def project_find(
        self, cloud_account: str, project_identifier: str
    ) -> Tuple[bool, Union[Project, str]]:
        """
        find and return a given project's properties
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or Openstack ID
        :return: status , Project object or error string
        """
        project = self._api.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        output = project if project else "The project could not be found."
        return bool(project), output

    def project_create(
        self,
        cloud_account: str,
        name: str,
        email: str,
        description: str,
        is_enabled: bool,
    ) -> Tuple[bool, Optional[Project]]:
        """
        Find and return a given project's properties. Expected
        to be called within a workflow and not directly
        :param cloud_account: The account from the clouds configuration to use
        :param name: Name of new project
        :param email: Contact email of new project
        :param description: Description for new project
        :param is_enabled: Set if new project enabled or disabled
        :return: status, optional project
        """
        details = ProjectDetails(
            name=name, email=email, description=description, is_enabled=is_enabled
        )
        project = self._api.create_project(
            cloud_account=cloud_account, project_details=details
        )
        return bool(project), project
