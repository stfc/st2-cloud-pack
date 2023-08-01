from typing import List
import re
from custom_types.openstack_query.aliases import QueryReturn

from enums.query.query_presets import (
    QueryPresetsDateTime,
    QueryPresetsString,
    QueryPresetsGeneric,
)
from enums.query.props.server_properties import ServerProperties
from enums.cloud_domains import CloudDomains

from openstack_query.queries.server_query import ServerQuery
from openstack_query.managers.query_manager import QueryManager

from structs.query.query_preset_details import QueryPresetDetails
from structs.query.query_output_details import QueryOutputDetails

# pylint:disable=too-many-arguments


class ServerManager(QueryManager):
    """
    Manager for querying Openstack Server objects.
    """

    def __init__(self, cloud_account: CloudDomains):
        QueryManager.__init__(
            self,
            query=ServerQuery(),
            cloud_account=cloud_account,
            prop_cls=ServerProperties(),
        )
