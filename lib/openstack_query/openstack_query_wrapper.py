from enum import Enum
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_connection import OpenstackConnection


class OpenstackQueryWrapper(OpenstackWrapperBase):

    def __init__(self, connection_cls=OpenstackConnection):

        OpenstackWrapperBase.__init__(self, connection_cls)

    def select(self, *props: Enum):
        """
        Public method used to 'select' properties that the query will return the value of.
        Mutually exclusive to returning objects using select_all()
        :param props: one or more properties to collect described as enum
        """

        # should be a idempotent function
        # calling multiple times with should aggregate properties to select
        raise NotImplementedError

    def select_all(self):
        """
        Public method used to 'select' all properties that are available to be returned
        Mutually exclusive to returning objects using select_all()

        Overrides all currently selected properties
        returns list of properties currently selected
        """
        raise NotImplementedError

    def where(self, preset: Enum, **kwargs):
        """
        Public method used to set the preset that will be used to get the query filter function
        :param preset: Name of preset to use
        :param kwargs: kwargs to pass to preset
        """
        raise NotImplementedError

    def sort_by(self, sort_by: Enum, reverse=False):
        """
        Public method used to configure sorting results
        :param sort_by: name of property to sort by
        :param reverse: False is sort by ascending, True is sort by descending, default False
        """
        raise NotImplementedError

    def group_by(self, group_by: Enum):
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        """
        raise NotImplementedError

    def run(self, cloud_account: str, **kwargs):
        """
        Public method that runs the query provided that it has been configured properly
        :param cloud_account: The account from the clouds configuration to use
        :param kwargs: keyword args that can be used to configure details of how query is run
            - valid kwargs specific to resource
        """
        raise NotImplementedError

    @staticmethod
    def _run_query(self, conn: OpenstackConnection, **kwargs):
        """
        This method is to be instantiated in subclasses of this class to run openstack query command
        """
        raise NotImplementedError("""
            This static method should be implemented in subclasses of OpenstackQueryWrapper to 
            run the appropriate openstack command(s)
        """)
