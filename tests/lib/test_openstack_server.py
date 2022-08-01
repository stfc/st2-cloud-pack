import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

from openstack_api.openstack_server import OpenstackServer


class OpenstackServerTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Servers module in the expected way
    """

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch("openstack_api.openstack_server.OpenstackIdentity") as identity_mock:
            self.instance = OpenstackServer(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.server_api = (
            self.mocked_connection.return_value.__enter__.return_value.server
        )

        self.mock_server_list = [
            {
                "id": "serverid1",
                "name": "server1",
                "created_at": "2020-06-28T14:00:00Z",
                "updated_at": "2020-06-28T14:00:00Z",
                "status": "SHUTOFF",
            },
            {
                "id": "serverid2",
                "name": "server2",
                "created_at": "2021-04-28T14:00:00Z",
                "updated_at": "2021-06-28T14:00:00Z",
                "status": "ERROR",
            },
            {
                "id": "serverid3",
                "name": "server3",
                "created_at": "2021-06-28T14:00:00Z",
                "updated_at": "2021-06-28T14:00:00Z",
                "status": ["SHUTOFF", "ERROR"],
            },
        ]

    def test_search_all_servers_no_project(self):
        """
        Tests calling search_all_servers with no project selected
        """
        # pylint:disable=too-few-public-methods,invalid-name,redefined-builtin
        class ProjectMock:
            def __init__(self, id):
                self.id = id

        self.identity_module.list_projects.return_value = [
            ProjectMock("ID1"),
            ProjectMock("ID2"),
        ]

        self.instance.search_all_servers(cloud_account="test", project_identifier="")

        self.identity_module.list_projects.assert_called_once_with("test")
        self.mocked_connection.assert_called_once_with("test")

        self.server_api.list_servers.assert_has_calls(
            [
                mock.call(
                    filters={
                        "all_tenants": True,
                        "project_id": "ID1",
                        "limit": 10000,
                    }
                ),
                mock.call(
                    filters={
                        "all_tenants": True,
                        "project_id": "ID2",
                        "limit": 10000,
                    }
                ),
            ],
            any_order=True,
        )

    def test_search_all_servers(self):
        """
        Tests calling search_all_servers
        """
        self.instance.search_all_servers(
            cloud_account="test", project_identifier="project"
        )

        self.identity_module.find_mandatory_project.assert_called_once_with(
            "test", project_identifier="project"
        )
        self.mocked_connection.assert_called_once_with("test")

        self.server_api.list_servers.assert_called_once_with(
            filters={
                "all_tenants": True,
                "project_id": self.identity_module.find_mandatory_project.return_value.id,
                "limit": 10000,
            }
        )

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_servers_older_than(self, mock_datetime):
        """
        Tests calling search_servers_older_than
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_older_than(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_server_list[0], self.mock_server_list[1]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_servers_younger_than(self, mock_datetime):
        """
        Tests calling search_servers_younger_than
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_younger_than(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_server_list[2]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_servers_last_updated_before(self, mock_datetime):
        """
        Tests calling search_servers_last_updated_before
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_last_updated_before(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_server_list[0]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_servers_last_updated_after(self, mock_datetime):
        """
        Tests calling search_servers_last_updated_after
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_last_updated_after(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_server_list[1], self.mock_server_list[2]])

    def test_search_servers_name_in(self):
        """
        Tests calling search_servers_name_in
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_name_in(
            cloud_account="test", project_identifier="", names=["server1", "server2"]
        )

        self.assertEqual(result, [self.mock_server_list[0], self.mock_server_list[1]])

    def test_search_servers_name_not_in(self):
        """
        Tests calling search_servers_name_not_in
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_name_not_in(
            cloud_account="test", project_identifier="", names=["server1", "server2"]
        )

        self.assertEqual(result, [self.mock_server_list[2]])

    def test_search_servers_name_contains(self):
        """
        Tests calling search_servers_name_contains
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["server", "1"]
        )

        self.assertEqual(result, [self.mock_server_list[0]])

        result = self.instance.search_servers_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["1"]
        )

        self.assertEqual(result, [self.mock_server_list[0]])

        result = self.instance.search_servers_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["server"]
        )

        self.assertEqual(result, self.mock_server_list)

    def test_search_servers_name_not_contains(self):
        """
        Tests calling search_servers_name_not_contains
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["server", "1"]
        )

        self.assertEqual(result, [])

        result = self.instance.search_servers_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["1"]
        )

        self.assertEqual(result, [self.mock_server_list[1], self.mock_server_list[2]])

        result = self.instance.search_servers_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["server"]
        )

        self.assertEqual(result, [])

    def test_search_servers_id_in(self):
        """
        Tests calling search_servers_id_in
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_id_in(
            cloud_account="test", project_identifier="", ids=["serverid1", "serverid2"]
        )

        self.assertEqual(result, [self.mock_server_list[0], self.mock_server_list[1]])

    def test_search_servers_id_not_in(self):
        """
        Tests calling search_servers_id_not_in
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_id_not_in(
            cloud_account="test", project_identifier="", ids=["serverid1", "serverid2"]
        )

        self.assertEqual(result, [self.mock_server_list[2]])

    def test_search_servers_errored(self):
        """
        Tests calling search_servers_errored
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_errored(
            cloud_account="test", project_identifier=""
        )

        self.assertEqual(result, [self.mock_server_list[1], self.mock_server_list[2]])

    def test_search_servers_shutoff(self):
        """
        Tests calling search_servers_errored
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_shutoff(
            cloud_account="test", project_identifier=""
        )

        self.assertEqual(result, [self.mock_server_list[0], self.mock_server_list[2]])

    def test_search_servers_errored_and_shutoff(self):
        """
        Tests calling search_servers_errored_and_shutoff
        """

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_errored_and_shutoff(
            cloud_account="test", project_identifier=""
        )

        self.assertEqual(result, [self.mock_server_list[2]])
