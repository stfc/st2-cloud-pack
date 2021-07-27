from st2common.runners.base_action import Action
import openstack
from openstack_action import OpenstackAction

class Role(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """ constructor class """
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "role_add": self.role_add
        }

    def role_add(self, **kwargs):
        """
        Add User Role to Project
        :param kwargs: role (String): Name or ID, project (String): Name or ID, user_domain (String): Name or ID,
        user (String): Name or ID
        :return: (status (Bool), reason (String))
        """

        # get role id
        role_id = self.find_resource_id(kwargs["role"], self.conn.identity.find_role)
        if not role_id:
            return False, "Role not found with Name or ID {}".format(kwargs["project"])

        # get project id
        project_id = self.find_resource_id(kwargs["project"], self.conn.identity.find_project)
        if not project_id:
            return False, "Project not found with Name or ID {}".format(kwargs["project"])

        # get user domain id
        user_domain_id = self.find_resource_id(kwargs["user_domain"], self.conn.identity.find_domain)
        if not user_domain_id:
            return False, "No domain found with Name or ID {}".format(kwargs["domain"])

        # get user id
        user_id = self.find_resource_id(kwargs["user"], self.conn.identity.find_user, domain_id=user_domain_id)
        if not user_id:
            return False, "No user found with Name or ID {0}".format(kwargs["user"])

        try:
            role_assignment = self.conn.identity.assign_project_role_to_user(project_id, user_id, role_id)
        except Exception as e:
            return False, "Role Assignment Failed {}".format(e)
        return True, role_assignment
