from openstack_query.queries.query_wrapper import QueryWrapper
from enums.query.server_properties import ServerProperties
from openstack_query.runners.server_runner import ServerRunner

from openstack_query.utils import convert_to_timestamp

from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsDateTime,
    QueryPresetsString,
)

from openstack_query.handlers.presets.preset_handler_generic import PresetHandlerGeneric
from openstack_query.handlers.presets.preset_handler_string import PresetHandlerString
from openstack_query.handlers.presets.preset_handler_datetime import (
    PresetHandlerDateTime,
)

from openstack_query.handlers.kwarg_handler import KwargHandler
from openstack_query.handlers.prop_handler import PropHandler


class QueryServer(QueryWrapper):
    # PROPERTY_MAPPINGS set how to get properties of a openstack server object
    # possible properties are documented here:
    # https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/server.html#openstack.compute.v2.server.Server
    _PROPERTY_MAPPINGS = {
        ServerProperties.USER_ID: lambda a: a["user_id"],
        ServerProperties.HYPERVISOR_ID: lambda a: a["host_id"],
        ServerProperties.SERVER_ID: lambda a: a["id"],
        ServerProperties.SERVER_NAME: lambda a: a["name"],
        ServerProperties.SERVER_DESCRIPTION: lambda a: a["description"],
        ServerProperties.SERVER_STATUS: lambda a: a["status"],
        ServerProperties.SERVER_CREATION_DATE: lambda a: a["created_at"],
        ServerProperties.SERVER_LAST_UPDATED_DATE: lambda a: a["updated_at"],
        ServerProperties.FLAVOR_ID: lambda a: ["flavor_id"],
        ServerProperties.IMAGE_ID: lambda a: ["image_id"],
        ServerProperties.PROJECT_ID: lambda a: a["location"]["project"]["id"],
    }

    # KWARG_MAPPINGS - 'filter' keyword arguments that openstack command conn.compute.servers() takes
    # - documented here https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
    # - all filters are documented here
    # https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#list-server-request
    _KWARG_MAPPINGS = {
        QueryPresetsGeneric.EQUAL_TO: {
            ServerProperties.USER_ID: lambda **kwargs: {"user_id": kwargs["value"]},
            ServerProperties.SERVER_ID: lambda **kwargs: {"uuid": kwargs["value"]},
            ServerProperties.SERVER_NAME: lambda **kwargs: {
                "hostname": kwargs["value"]
            },
            ServerProperties.SERVER_DESCRIPTION: lambda **kwargs: {
                "description": kwargs["value"]
            },
            ServerProperties.SERVER_STATUS: lambda **kwargs: {
                "vm_state": kwargs["value"]
            },
            ServerProperties.SERVER_CREATION_DATE: lambda **kwargs: {
                "created_at": kwargs["value"]
            },
            ServerProperties.FLAVOR_ID: lambda **kwargs: {"flavor": kwargs["value"]},
            ServerProperties.IMAGE_ID: lambda **kwargs: {"image": kwargs["value"]},
            ServerProperties.PROJECT_ID: lambda **kwargs: {
                "project_id": kwargs["value"]
            },
        },
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: {
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                "changes-before": convert_to_timestamp(**kwargs)
            }
        },
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: {
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                "changes-since": convert_to_timestamp(**kwargs)
            }
        },
    }

    FILTER_FUNCTION_MAPPING_GENERIC = {
        QueryPresetsGeneric.EQUAL_TO: ["*"],
        QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
    }

    FILTER_FUNCTION_MAPPING_DATETIME = {
        QueryPresetsDateTime.OLDER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsDateTime.YOUNGER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
    }

    FILTER_FUNCTION_MAPPING_STRING = {
        QueryPresetsString.MATCHES_REGEX: [ServerProperties.SERVER_NAME],
    }

    def __init__(self):
        preset_handlers = [
            PresetHandlerGeneric(self.FILTER_FUNCTION_MAPPING_GENERIC),
            PresetHandlerDateTime(self.FILTER_FUNCTION_MAPPING_DATETIME),
            PresetHandlerString(self.FILTER_FUNCTION_MAPPING_STRING),
        ]
        kwarg_handler = KwargHandler(self._KWARG_MAPPINGS)
        prop_handler = PropHandler(self._PROPERTY_MAPPINGS)

        super().__init__(prop_handler, preset_handlers, kwarg_handler)
        self.runner = ServerRunner()
