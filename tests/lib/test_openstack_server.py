import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

import openstack
from openstack.exceptions import HttpException

from openstack_api.openstack_server import OpenstackServer

# pylint:disable=too-many-public-methods
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

        self.api = self.mocked_connection.return_value.__enter__.return_value

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

        self.api.list_servers.assert_has_calls(
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

        self.api.list_servers.assert_called_once_with(
            filters={
                "all_tenants": True,
                "project_id": self.identity_module.find_mandatory_project.return_value.id,
                "limit": 10000,
            }
        )

    def test_search_all_servers_error(self):
        """
        Tests calling search_all_servers handles a HttpException correctly
        """
        self.api.list_servers.side_effect = HttpException()
        self.instance.search_all_servers(
            cloud_account="test", project_identifier="project"
        )

        self.identity_module.find_mandatory_project.assert_called_once_with(
            "test", project_identifier="project"
        )
        self.mocked_connection.assert_called_once_with("test")

        self.api.list_servers.assert_called_once_with(
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

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_servers_shutoff_before(self, mock_datetime):
        """
        Tests calling search_servers_shutoff_before
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_servers = MagicMock()
        self.instance.search_all_servers.return_value = self.mock_server_list

        result = self.instance.search_servers_shutoff_before(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_server_list[0]])

    def test_find_non_existent_servers_no_project(self):
        """
        Tests calling find_non_existent_servers with no project selected
        """
        # pylint:disable=too-few-public-methods,invalid-name,redefined-builtin
        class ObjectMock:
            def __init__(self, id):
                self.id = id

        self.identity_module.list_projects.return_value = [
            ObjectMock("ProjectID1"),
            ObjectMock("ProjectID2"),
        ]

        self.api.list_servers.side_effect = [
            [ObjectMock("ServerID1"), ObjectMock("ServerID2")],
            [ObjectMock("ServerID3")],
        ]
        self.api.compute.get_server.side_effect = (
            openstack.exceptions.ResourceNotFound()
        )
        result = self.instance.find_non_existent_servers(
            cloud_account="test", project_identifier=""
        )

        self.identity_module.list_projects.assert_called_once_with("test")
        self.mocked_connection.assert_called_once_with("test")

        self.api.list_servers.assert_has_calls(
            [
                mock.call(
                    detailed=False,
                    all_projects=True,
                    bare=True,
                    filters={
                        "all_tenants": True,
                        "project_id": "ProjectID1",
                    },
                ),
                mock.call(
                    detailed=False,
                    all_projects=True,
                    bare=True,
                    filters={
                        "all_tenants": True,
                        "project_id": "ProjectID2",
                    },
                ),
            ],
            any_order=True,
        )

        self.assertEqual(
            result,
            {"ProjectID1": ["ServerID1", "ServerID2"], "ProjectID2": ["ServerID3"]},
        )

    def test_find_non_existent_servers(self):
        """
        Tests calling find_non_existent_servers
        """
        # pylint:disable=too-few-public-methods,invalid-name,redefined-builtin
        class ObjectMock:
            def __init__(self, id):
                self.id = id

        self.api.list_servers.return_value = [
            ObjectMock("ServerID1"),
            ObjectMock("ServerID2"),
        ]
        self.api.compute.get_server.side_effect = (
            openstack.exceptions.ResourceNotFound()
        )

        result = self.instance.find_non_existent_servers(
            cloud_account="test", project_identifier="project"
        )

        self.identity_module.find_mandatory_project.assert_called_once_with(
            "test", project_identifier="project"
        )
        self.mocked_connection.assert_called_once_with("test")

        self.api.list_servers.assert_called_once_with(
            detailed=False,
            all_projects=True,
            bare=True,
            filters={
                "all_tenants": True,
                "project_id": self.identity_module.find_mandatory_project.return_value.id,
            },
        )

        self.assertEqual(
            result,
            {
                self.identity_module.find_mandatory_project.return_value.id: [
                    "ServerID1",
                    "ServerID2",
                ],
            },
        )

    def test_find_non_existent_projects(self):
        """
        Tests calling find_non_existent_projects
        """
        # pylint:disable=too-few-public-methods,invalid-name,redefined-builtin
        class ObjectMock:
            def __init__(self, id):
                self.id = id
                self.project_id = "Project"

        self.api.list_servers.return_value = [
            ObjectMock("ServerID1"),
            ObjectMock("ServerID2"),
        ]
        self.api.identity.get_project.side_effect = (
            openstack.exceptions.ResourceNotFound()
        )

        result = self.instance.find_non_existent_projects(cloud_account="test")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_servers.assert_called_once_with(
            detailed=False,
            all_projects=True,
            bare=True,
            filters={
                "all_tenants": True,
            },
        )

        self.assertEqual(
            result,
            {
                "Project": ["ServerID1", "ServerID2"],
            },
        )
