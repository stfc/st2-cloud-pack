from dataclasses import dataclass
import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, NonCallableMock
import openstack
from nose.tools import raises

from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from structs.email_params import EmailParams

# pylint:disable=too-many-public-methods
class OpenstackFloatingIPTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Network module in the expected way
    """

    # pylint:disable=too-few-public-methods,invalid-name
    class MockProject:
        def __init__(self):
            self.id = "ProjectID"

        def __getitem__(self, item):
            return getattr(self, item)

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch(
            "openstack_api.openstack_floating_ip.OpenstackIdentity"
        ) as identity_mock:
            self.instance = OpenstackFloatingIP(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.api = self.mocked_connection.return_value.__enter__.return_value

        self.mock_fip_list = [
            {
                "id": "fipid1",
                "name": "130.246.211.216",
                "created_at": "2020-06-28T14:00:00Z",
                "updated_at": "2020-06-28T14:00:00Z",
                "status": "DOWN",
            },
            {
                "id": "fipid2",
                "name": "130.246.211.217",
                "created_at": "2021-04-28T14:00:00Z",
                "updated_at": "2021-06-28T14:00:00Z",
                "status": "ACTIVE",
            },
            {
                "id": "fipid3",
                "name": "130.246.212.218",
                "created_at": "2021-06-28T14:00:00Z",
                "updated_at": "2021-06-28T14:00:00Z",
                "status": "ACTIVE",
            },
        ]

    def test_property_funcs(self):
        """
        Tests calling get_query_property_funcs
        """

        class _FloatingIPMock:
            project_id: str

            def __init__(self, project_id: str):
                self.project_id = project_id

            def __getitem__(self, attr):
                return getattr(self, attr)

        item = _FloatingIPMock("UserID")
        property_funcs = self.instance.get_query_property_funcs("test")

        # Test project_name
        result = property_funcs["project_name"](item)
        self.assertEqual(result, self.api.identity.find_project.return_value["name"])

        # Test project_email
        result = property_funcs["project_email"](item)
        self.assertEqual(result, self.identity_module.find_project_email.return_value)

    def test_search(self):
        """
        Tests calling search
        """
        query_params = QueryParams(
            query_preset="all_fips",
            properties_to_select=NonCallableMock(),
            group_by=NonCallableMock(),
            get_html=NonCallableMock(),
        )

        self.instance.search_all_fips = MagicMock()

        self.instance.search(
            cloud_account="test",
            query_params=query_params,
            project_identifier="ProjectID",
            test_param="TestParam",
        )

        self.instance.search_all_fips.assert_called_once_with(
            "test", project_identifier="ProjectID", test_param="TestParam"
        )

    def test_search_all_fips_no_project(self):
        """
        Tests calling search_all_fips with no project selected
        """
        self.instance.search_all_fips(cloud_account="test", project_identifier="")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_floating_ips.assert_called_once_with(filters={})

    def test_search_all_fips(self):
        """
        Tests calling search_all_fips
        """
        self.identity_module.find_mandatory_project.return_value = self.MockProject()
        self.instance.search_all_fips(
            cloud_account="test", project_identifier="ProjectName"
        )

        self.mocked_connection.assert_called_once_with("test")

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud_account="test", project_identifier="ProjectName"
        )
        self.api.list_floating_ips.assert_called_once_with(
            filters={
                "project_id": "ProjectID",
            }
        )

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_fips_older_than(self, mock_datetime):
        """
        Tests calling search_fips_older_than
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_older_than(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_fip_list[0], self.mock_fip_list[1]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_fips_younger_than(self, mock_datetime):
        """
        Tests calling search_fips_younger_than
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_younger_than(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_fip_list[2]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_fips_last_updated_before(self, mock_datetime):
        """
        Tests calling search_fips_last_updated_before
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_last_updated_before(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_fip_list[0]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_fips_last_updated_after(self, mock_datetime):
        """
        Tests calling search_fips_last_updated_after
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_last_updated_after(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_fip_list[1], self.mock_fip_list[2]])

    def test_search_fips_name_in(self):
        """
        Tests calling search_fips_name_in
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_name_in(
            cloud_account="test",
            project_identifier="",
            names=["130.246.211.216", "130.246.211.217"],
        )

        self.assertEqual(result, [self.mock_fip_list[0], self.mock_fip_list[1]])

    def test_search_fips_name_not_in(self):
        """
        Tests calling search_fips_name_not_in
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_name_not_in(
            cloud_account="test",
            project_identifier="",
            names=["130.246.211.216", "130.246.211.217"],
        )

        self.assertEqual(result, [self.mock_fip_list[2]])

    def test_search_fips_name_contains(self):
        """
        Tests calling search_fips_name_contains
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_name_contains(
            cloud_account="test",
            project_identifier="",
            name_snippets=["130.246", "211"],
        )

        self.assertEqual(result, [self.mock_fip_list[0], self.mock_fip_list[1]])

        result = self.instance.search_fips_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["130.246.212"]
        )

        self.assertEqual(result, [self.mock_fip_list[2]])

        result = self.instance.search_fips_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["130"]
        )

        self.assertEqual(result, self.mock_fip_list)

    def test_search_fips_name_not_contains(self):
        """
        Tests calling search_fips_name_not_contains
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_name_not_contains(
            cloud_account="test",
            project_identifier="",
            name_snippets=["130.246", "21"],
        )

        self.assertEqual(result, [])

        result = self.instance.search_fips_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["130.246.212"]
        )

        self.assertEqual(result, [self.mock_fip_list[0], self.mock_fip_list[1]])

        result = self.instance.search_fips_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["130"]
        )

        self.assertEqual(result, [])

    def test_search_fip_id_in(self):
        """
        Tests calling search_fips_id_in
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_id_in(
            cloud_account="test", project_identifier="", ids=["fipid1", "fipid2"]
        )

        self.assertEqual(result, [self.mock_fip_list[0], self.mock_fip_list[1]])

    def test_search_fips_id_not_in(self):
        """
        Tests calling search_fips_id_not_in
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_id_not_in(
            cloud_account="test", project_identifier="", ids=["fipid1", "fipid2"]
        )

        self.assertEqual(result, [self.mock_fip_list[2]])

    def test_search_fips_down(self):
        """
        Tests calling search_fips_down
        """

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_down(
            cloud_account="test", project_identifier=""
        )

        self.assertEqual(result, [self.mock_fip_list[0]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_fips_down_before(self, mock_datetime):
        """
        Tests calling search_fips_down_before_before
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_fips = MagicMock()
        self.instance.search_all_fips.return_value = self.mock_fip_list

        result = self.instance.search_fips_down_before(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_fip_list[0]])

    def test_find_non_existent_fips(self):
        """
        Tests calling find_non_existent_fips
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            project_id: str

            def __getitem__(self, item):
                return getattr(self, item)

        self.api.list_floating_ips.return_value = [
            _ObjectMock("ObjectID1", "ProjectID1"),
            _ObjectMock("ObjectID2", "ProjectID1"),
            _ObjectMock("ObjectID3", "ProjectID1"),
        ]

        self.api.network.get_ip.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        result = self.instance.find_non_existent_fips(
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

        self.api.list_floating_ips.return_value = [
            _ObjectMock("FipID1", "ProjectID1"),
            _ObjectMock("FipID2", "ProjectID1"),
            _ObjectMock("FipID3", "ProjectID2"),
        ]

        self.api.identity.get_project.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        result = self.instance.find_non_existent_projects(cloud_account="test")

        self.assertEqual(result, {"ProjectID1": ["FipID1", "FipID2"]})

    @raises(ValueError)
    def test_email_users_no_email_error(self):
        """
        Tests the that email_users gives a value error when user_email is not present in the `properties_to_select`
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
            query_preset="servers_older_than",
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
            properties_to_select=["project_email"],
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

        for query_preset in OpenstackFloatingIP.SEARCH_QUERY_PRESETS_NO_PROJECT:
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

        # Should raise an error for all but a few queries
        should_pass = OpenstackFloatingIP.SEARCH_QUERY_PRESETS_NO_PROJECT
        should_not_pass = [
            x for x in OpenstackFloatingIP.SEARCH_QUERY_PRESETS if x not in should_pass
        ]

        for query_preset in should_not_pass:
            self._check_email_users_raises(query_preset)
