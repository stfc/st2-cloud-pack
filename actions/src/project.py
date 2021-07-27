from st2common.runners.base_action import Action
import openstack
from openstack_action import OpenstackAction

class Project(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """ constructor class """
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "project_show": self.project_show,
            "project_create": self.project_create
        }

    def project_show(self, **kwargs):
        """
        find and return a given project's properties
        :param kwargs: project (String): Name or ID, domain (String): Name or ID
        :return: (status (Bool), reason (String))
        """
        domain_id = self.find_resource_id(kwargs["domain"], self.conn.identity.find_domain)
        if not domain_id:
            return False, "No domain found with Name or ID {}".format(kwargs["domain"])
        try:
            project = self.conn.identity.find_project(kwargs["project"], domain_id=domain_id)
        except Exception as e:
            return (False, "Finding Project Failed {}".format(e))
        return True, project

    def project_create(self, **kwargs):
        """
        find and return a given project's properties
        :param kwargs: domain (String): Name or ID,  (other_args - see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """
        new_kwargs = {k:v for k, v in kwargs.items() if k not in ["domain"]}

        domain_id = self.find_resource_id(kwargs["domain"], self.conn.identity.find_domain)
        if not domain_id:
            return False, "No domain found with Name or ID {}".format(kwargs["domain"])
        try:
            project = self.conn.identity.create_project(domain_id=domain_id, **new_kwargs)
        except Exception as e:
            return False, "Project Creation Failed {}".format(e)
        return True, project
