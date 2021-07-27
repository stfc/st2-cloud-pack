from st2common.runners.base_action import Action
import openstack
from openstack_action import OpenstackAction

class Quote(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """ constructor class """
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "quota_set": self.quota_set
        }

    def quota_set(self, **kwargs):
        """
        Set a project's quota
        :param kwargs: project (String): ID or Name, (other_args - see action definition yaml file for details)
        :return: (status (Bool), reason (String))
        """

        new_kwargs = {k:v for k, v in kwargs.items() if k not in ["project"]}

        #get project id
        project_id = self.find_resource_id(kwargs["project"], self.conn.identity.find_project)
        if not project_id:
            return False, "Project not found with Name or ID {}".format(kwargs["project"])

        try:
            quota = self.conn.network.update_quota(quota=project_id, **new_kwargs)
        except Exception as e:
            return False, "Quota update failed {}".format(e)
        return True, quota
