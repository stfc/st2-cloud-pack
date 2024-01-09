from typing import Type

from enums.query.props.image_properties import ImageProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsDateTime,
    QueryPresetsInteger,
    QueryPresetsString,
)
from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)
from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from openstack_query.handlers.server_side_handler import ServerSideHandler

from openstack_query.mappings.mapping_interface import MappingInterface
from openstack_query.runners.image_runner import ImageRunner
from openstack_query.time_utils import TimeUtils
from structs.query.query_client_side_handlers import QueryClientSideHandlers


class ImageMapping(MappingInterface):
    """
    Mapping class for querying Openstack Image objects.
    Define property mappings, kwarg mappings and filter function mappings, and runner mapping related to images here
    """

    @staticmethod
    def get_chain_mappings():
        """
        Return a dictionary containing property pairs mapped to query mappings.
        This is used to define how to chain results from this query to other possible queries
        """
        return {ImageProperties.IMAGE_ID: ServerProperties.SERVER_ID}

    @staticmethod
    def get_runner_mapping() -> Type[ImageRunner]:
        """
        Returns a mapping to associated Runner class for the Query (ImageRunner)
        """
        return ImageRunner

    @staticmethod
    def get_prop_mapping() -> Type[ImageProperties]:
        """
        Returns a mapping of valid presets for server side attributes (ImageProperties)
        """
        return ImageProperties

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.images() to filter results for a valid preset-property pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
            https://docs.openstack.org/api-ref/image/v2/index.html#list-images
        """
        return ServerSideHandler(
            {
                QueryPresetsGeneric.EQUAL_TO: {
                    ImageProperties.IMAGE_NAME: lambda value: {"name": value},
                    ImageProperties.IMAGE_STATUS: lambda value: {"status": value},
                },
                QueryPresetsGeneric.ANY_IN: {
                    ImageProperties.IMAGE_NAME: lambda values: [
                        {"name": value} for value in values
                    ],
                    ImageProperties.IMAGE_STATUS: lambda values: [
                        {"status": value} for value in values
                    ],
                },
                QueryPresetsDateTime.OLDER_THAN: {
                    ImageProperties.IMAGE_CREATION_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "created_at": f"lt:{func(**kwargs)}"
                    },
                    ImageProperties.IMAGE_LAST_UPDATED_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "updated_at": f"lt:{func(**kwargs)}"
                    },
                },
                QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: {
                    ImageProperties.IMAGE_CREATION_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "created_at": f"lte:{func(**kwargs)}"
                    },
                    ImageProperties.IMAGE_LAST_UPDATED_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "updated_at": f"lte:{func(**kwargs)}"
                    },
                },
                QueryPresetsDateTime.YOUNGER_THAN: {
                    ImageProperties.IMAGE_CREATION_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "created_at": f"gt:{func(**kwargs)}"
                    },
                    ImageProperties.IMAGE_LAST_UPDATED_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "updated_at": f"gt:{func(**kwargs)}"
                    },
                },
                QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: {
                    ImageProperties.IMAGE_CREATION_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "created_at": f"gte:{func(**kwargs)}"
                    },
                    ImageProperties.IMAGE_LAST_UPDATED_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "updated_at": f"gte:{func(**kwargs)}"
                    },
                },
                QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: {
                    ImageProperties.IMAGE_SIZE: lambda value: {"size_min": int(value)}
                },
                QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: {
                    ImageProperties.IMAGE_SIZE: lambda value: {"size_max": int(value)}
                },
            }
        )

    @staticmethod
    def get_client_side_handlers() -> QueryClientSideHandlers:
        """
        method to configure a set of client-side handlers which can be used to get local filter functions
        corresponding to valid preset-property pairs. These filter functions can be used to filter results after
        listing all servers.
        """
        integer_prop_list = [
            ImageProperties.IMAGE_SIZE,
            ImageProperties.IMAGE_MINIMUM_RAM,
            ImageProperties.IMAGE_MINIMUM_DISK,
            ImageProperties.IMAGE_CREATION_PROGRESS,
        ]
        date_prop_list = [
            ImageProperties.IMAGE_CREATION_DATE,
            ImageProperties.IMAGE_LAST_UPDATED_DATE,
        ]

        return QueryClientSideHandlers(
            # set generic query preset mappings
            generic_handler=ClientSideHandlerGeneric(
                {
                    QueryPresetsGeneric.EQUAL_TO: ["*"],
                    QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
                    QueryPresetsGeneric.ANY_IN: ["*"],
                    QueryPresetsGeneric.NOT_ANY_IN: ["*"],
                }
            ),
            # set string query preset mappings
            string_handler=ClientSideHandlerString(
                {QueryPresetsString.MATCHES_REGEX: [ImageProperties.IMAGE_NAME]}
            ),
            # set datetime query preset mappings
            datetime_handler=ClientSideHandlerDateTime(
                {
                    QueryPresetsDateTime.YOUNGER_THAN: date_prop_list,
                    QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: date_prop_list,
                    QueryPresetsDateTime.OLDER_THAN: date_prop_list,
                    QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: date_prop_list,
                }
            ),
            # set integer query preset mappings
            integer_handler=ClientSideHandlerInteger(
                {
                    QueryPresetsInteger.LESS_THAN: integer_prop_list,
                    QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: integer_prop_list,
                    QueryPresetsInteger.GREATER_THAN: integer_prop_list,
                    QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: integer_prop_list,
                }
            ),
        )
