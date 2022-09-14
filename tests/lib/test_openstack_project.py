from dataclasses import dataclass
import unittest
from typing import List
from unittest.mock import MagicMock

from openstack_api.openstack_project import OpenstackProject
from tests.lib.test_openstack_query_base import OpenstackQueryBaseTests


class OpenstackProjectTests(unittest.TestCase, OpenstackQueryBaseTests):
    """
    Runs various tests to ensure we are using the Openstack
    identity module in the expected way
    """

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackProject(self.mocked_connection)
        self.api = self.mocked_connection.return_value.__enter__.return_value

        self.mock_project_list = [
            {
                "id": "projectid1",
                "name": "Project1",
                "description": "Description1",
                "tags": ["test1@test.com"],
            },
            {
                "id": "projectid2",
                "name": "Project2",
                "description": "Description2",
                "tags": ["test2@test.com"],
            },
            {
                "id": "projectid3",
                "name": "Project3",
                "description": None,
                "tags": [],
            },
        ]

    def test_property_funcs(self):
        """
        Tests calling get_query_property_funcs
        """

        @dataclass
        class _ProjectMock:
            tags: List[str]

            def __getitem__(self, attr):
                return getattr(self, attr)

        item = _ProjectMock(["test@example.com"])
        property_funcs = self.instance.get_query_property_funcs("test")

        # Test project_email
        result = property_funcs["email"](item)
        self.assertEqual(result, "test@example.com")

    def test_search_project_id_in(self):
        """
        Tests calling search_project_id_in
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_id_in(
            cloud_account="test", ids=["projectid1", "projectid2"]
        )

        self.assertEqual(result, [self.mock_project_list[0], self.mock_project_list[1]])

    def test_search_projects_id_not_in(self):
        """
        Tests calling search_project_id_not_in
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_id_not_in(
            cloud_account="test", ids=["projectid1", "projectid2"]
        )

        self.assertEqual(result, [self.mock_project_list[2]])

    def test_search_all_projects_no_project(self):
        """
        Tests calling search_all_projects with no project selected
        """
        self.instance.search_all_projects(cloud_account="test")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_projects.assert_called_once_with()

    def test_search_all_projects(self):
        """
        Tests calling search_all_projects
        """
        self.instance.search_all_projects(cloud_account="test")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_projects.assert_called_once_with()

    def test_search_projects_name_in(self):
        """
        Tests calling search_projects_name_in
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_name_in(
            cloud_account="test",
            names=["Project1", "Project2"],
        )

        self.assertEqual(result, [self.mock_project_list[0], self.mock_project_list[1]])

    def test_search_projects_name_not_in(self):
        """
        Tests calling search_projects_name_not_in
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_name_not_in(
            cloud_account="test",
            names=["Project1", "Project2"],
        )

        self.assertEqual(result, [self.mock_project_list[2]])

    def test_search_projects_name_contains(self):
        """
        Tests calling search_projects_name_contains
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_name_contains(
            cloud_account="test",
            name_snippets=["Project", "1"],
        )

        self.assertEqual(result, [self.mock_project_list[0]])

        result = self.instance.search_projects_name_contains(
            cloud_account="test", name_snippets=["2"]
        )

        self.assertEqual(result, [self.mock_project_list[1]])

        result = self.instance.search_projects_name_contains(
            cloud_account="test", name_snippets=["Project"]
        )

        self.assertEqual(result, self.mock_project_list)

    def test_search_projects_name_not_contains(self):
        """
        Tests calling search_projects_name_not_contains
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_name_not_contains(
            cloud_account="test",
            name_snippets=["Project", "1"],
        )

        self.assertEqual(result, [])

        result = self.instance.search_projects_name_not_contains(
            cloud_account="test", name_snippets=["2"]
        )

        self.assertEqual(result, [self.mock_project_list[0], self.mock_project_list[2]])

        result = self.instance.search_projects_name_not_contains(
            cloud_account="test", name_snippets=["Project"]
        )

        self.assertEqual(result, [])

    def test_search_projects_description_contains(self):
        """
        Tests calling search_projects_description_contains
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_description_contains(
            cloud_account="test",
            description_snippets=["Description", "1"],
        )

        self.assertEqual(result, [self.mock_project_list[0]])

        result = self.instance.search_projects_description_contains(
            cloud_account="test", description_snippets=["2"]
        )

        self.assertEqual(result, [self.mock_project_list[1]])

        result = self.instance.search_projects_description_contains(
            cloud_account="test", description_snippets=["Description"]
        )

        self.assertEqual(result, [self.mock_project_list[0], self.mock_project_list[1]])

    def test_search_projects_description_not_contains(self):
        """
        Tests calling search_projects_description_not_contains
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_description_not_contains(
            cloud_account="test",
            description_snippets=["Description", "1"],
        )

        self.assertEqual(result, [self.mock_project_list[2]])

        result = self.instance.search_projects_description_not_contains(
            cloud_account="test", description_snippets=["2"]
        )

        self.assertEqual(result, [self.mock_project_list[0], self.mock_project_list[2]])

        result = self.instance.search_projects_description_not_contains(
            cloud_account="test", description_snippets=["Description"]
        )

        self.assertEqual(result, [self.mock_project_list[2]])

    def test_search_projects_without_email(self):
        """
        Tests calling search_projects_without_email
        """

        self.instance.search_all_projects = MagicMock()
        self.instance.search_all_projects.return_value = self.mock_project_list

        result = self.instance.search_projects_without_email(
            cloud_account="test",
        )

        self.assertEqual(result, [self.mock_project_list[2]])
