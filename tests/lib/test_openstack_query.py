from dataclasses import dataclass
import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, NonCallableMock, patch, ANY, NonCallableMock, Mock

import openstack
from nose.tools import raises

from openstack_api.dataclasses import (
    NonExistentCheckParams,
    NonExistentProjectCheckParams,
    EmailQueryParams,
    QueryParams,
)

from openstack_api.openstack_query import OpenstackQuery
from structs.email_params import EmailParams


class OpenstackQueryTests(unittest.TestCase):
    """
    Runs various tests to ensure OpenstackQuery functions in the expected way
    """

    # pylint:disable=too-few-public-methods,too-many-instance-attributes
    class ItemTest:
        def __init__(self, test1, test2):
            self.test1 = test1
            self.test2 = test2

        def __getitem__(self, key):
            return getattr(self, key)

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch("openstack_api.openstack_query.EmailApi") as email_mock:
            self.instance = OpenstackQuery(self.mocked_connection)
            self.email_mock = email_mock.return_value
        self.api = self.mocked_connection.return_value.__enter__.return_value
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_datetime_before_x_days(self, mock_datetime):
        """
        Tests datetime_before_x_days works as expected
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        # Should pass
        assert (
            self.instance.datetime_before_x_days(
                "2021-06-28T14:00:00Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is True
        )

        # Should fail
        assert (
            self.instance.datetime_before_x_days(
                "2021-07-28T14:00:00Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is False
        )

        # Edgecases
        assert (
            self.instance.datetime_before_x_days(
                "2021-07-11T23:59:59Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is True
        )

        assert (
            self.instance.datetime_before_x_days(
                "2021-07-12T00:00:01Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is False
        )

    def test_apply_query(self):
        """
        Tests apply_query works as expected
        """

        items = [1, 2, 3, 4]

        assert self.instance.apply_query(items, lambda item: True) == items
        assert not self.instance.apply_query(items, lambda item: False)
        assert self.instance.apply_query(items, lambda item: item > 2) == [3, 4]

    def test_apply_queries(self):
        """
        Tests apply_queries works as expected
        """

        items = [1, 2, 3, 4]

        assert self.instance.apply_queries(
            items, [lambda item: item > 2, lambda item: item < 4]
        ) == [3]

    def test_parse_properties(self):
        """
        Tests parse_properties works as expected
        """
        property_funcs = {"test2": lambda item: item.test2 + " World"}

        items = [self.ItemTest("Item1", "Hello"), self.ItemTest("Item2", "Hello")]

        result = self.instance.parse_properties(
            items, ["test1", "test2"], property_funcs
        )

        self.assertEqual(
            result,
            [
                {"test1": "Item1", "test2": "Hello World"},
                {"test1": "Item2", "test2": "Hello World"},
            ],
        )

    def test_get_user_prop(self):
        """
        Tests get_user_prop works as expected
        """

        self.identity_api.find_user.return_value = self.ItemTest("Value1", "Value2")
        result = self.instance.get_user_prop("test", "userid", "test1")
        self.assertEqual(result, "Value1")

        self.identity_api.find_user.return_value = None
        result = self.instance.get_user_prop("test", "userid", "test1")
        self.assertEqual(result, None)

    def test_get_project_prop(self):
        """
        Tests get_project_prop works as expected
        """

        self.identity_api.find_project.return_value = self.ItemTest("Value1", "Value2")
        result = self.instance.get_project_prop("test", "projectid", "test1")
        self.assertEqual(result, "Value1")

        self.identity_api.find_project.return_value = None
        result = self.instance.get_project_prop("test", "projectid", "test1")
        self.assertEqual(result, None)

    def test_collate_results(self):
        """
        Tests collate_results works as expected
        """
        property_funcs = {
            "test2": lambda item: item.test2 + " World" if item.test2 else None
        }

        items = [
            self.ItemTest("Item1", "Hello"),
            self.ItemTest("Item2", "Hello"),
            self.ItemTest("Item3", "Test"),
            self.ItemTest("Item4", None),
        ]

        properties_dict = self.instance.parse_properties(
            items, ["test1", "test2"], property_funcs
        )

        result = self.instance.collate_results(properties_dict, "test2", False)

        assert len(result) == 2
        assert len(result["Hello World"]) > 0
        assert "Item1" in result["Hello World"] and "Item2" in result["Hello World"]
        assert len(result["Test World"]) > 0

    def test_parse_and_output_table_with_grouping(self):
        """
        Tests parse_and_output_table works as expected when collating is required
        """
        items = [
            self.ItemTest("Item1", "Hello"),
            self.ItemTest("Item2", "Hello"),
            self.ItemTest("Item3", "Test"),
        ]
        properties_to_select = ["test1", "new_property", "test2"]
        property_funcs = {"new_property": lambda a: f"{a['test1']}_new"}

        self.instance.parse_properties = MagicMock()
        self.instance.parse_properties.return_value = [{}]
        self.instance.collate_results = MagicMock()
        self.instance.generate_table = MagicMock()

        result = self.instance.parse_and_output_table(
            items,
            property_funcs,
            properties_to_select,
            "new_property",
            False,
        )

        self.instance.parse_properties.assert_called_once_with(
            items, properties_to_select, property_funcs
        )
        self.instance.collate_results.assert_called_once()
        self.instance.generate_table.assert_not_called()

        self.assertEqual(result, self.instance.collate_results.return_value)

    def test_parse_and_output_table_no_grouping(self):
        """
        Tests parse_and_output_table works as expected when no collating is required
        """
        items = [
            self.ItemTest("Item1", "Hello"),
            self.ItemTest("Item2", "Hello"),
            self.ItemTest("Item3", "Test"),
        ]
        properties_to_select = ["test1", "new_property", "test2"]
        property_funcs = {"new_property": lambda a: f"{a['test1']}_new"}

        self.instance.parse_properties = MagicMock()
        self.instance.parse_properties.return_value = [{}]
        self.instance.collate_results = MagicMock()
        self.instance.generate_table = MagicMock()

        result = self.instance.parse_and_output_table(
            items,
            property_funcs,
            properties_to_select,
            "",
            False,
        )

        self.instance.parse_properties.assert_called_once_with(
            items, properties_to_select, property_funcs
        )
        self.instance.collate_results.assert_not_called()
        self.instance.generate_table.assert_called_once()

        self.assertEqual(result, self.instance.generate_table.return_value)

    def test_search_resource(self):
        """
        Tests calling search_resource
        """

        search_api = MagicMock()
        property_funcs = NonCallableMock()

        self.instance.parse_and_output_table = Mock()

        query_params = QueryParams(
            query_preset="test_query",
            properties_to_select=NonCallableMock(),
            group_by=NonCallableMock(),
            get_html=NonCallableMock(),
        )

        result = self.instance.search_resource(
            "test",
            search_api,
            property_funcs,
            query_params,
            project_identifier="project_identifier",
        )

        search_api["search_test_query"].assert_called_once_with(
            "test", project_identifier="project_identifier"
        )
        self.instance.parse_and_output_table.assert_called_once_with(
            items=search_api["search_test_query"].return_value,
            property_funcs=property_funcs,
            properties_to_select=query_params.properties_to_select,
            group_by=query_params.group_by,
            get_html=query_params.get_html,
        )
        self.assertEqual(result, self.instance.parse_and_output_table.return_value)

    def test_find_non_existent_objects(self):
        """
        Tests calling find_non_existent_objects
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            project_id: str

            def __getitem__(self, item):
                return getattr(self, item)

        # pylint:disable=unused-argument
        def object_get_func(conn, object_id):
            if object_id in {"ObjectID1", "ObjectID2"}:
                raise openstack.exceptions.ResourceNotFound()

        # pylint:disable=unused-argument
        def object_list_func(conn, project):
            if project.id == "ProjectID1":
                return [
                    _ObjectMock("ObjectID1", "ProjectID1"),
                    _ObjectMock("ObjectID2", "ProjectID1"),
                    _ObjectMock("ObjectID3", "ProjectID1"),
                ]
            return [
                _ObjectMock("ObjectID1", "ProjectID2"),
            ]

        check_params = NonExistentCheckParams(
            object_list_func=object_list_func,
            object_get_func=object_get_func,
            object_id_param_name="id",
            object_project_param_name="project_id",
        )

        self.api.list_projects.return_value = [
            _ObjectMock("ProjectID1", ""),
            _ObjectMock("ProjectID2", ""),
        ]

        result = self.instance.find_non_existent_objects(
            cloud_account="test", project_identifier="", check_params=check_params
        )

        self.mocked_connection.assert_called_with("test")

        self.assertEqual(
            result,
            {
                "ProjectID1": [
                    "ObjectID1",
                    "ObjectID2",
                ],
                "ProjectID2": ["ObjectID1"],
            },
        )

    def test_find_non_existent_object_projects(self):
        """
        Tests calling find_non_existent_object_projects
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            project_id: str

            def __getitem__(self, item):
                return getattr(self, item)

        self.identity_api.get_project.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        check_params = NonExistentProjectCheckParams(
            object_list_func=lambda conn: [
                _ObjectMock("ObjectID1", "ProjectID1"),
                _ObjectMock("ObjectID2", "ProjectID1"),
                _ObjectMock("ObjectID3", "ProjectID1"),
            ],
            object_id_param_name="id",
            object_project_param_name="project_id",
        )

        self.identity_api.find_project.return_value = _ObjectMock("ProjectID1", "")

        result = self.instance.find_non_existent_object_projects(
            cloud_account="test", check_params=check_params
        )

        self.mocked_connection.assert_called_with("test")

        self.assertEqual(
            result,
            {
                "ProjectID1": [
                    "ObjectID1",
                    "ObjectID2",
                ],
            },
        )

    def test_email_users(
        self,
    ):
        """
        Tests calling email_users
        """
        smtp_account = NonCallableMock()
        query_params = EmailQueryParams(
            required_email_property="required_property",
            valid_search_queries=[NonCallableMock(), "no_project"],
            valid_search_queries_no_project=["no_project"],
            search_api=MagicMock(),
            object_type="server",
        )
        email_params = EmailParams(
            subject=NonCallableMock(),
            email_from=NonCallableMock(),
            email_cc=NonCallableMock(),
            header=NonCallableMock(),
            footer=NonCallableMock(),
            attachment_filepaths=NonCallableMock(),
            test_override=NonCallableMock(),
            test_override_email=NonCallableMock(),
            send_as_html=NonCallableMock(),
        )
        properties_to_select = [NonCallableMock(), query_params.required_email_property]

        self.instance.parse_and_output_table = MagicMock()

        self.instance.email_users(
            cloud_account="test",
            smtp_account=smtp_account,
            query_params=query_params,
            project_identifier="",
            query_preset=query_params.valid_search_queries_no_project[0],
            message=NonCallableMock(),
            properties_to_select=properties_to_select,
            email_params=email_params,
        )
        self.instance.parse_and_output_table.assert_called_once_with(
            cloud_account="test",
            items=query_params.search_api["search_query_preset"].return_value,
            object_type=query_params.object_type,
            properties_to_select=properties_to_select,
            group_by=query_params.required_email_property,
            get_html=email_params.send_as_html,
        )
        self.email_mock.send_emails.assert_called_once_with(
            smtp_account=smtp_account, emails=ANY, email_params=email_params
        )

    @raises(ValueError)
    def test_email_users_missing_required_property(
        self,
    ):
        """
        Tests calling email_users raises an error when the required property is missing from the selected ones
        """
        smtp_account = NonCallableMock()
        query_params = EmailQueryParams(
            required_email_property="required_property",
            valid_search_queries=[NonCallableMock(), "no_project"],
            valid_search_queries_no_project=["no_project"],
            search_api=MagicMock(),
            object_type="server",
        )
        email_params = EmailParams(
            subject=NonCallableMock(),
            email_from=NonCallableMock(),
            email_cc=NonCallableMock(),
            header=NonCallableMock(),
            footer=NonCallableMock(),
            attachment_filepaths=NonCallableMock(),
            test_override=NonCallableMock(),
            test_override_email=NonCallableMock(),
            send_as_html=NonCallableMock(),
        )
        properties_to_select = [NonCallableMock()]

        self.instance.parse_and_output_table = MagicMock()

        self.instance.email_users(
            cloud_account="test",
            smtp_account=smtp_account,
            query_params=query_params,
            project_identifier=NonCallableMock(),
            query_preset=query_params.valid_search_queries[0],
            message=NonCallableMock(),
            properties_to_select=properties_to_select,
            email_params=email_params,
        )

    @raises(ValueError)
    def test_email_users_invalid_query(
        self,
    ):
        """
        Tests calling email_users raises an error when the query_preset is invalid
        """
        smtp_account = NonCallableMock()
        query_params = EmailQueryParams(
            required_email_property="required_property",
            valid_search_queries=["query1", "no_project"],
            valid_search_queries_no_project=["no_project"],
            search_api=MagicMock(),
            object_type="server",
        )
        email_params = EmailParams(
            subject=NonCallableMock(),
            email_from=NonCallableMock(),
            email_cc=NonCallableMock(),
            header=NonCallableMock(),
            footer=NonCallableMock(),
            attachment_filepaths=NonCallableMock(),
            test_override=NonCallableMock(),
            test_override_email=NonCallableMock(),
            send_as_html=NonCallableMock(),
        )
        properties_to_select = [NonCallableMock(), query_params.required_email_property]

        self.instance.parse_and_output_table = MagicMock()

        self.instance.email_users(
            cloud_account="test",
            smtp_account=smtp_account,
            query_params=query_params,
            project_identifier=NonCallableMock(),
            query_preset=NonCallableMock(),
            message=NonCallableMock(),
            properties_to_select=properties_to_select,
            email_params=email_params,
        )

    @raises(ValueError)
    def test_email_users_missing_project(
        self,
    ):
        """
        Tests calling email_users raises an error when the query requires a project but is not given one
        """
        smtp_account = NonCallableMock()
        query_params = EmailQueryParams(
            required_email_property="required_property",
            valid_search_queries=[NonCallableMock(), "no_project"],
            valid_search_queries_no_project=["no_project"],
            search_api=MagicMock(),
            object_type="server",
        )
        email_params = EmailParams(
            subject=NonCallableMock(),
            email_from=NonCallableMock(),
            email_cc=NonCallableMock(),
            header=NonCallableMock(),
            footer=NonCallableMock(),
            attachment_filepaths=NonCallableMock(),
            test_override=NonCallableMock(),
            test_override_email=NonCallableMock(),
            send_as_html=NonCallableMock(),
        )
        properties_to_select = [NonCallableMock(), query_params.required_email_property]

        self.instance.parse_and_output_table = MagicMock()

        self.instance.email_users(
            cloud_account="test",
            smtp_account=smtp_account,
            query_params=query_params,
            project_identifier="",
            query_preset=query_params.valid_search_queries[0],
            message=NonCallableMock(),
            properties_to_select=properties_to_select,
            email_params=email_params,
        )
