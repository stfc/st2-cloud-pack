import logging

from enums.query.props.user_properties import UserProperties
from enums.cloud_domains import CloudDomains

from openstack_query.api.query_objects import UserQuery
from openstack_query.managers.manager_wrapper import ManagerWrapper

from exceptions.parse_query_error import ParseQueryError


logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class UserManager(ManagerWrapper):
    """
    Manager for querying Openstack user objects.
    """

    def __init__(self, cloud_account: CloudDomains):
        ManagerWrapper.__init__(
            self,
            query=UserQuery(),
            cloud_account=cloud_account,
            prop_cls=UserProperties,
        )

    def search_by_datetime(self, **_) -> None:
        """
        Method to search by datetime.
        For querying users this will raise an error as this is not possible
        """
        logger.error(
            "Search by datetime is not possible for User queries as Users don't have a datetime property"
        )
        raise ParseQueryError("Cannot query by datatime with users")
