from typing import Tuple, Optional, Dict, Callable

from openstack.identity.v3.project import Project

from openstack_api.openstack_identity import OpenstackIdentity

from structs.project_details import ProjectDetails
from st2common.runners.base_action import Action


class ProjectAction(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        # DI handled in OpenstackActionTestCase
        super().__init__(*args, config=config, **kwargs)
        self._identity_api: OpenstackIdentity = config.get(
            "openstack_identity_api", OpenstackIdentity()
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
        project_string = {k: project[k] for k in ["id", "name", "description", "email"]}

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
