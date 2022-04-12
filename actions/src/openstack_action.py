from abc import ABC
from typing import Dict

import openstack

from st2common.runners.base_action import Action


def connect_to_openstack():
    """
    Connect to openstack
    :return: openstack connection object
    """
    return openstack.connect()


class OpenstackAction(Action, ABC):
    def __init__(self, config=None, action_service=None):
        super().__init__(config, action_service)
        self.conn = None
        # Abstract method
        self.func: Dict

    def run(self, **kwargs):
        """
        function that is run openstack_resource stackstorm when an action is invoked
        :param kwargs: arguments for openstack actions
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        self.conn = connect_to_openstack()

        function = self.func.get(kwargs["submodule"])
        return function(
            **{
                k: v
                for k, v in kwargs.items()
                if v not in [None, ["NULL"]] and k not in ["submodule"]
            }
        )

    @staticmethod
    def find_resource_id(identifier, openstack_func, **kwargs):
        """
        helper to find the ID of a openstack resource
        :param identifier: Associated Name of the openstack resource
        :param openstack_func: Openstack function to find the resource
        :param kwargs: Arguments to pass into Openstack function
        :return: (String/None): ID of resource (or None if not found)
        """
        resource = openstack_func(identifier, **kwargs)
        if not resource:
            return None
        return resource.get("id", None)
