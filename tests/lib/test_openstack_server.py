from dataclasses import dataclass
import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, NonCallableMock

from nose.tools import raises

import openstack
from openstack.exceptions import HttpException

from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_server import OpenstackServer

from structs.email_params import EmailParams


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

    def test_property_funcs(self):
        """
        Tests calling get_query_property_funcs
        """

        @dataclass
        class _ServerMock:
            user_id: str

            def __getitem__(self, attr):
                return getattr(self, attr)

        item = _ServerMock("UserID")
        property_funcs = self.instance.get_query_property_funcs("test")

        # Test user_email
        result = property_funcs["user_email"](item)
        self.assertEqual(result, self.api.identity.find_user.return_value["user_email"])

        # Test user_name
        result = property_funcs["user_name"](item)
        self.assertEqual(result, self.api.identity.find_user.return_value["user_name"])

    def test_search(self):
        """
        Tests calling search
        """
        query_params = QueryParams(
            query_preset="all_servers",
            properties_to_select=NonCallableMock(),
            group_by=NonCallableMock(),
            get_html=NonCallableMock(),
        )

        self.instance.search_all_servers = MagicMock()

        self.instance.search(
            cloud_account="test",
            query_params=query_params,
            project_identifier="ProjectID",
            test_param="TestParam",
        )

        self.instance.search_all_servers.assert_called_once_with(
            "test", project_identifier="ProjectID", test_param="TestParam"
        )

    def test_search_all_servers_no_project(self):
        """
        Tests calling search_all_servers with no project selected
        """

        @dataclass
        class _ProjectMock:
            # pylint: disable=invalid-name
            id: str

        self.identity_module.list_projects.return_value = [
            _ProjectMock("ID1"),
            _ProjectMock("ID2"),
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
                    }
                ),
                mock.call(
                    filters={
                        "all_tenants": True,
                        "project_id": "ID2",
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

    def test_find_non_existent_servers(self):
        """
        Tests calling find_non_existent_servers
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            project_id: str

            def __getitem__(self, item):
                return getattr(self, item)

        self.api.list_servers.return_value = [
            _ObjectMock("ObjectID1", "ProjectID1"),
            _ObjectMock("ObjectID2", "ProjectID1"),
            _ObjectMock("ObjectID3", "ProjectID1"),
        ]

        self.api.compute.get_server.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        result = self.instance.find_non_existent_servers(
            cloud_account="test", project_identifier="project"
        )

        self.assertEqual(
            result,
            {
                self.api.identity.find_project.return_value.id: [
                    "ObjectID1",
                    "ObjectID2",
                ]
            },
        )

    def test_find_non_existent_projects(self):
        """
        Tests calling find_non_existent_projects
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            project_id: str

            def __getitem__(self, item):
                return getattr(self, item)

        self.api.list_servers.return_value = [
            _ObjectMock("ServerID1", "ProjectID1"),
            _ObjectMock("ServerID2", "ProjectID1"),
            _ObjectMock("ServerID3", "ProjectID2"),
        ]

        self.api.identity.get_project.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        result = self.instance.find_non_existent_projects(cloud_account="test")

        self.assertEqual(result, {"ProjectID1": ["ServerID1", "ServerID2"]})

    @raises(ValueError)
    def test_email_users_no_email_error(self):
        """
        Tests the that email_users gives a value error when project_email is not present in the `properties_to_select`
        """
        smtp_account = MagicMock()
        email_params = EmailParams(
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=False,
            test_override_email=[""],
            send_as_html=False,
        )
        return self.instance.email_users(
            cloud_account="test_account",
            smtp_account=smtp_account,
            project_identifier="",
            query_preset="fips_older_than",
            message="Message",
            properties_to_select=["name"],
            email_params=email_params,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    def _email_users(self, query_preset: str):
        """
        Helper for checking email_users works correctly
        """
        smtp_account = MagicMock()
        email_params = EmailParams(
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=False,
            test_override_email=[""],
            send_as_html=False,
        )
        return self.instance.email_users(
            cloud_account="test_account",
            smtp_account=smtp_account,
            project_identifier="",
            query_preset=query_preset,
            message="Message",
            properties_to_select=["user_email"],
            email_params=email_params,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    def test_email_users_no_project(self):
        """
        Tests that email_users does not give a value error when a project is not required for the query type
        """

        for query_preset in OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT:
            self._email_users(query_preset)

    @raises(ValueError)
    def _check_email_users_raises(self, query_preset):
        """
        Helper for checking email_users raises a ValueError when needed (needed to allow multiple to be checked
        in the same test otherwise it stops after the first error)
        """
        self.assertRaises(ValueError, self._email_users(query_preset))

    def test_email_users_no_project_raises(self):
        """
        Tests that email_users gives a value error when a project is not required for the query type
        """

        # Should raise an error for all but servers_older_than and servers_last_updated_before
        should_pass = OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT
        should_not_pass = [
            x for x in OpenstackServer.SEARCH_QUERY_PRESETS if x not in should_pass
        ]

        for query_preset in should_not_pass:
            self._check_email_users_raises(query_preset)
