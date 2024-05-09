from dataclasses import dataclass
import unittest
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

        self.api = self.mocked_connection.return_value.__enter__.return_value

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
