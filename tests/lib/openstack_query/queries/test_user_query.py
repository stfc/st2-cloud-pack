import unittest


from openstack_query.queries.user_query import UserQuery
from enums.query.props.user_properties import UserProperties

# pylint:disable=protected-access


class TestServerQuery(unittest.TestCase):
    """
    Runs various tests to ensure that ServerQuery functions expectedly.
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.instance = UserQuery()

    def test_get_prop_handler(self):
        """
        Tests that all user properties have a property function mapping
        """
        prop_handler = self.instance._get_prop_handler()

        for prop in UserProperties:
            prop_handler.check_supported(prop)

