from st2common.runners.base_action import Action
import openstack
from openstack_action import OpenstackAction

class Network(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """ constructor class """
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "network_rbac_create": self.network_rbac_create,
            "network_create": self.network_create
        }

    def network_create(self, **kwargs):
        """
        Create a Network for a project
        :param kwargs: project (String): ID or Name, (other_args - see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """
        new_kwargs = {k:v for k, v in kwargs.items() if k not in ["project"]}

        #get project id
        project_id = self.find_resource_id(kwargs["project"], self.conn.identity.find_project)
        if not project_id:
            return False, "Project Not Found"

        try:
            network = self.conn.network.create_network(project_id=project_id, **new_kwargs)
        except Exception as e:
            return False, "Network Creation Failed: {}".format(e)
        return True, network


    def network_rbac_create(self, **kwargs):
        """
        Create RBAC rules
        :param kwargs: object_type (String): rbac_object resource type, rbac_object (String): ID or Name,
        target_project (String): ID or Name, (other_args - see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """
        new_kwargs = {k:v for k, v in kwargs.items() if k not in ["rbac_object", "target_project"]}

        # get rbac_object ID
        if kwargs["object_type"].lower() == "network":
            object_id = self.find_resource_id(kwargs["rbac_object"], self.conn.network.find_network)
            if not object_id:
                return False, "No Network Found with Name or ID {}".format(kwargs["rbac_object"])
        else:
            return False, "Currently only allowing network as valid rbac type"

        # get project ID
        target_project_id = self.find_resource_id(kwargs["target_project"], self.conn.identity.find_project)
        if not target_project_id:
            return False, "No Project Found with Name or ID {}".format(kwargs["target_project"])

        try:
            rbac = self.conn.network.create_rbac_policy(object_id=object_id, target_project_id=target_project_id, **new_kwargs)
        except Exception as e:
            return False, "RBAC Policy creation Failed {}".format(e)

        return True, rbac
