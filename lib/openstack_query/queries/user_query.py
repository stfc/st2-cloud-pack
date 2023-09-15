from typing import Type

from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsString,
)
from openstack_query.handlers.server_side_handler import ServerSideHandler


from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString

from openstack_query.queries.query_wrapper import QueryWrapper
from openstack_query.runners.user_runner import UserRunner


class UserQuery(QueryWrapper):
    """
    Query class for querying Openstack User objects.
    Define property mappings, kwarg mappings and filter function mappings related to users here
    """

    @property
    def prop_mapping(self) -> Type[UserProperties]:
        """
        Property enum class for users
        """
        return UserProperties

    @property
    def query_runner(self) -> UserRunner:
        """
        Constructs a QueryRunner class for users
        """
        return UserRunner(self.prop_mapping)

    def _get_server_side_handler(self) -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.servers() to filter results for a valid preset-property pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
            https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#list-server-request
        """
        return ServerSideHandler(
            {
                QueryPresetsGeneric.EQUAL_TO: {
                    UserProperties.USER_DOMAIN_ID: lambda value: {"domain_id": value},
                    UserProperties.USER_NAME: lambda value: {"name": value},
                }
            }
        )

    def _get_client_side_handlers(self) -> QueryClientSideHandlers:
        """
        method to configure a set of client-side handlers which can be used to get local filter functions
        corresponding to valid preset-property pairs. These filter functions can be used to filter results after
        listing all servers.
        """
        return QueryClientSideHandlers(
            # set generic query preset mappings
            generic_handler=ClientSideHandlerGeneric(
                {
                    QueryPresetsGeneric.EQUAL_TO: ["*"],
                    QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
                }
            ),
            # set string query preset mappings
            string_handler=ClientSideHandlerString(
                {
                    QueryPresetsString.MATCHES_REGEX: [
                        UserProperties.USER_EMAIL,
                        UserProperties.USER_NAME,
                    ]
                }
            ),
            # set datetime query preset mappings
            datetime_handler=None,
            # set integer query preset mappings
            integer_handler=None,
        )
