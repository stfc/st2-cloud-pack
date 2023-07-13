import unittest
from unittest.mock import MagicMock, patch, NonCallableMock

from openstack_query.managers.server_manager import ServerManager

from enums.query.query_presets import (
    QueryPresetsDateTime,
    QueryPresetsString,
)

from enums.query.props.server_properties import ServerProperties

from structs.query.query_preset_details import QueryPresetDetails
from tests.lib.openstack_query.mocks.mocked_structs import MOCKED_OUTPUT_DETAILS

# pylint:disable=protected-access,


@patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
class ServerManagerTests(unittest.TestCase):
    """
    Runs various tests to ensure that ServerManager class methods function expectedly
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()

        self.query = MagicMock()
        self.instance = ServerManager(cloud_account="test_account")
        self.instance._query = self.query

    def test_search_all_servers(self, mock_build_and_run_query):
        """
        Tests that search_all_servers method functions expectedly
        Runs a query to get all servers, returns query results
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        res = self.instance.search_all_servers(MOCKED_OUTPUT_DETAILS)
        mock_build_and_run_query.assert_called_once_with(
            preset_details=None, output_details=MOCKED_OUTPUT_DETAILS
        )
        self.assertEqual(res, mock_query_return)

    def test_search_servers_older_than_relative_to_now(self, mock_build_and_run_query):
        """
        Tests that search_servers_older_than_relative_to_now method functions expectedly
        Runs a query to get all servers older than a relative time (e.g. older than 60 days)
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        res = self.instance.search_servers_older_than_relative_to_now(
            MOCKED_OUTPUT_DETAILS, days=10, hours=10, minutes=1
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.OLDER_THAN,
                prop=ServerProperties.SERVER_CREATION_DATE,
                args={
                    "days": 10,
                    "hours": 10,
                    "minutes": 1,
                    "seconds": 0,
                },
            ),
            output_details=MOCKED_OUTPUT_DETAILS,
        )
        self.assertEqual(res, mock_query_return)

    def test_search_servers_younger_than_relative_to_now(
        self, mock_build_and_run_query
    ):
        """
        Tests that search_servers_younger_than_relative_to_now method functions expectedly
        Runs a query to get all servers younger than a relative time (e.g. younger than 60 days)
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        res = self.instance.search_servers_younger_than_relative_to_now(
            MOCKED_OUTPUT_DETAILS, days=10, hours=10, minutes=1
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.YOUNGER_THAN,
                prop=ServerProperties.SERVER_CREATION_DATE,
                args={
                    "days": 10,
                    "hours": 10,
                    "minutes": 1,
                    "seconds": 0,
                },
            ),
            output_details=MOCKED_OUTPUT_DETAILS,
        )
        self.assertEqual(res, mock_query_return)

    def test_search_servers_last_updated_before_relative_to_now(
        self, mock_build_and_run_query
    ):
        """
        Tests that search_servers_last_updated_before_relative_to_now method functions expectedly
        Runs a query to get all servers that have had their last status changed before than a relative time
        (e.g. days=60 => 60 days ago or older)
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        res = self.instance.search_servers_last_updated_before_relative_to_now(
            MOCKED_OUTPUT_DETAILS, days=10, hours=10, minutes=1
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.OLDER_THAN,
                prop=ServerProperties.SERVER_LAST_UPDATED_DATE,
                args={
                    "days": 10,
                    "hours": 10,
                    "minutes": 1,
                    "seconds": 0,
                },
            ),
            output_details=MOCKED_OUTPUT_DETAILS,
        )
        self.assertEqual(res, mock_query_return)

    def test_search_servers_last_updated_after_relative_to_now(
        self, mock_build_and_run_query
    ):
        """
        Tests that search_servers_last_updated_after_relative_to_now method functions expectedly
        Runs a query to get all servers that have had their last status changed after than a relative time
        (e.g. days=60 => 60 days ago or earlier)
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        res = self.instance.search_servers_last_updated_after_relative_to_now(
            MOCKED_OUTPUT_DETAILS, days=10, hours=10, minutes=1
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.YOUNGER_THAN,
                prop=ServerProperties.SERVER_LAST_UPDATED_DATE,
                args={
                    "days": 10,
                    "hours": 10,
                    "minutes": 1,
                    "seconds": 0,
                },
            ),
            output_details=MOCKED_OUTPUT_DETAILS,
        )
        self.assertEqual(res, mock_query_return)

    def test_search_servers_name_in(self, mock_build_and_run_query):
        """
        Tests that search_servers_name_in method functions expectedly
        Runs a query to get all servers that match a given list of names
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return
        res = self.instance.search_servers_name_in(
            MOCKED_OUTPUT_DETAILS, names=["name1", "name2"]
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.ANY_IN,
                prop=ServerProperties.SERVER_NAME,
                args={"values": ["name1", "name2"]},
            ),
            output_details=MOCKED_OUTPUT_DETAILS,
        )
        self.assertEqual(res, mock_query_return)

    def test_search_servers_name_not_in(self, mock_build_and_run_query):
        """
        Tests that search_servers_name_not_in method functions expectedly
        Runs a query to get all servers that don't match a given list of names
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        res = self.instance.search_servers_name_not_in(
            MOCKED_OUTPUT_DETAILS, names=["name1", "name2"]
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.NOT_ANY_IN,
                prop=ServerProperties.SERVER_NAME,
                args={"values": ["name1", "name2"]},
            ),
            output_details=MOCKED_OUTPUT_DETAILS,
        )
        self.assertEqual(res, mock_query_return)
