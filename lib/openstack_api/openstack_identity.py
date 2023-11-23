from typing import List, Optional, Callable

from openstack.exceptions import ConflictException
from openstack.identity.v3.project import Project
from openstack.identity.v3.user import User

from enums.user_domains import UserDomains
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from structs.project_details import ProjectDetails


class OpenstackIdentity(OpenstackWrapperBase):
    def create_project(
        self, cloud_account: str, project_details: ProjectDetails
    ) -> Optional[Project]:
        """
        Creates a given project with the provided details
        :param cloud_account: The clouds entry to use
        :param project_details: A datastructure containing all the project details
        :return: A clouds project, or None if it was unsuccessful
        """
        # domain_id can be blank, we will create a project in the default domain
        if not project_details.name:
            raise MissingMandatoryParamError("The project name is missing")
        if not project_details.email:
            raise MissingMandatoryParamError("The project contact email is missing")
        if "@" not in project_details.email:
            raise ValueError("The project contact email is invalid")

        create_project_kwargs = {
            "name": project_details.name,
            "description": project_details.description,
            "is_enabled": project_details.is_enabled,
        }
        if project_details.parent_id:
            create_project_kwargs["parent_id"] = project_details.parent_id

        tags = [project_details.email]
        if project_details.immutable:
            tags.append("immutable")
        create_project_kwargs["tags"] = tags

        with self._connection_cls(cloud_account) as conn:
            try:
                return conn.identity.create_project(**create_project_kwargs)
            except ConflictException as err:
                # Strip out frames that are noise by rethrowing
                raise ConflictException(err.message) from err

    def delete_project(self, cloud_account: str, project_identifier: str) -> bool:
        """
        Deletes a project from Openstack default domain
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: True if the project was deleted, False if the operation failed
        """
        project = self.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        if not project:
            return False

        if self.is_project_immutable(project):
            raise ValueError("Project is immutable and so can't be deleted")

        with self._connection_cls(cloud_account) as conn:
            result = conn.identity.delete_project(project=project, ignore_missing=False)
            return result is None  # Where None == success

    def find_mandatory_project(
        self, cloud_account: str, project_identifier: str
    ) -> Project:
        """
        Finds a property or throws a ItemNotFoundError
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: The found project, or raises a ItemNotFoundError
        """
        found = self.find_project(cloud_account, project_identifier)
        if found:
            return found
        raise ItemNotFoundError("The specified project was not found")

    def find_project(
        self, cloud_account: str, project_identifier: str
    ) -> Optional[Project]:
        """
        Finds a project with the given name or ID
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: The found project, or None
        """
        project_identifier = project_identifier.strip()
        if not project_identifier:
            raise MissingMandatoryParamError(
                "A project name or project ID must be provided"
            )

        with self._connection_cls(cloud_account) as conn:
            return conn.identity.find_project(project_identifier, ignore_missing=True)

    def list_projects(self, cloud_account: str) -> List[Project]:
        """
        Lists all projects
        :param cloud_account: The clouds entry to use
        :return: A list of all projects
        """
        with self._connection_cls(cloud_account) as conn:
            return conn.list_projects()

    def find_user(
        self, cloud_account: str, user_identifier: str, user_domain: UserDomains
    ) -> Optional[User]:
        """
        Finds a user with the given name or ID
        :param cloud_account: The clouds entry to use
        :param user_identifier: The name or Openstack ID for the user
        :param user_domain: The domain to search for the user in
        :return: The found user, or None
        """
        user_identifier = user_identifier.strip()
        if not user_identifier:
            raise MissingMandatoryParamError("A user name or ID must be provided")

        domain = user_domain.value.lower().strip()
        if not domain:
            raise MissingMandatoryParamError("A domain name or ID must be provided")

        with self._connection_cls(cloud_account) as conn:
            domain_id = conn.identity.find_domain(domain, ignore_missing=False)

            return conn.identity.find_user(
                user_identifier, domain_id=domain_id.id, ignore_missing=True
            )

    def find_user_all_domains(
        self, cloud_account: str, user_identifier: str
    ) -> Optional[User]:
        """
        Finds a user with the given name or ID
        :param cloud_account: The clouds entry to use
        :param user_identifier: The name or Openstack ID for the user
        :return: The found user, or None
        """
        user_identifier = user_identifier.strip()
        if not user_identifier:
            raise MissingMandatoryParamError("A user name or ID must be provided")

        with self._connection_cls(cloud_account) as conn:
            return conn.identity.find_user(user_identifier, ignore_missing=True)

    def _find_project_tag_index(
        self, project_tags: List[str], select_func: Callable[[str], bool]
    ) -> Optional[int]:
        """
        Returns the index of a project tag matching a given query
        :param project_tags: The project tags
        :param select_func: Function that determines whether a tag should be selected
        :return: The index of found tag or None
        """
        for i, project_tag in enumerate(project_tags):
            if select_func(project_tag):
                return i
        return None

    def find_project_tag(
        self, project_tags: List[str], select_func: Callable[[str], bool]
    ) -> Optional[str]:
        """
        Returns the index of a project tag matching a given query
        :param project_tags: The project tags
        :param select_func: Function that determines whether a tag should be selected
        :return: The tag found or None
        """
        tag_index = self._find_project_tag_index(project_tags, select_func)
        if tag_index is not None:
            return project_tags[tag_index]
        return None

    def update_project_tag(
        self,
        project_tags: List[str],
        select_func: Callable[[str], bool],
        new_value: Optional[str],
    ) -> List[str]:
        """
        Returns an updated list of project tags after adding or updating one
        :param project_tags: The project tags
        :param select_func: Function that determines whether a tag should be selected
        :param new_value: New value of the tag, if None will remove the tag completely
        :return: The index of found tag or None
        """
        tag_index = self._find_project_tag_index(project_tags, select_func)
        if tag_index is not None:
            if new_value is not None:
                project_tags[tag_index] = new_value
            else:
                del project_tags[tag_index]
        else:
            project_tags.append(new_value)
        return project_tags

    def _select_project_email(self, tag) -> bool:
        return "@" in tag

    def _select_project_immutable(self, tag) -> bool:
        return tag == "immutable"

    def get_project_email(self, project: Project) -> Optional[str]:
        """
        Returns the contact email of a project
        :param project: The project to obtain the email from
        :return: The found email or None
        """
        return self.find_project_tag(project["tags"], self._select_project_email)

    def is_project_immutable(self, project: Project) -> bool:
        """
        Returns whether a given project is immutable or not
        :param project: The project to check
        :return: Whether the project is immutable
        """
        return (
            self.find_project_tag(project["tags"], self._select_project_immutable)
            == "immutable"
        )

    def find_project_email(
        self, cloud_account: str, project_identifier: str
    ) -> Optional[str]:
        """
        Returns the contact email of a project
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: The found email or None
        """
        found_email = None
        project = self.find_project(cloud_account, project_identifier)
        if project:
            found_email = self.get_project_email(project)
        return found_email

    def update_project(
        self,
        cloud_account: str,
        project_identifier: str,
        project_details: ProjectDetails,
    ):
        """
        Creates a given project with the provided details
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :param project_details: A datastructure containing all the new project details
        :return: A clouds project, or None if it was unsuccessful
        """
        project = self.find_mandatory_project(cloud_account, project_identifier)
        project_tags = project["tags"]
        project_immutable = self.is_project_immutable(project)

        params_to_update = {}
        if project_details.name:
            params_to_update.update({"name": project_details.name})
        if project_details.description:
            params_to_update.update({"description": project_details.description})
        if project_details.is_enabled is not None:
            params_to_update.update({"is_enabled": project_details.is_enabled})
        if project_details.email:
            if "@" not in project_details.email:
                raise ValueError("The project contact email is invalid")

            project_tags = self.update_project_tag(
                project_tags, self._select_project_email, project_details.email
            )
            params_to_update.update({"tags": project_tags})
        if project_details.immutable is not None:
            project_tags = self.update_project_tag(
                project_tags,
                self._select_project_immutable,
                "immutable" if project_details.immutable else None,
            )
            params_to_update.update({"tags": project_tags})

        if project_immutable:
            # Ensure only change is to the immutability
            if params_to_update.keys() != {"tags"}:
                raise ValueError(
                    "The project is immutable and so only the immutability can be changed"
                )

        with self._connection_cls(cloud_account) as conn:
            # This update_project does not currently update tags for some reason
            # have to use project.set_tags instead
            if "tags" in params_to_update:
                project.set_tags(conn.identity, params_to_update["tags"])

            return conn.identity.update_project(
                project=project,
                **params_to_update,
            )
