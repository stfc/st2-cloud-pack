from typing import Dict
from openstack_api.openstack_connection import OpenstackConnection

from openstack_api.openstack_wrapper_base import OpenstackWrapperBase

from st2common.runners.base_action import Action


class OpenstackAction(Action, OpenstackWrapperBase):
    def __init__(
        self, config=None, action_service=None, connection_cls=OpenstackConnection
    ):
        Action.__init__(self, config, action_service)
        OpenstackWrapperBase.__init__(self, connection_cls)

        self.conn = None
        # Abstract method
        self.func: Dict

    def run(self, **kwargs):
        """
        function that is run openstack_resource stackstorm when an action is invoked
        :param kwargs: arguments for openstack actions
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        self.conn = self._connection_cls(kwargs["cloud_account"])

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
