from enums.query.props.server_properties import ServerProperties
from enums.cloud_domains import CloudDomains

from openstack_query.queries.server_query import ServerQuery
from openstack_query.managers.manager_wrapper import ManagerWrapper

# pylint:disable=too-few-public-methods


class ServerManager(ManagerWrapper):
    """
    Manager for querying Openstack Server objects.
    """

    def __init__(self, cloud_account: CloudDomains):
        ManagerWrapper.__init__(
            self,
            query=ServerQuery(),
            cloud_account=cloud_account,
            prop_cls=ServerProperties,
        )
