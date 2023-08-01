from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsString,
)
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.handlers.prop_handler import PropHandler


from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString

from openstack_query.queries.query_wrapper import QueryWrapper
from openstack_query.runners.user_runner import UserRunner

from openstack_query.time_utils import TimeUtils

# pylint:disable=too-few-public-methods


class UserQuery(QueryWrapper):
    """
    Query class for querying Openstack User objects.
    Define property mappings, kwarg mappings and filter function mappings related to users here
    """

    def _get_prop_handler(self) -> PropHandler:
        """
        method to configure a property handler which can be used to get any valid property of a openstack User object
        valid properties are documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/identity/v3/user.html#openstack.identity.v3.user.User

        """
        return PropHandler(
            {
                UserProperties.USER_DOMAIN_ID: lambda a: a["domain_id"],
                UserProperties.USER_DESCRIPTION: lambda a: a["description"],
                UserProperties.USER_EMAIL: lambda a: a["email"],
                UserProperties.USER_NAME: lambda a: a["name"],
            }
        )

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
                    UserProperties.DOMAIN_ID: lambda value: {"domain_id": value},
                    UserProperties.NAME: lambda value: {"name": value},
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

    def __init__(self):
        super().__init__(runner=UserRunner())
