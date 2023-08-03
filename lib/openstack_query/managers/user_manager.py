from custom_types.openstack_query.aliases import QueryReturn

from enums.query.props.user_properties import UserProperties
from enums.cloud_domains import CloudDomains

from openstack_query.queries.user_query import UserQuery
from openstack_query.managers.query_manager import QueryManager


from exceptions.parse_query_error import ParseQueryError


class UserManager(QueryManager):
    """
    Manager for querying Openstack user objects.
    """

    def __init__(self, cloud_account: CloudDomains):
        QueryManager.__init__(
            self,
            query=UserQuery(),
            cloud_account=cloud_account,
            prop_cls=UserProperties,
        )

    def search_by_datetime(
        self,
        search_mode: str,
        property_to_search_by: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        **kwargs,
    ) -> QueryReturn:
        """
        Method to search by datetime.
        For querying users this will raise an error as this is not possible
        """
        raise ParseQueryError("Cannot query by datatime with users")
