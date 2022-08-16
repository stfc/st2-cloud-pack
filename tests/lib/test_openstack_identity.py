import unittest
from unittest.mock import NonCallableMock, ANY, Mock, MagicMock

from nose.tools import raises
from openstack.exceptions import ConflictException

from enums.user_domains import UserDomains
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_identity import OpenstackIdentity
from structs.project_details import ProjectDetails


# pylint:disable=too-many-public-methods
class OpenstackIdentityTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Identity module in the expected way
    """

    # pylint:disable=too-few-public-methods
    class MockProject:
        def __init__(self, tags):
            self.tags = tags
            self.set_tags = Mock()

        def __getitem__(self, item):
            return getattr(self, item)

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackIdentity(self.mocked_connection)
        self.api = self.mocked_connection.return_value.__enter__.return_value
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )

    @raises(MissingMandatoryParamError)
    def test_create_project_name_missing_throws(self):
        """
        Tests calling the API wrapper without a domain will throw
        """
        self.instance.create_project(
            "",
            ProjectDetails(
                name="", description="", email="Test@Test.com", is_enabled=False
            ),
        )

    @raises(MissingMandatoryParamError)
    def test_create_project_email_missing_throws(self):
        """
        Tests calling the API wrapper without an email will throw
        """
        self.instance.create_project(
            "", ProjectDetails(name="Test", email="", description="", is_enabled=False)
        )

    @raises(ValueError)
    def test_create_project_invalid_email_throws(self):
        """
        Tests calling the API wrapper with an invalid email will throw
        """
        self.instance.create_project(
            "",
            ProjectDetails(
                name="Test", email="NotAnEmail", description="", is_enabled=False
            ),
        )

    def test_create_project_forwards_result(self):
        """
        Tests that the params and result are forwarded as-is to/from the
        create_project API
        """

        expected_details = ProjectDetails(
            name=NonCallableMock(),
            email="Test@Test.com",
            description=NonCallableMock(),
            is_enabled=NonCallableMock(),
        )

        found = self.instance.create_project(
            cloud_account="test", project_details=expected_details
        )

        self.mocked_connection.assert_called_once_with("test")

        assert found == self.identity_api.create_project.return_value
        self.identity_api.create_project.assert_called_once_with(
            name=expected_details.name,
            domain_id="default",
            description=expected_details.description,
            is_enabled=expected_details.is_enabled,
            tags=[expected_details.email],
        )

    @raises(ConflictException)
    def test_create_project_forwards_conflict_exception(self):
        """
        Tests that a conflict exception doesn't get lost from Openstack
        """

        self.identity_api.create_project.side_effect = ConflictException
        project_details = ProjectDetails(
            name=NonCallableMock(),
            email="Test@Test.com",
            description=NonCallableMock(),
            is_enabled=NonCallableMock(),
        )
        self.instance.create_project(NonCallableMock(), project_details)

    @staticmethod
    @raises(MissingMandatoryParamError)
    def test_delete_project_throws_whitespace_args():
        """
        Test that if the user doesn't provide meaningful args to delete we throw
        """
        # Intentional spaces
        OpenstackIdentity().delete_project("", project_identifier=" \t")

    def test_delete_project_calls_find_project(self):
        """
        Since delete project expects either the OS UUID or a project instance
        we need to forward the call onto find before we call delete
        """

        identifier = NonCallableMock()

        self.instance.delete_project(NonCallableMock(), project_identifier=identifier)

        # We want this to throw to follow Pythonic E.A.F.P.
        self.identity_api.find_project.assert_called_once_with(
            identifier.strip(), ignore_missing=ANY
        )
        found_identifier = self.identity_api.find_project.return_value
        self.identity_api.delete_project.assert_called_once_with(
            project=found_identifier, ignore_missing=False
        )

    def test_delete_project_successful_with_name_or_id(self):
        """
        Tests delete project will use name or Openstack ID if provided
        and will return the result
        """

        self.instance.find_project = Mock()
        self.identity_api.delete_project.return_value = None

        identifier = NonCallableMock()
        result = self.instance.delete_project(
            cloud_account="test", project_identifier=identifier
        )

        assert result is True
        self.identity_api.delete_project.assert_called_once_with(
            project=self.instance.find_project.return_value, ignore_missing=False
        )

    def test_delete_project_handles_resource_not_found(self):
        """
        Tests that the delete method can handle resource not found. This is
        enabled, so it's easier to tell between a None (success) type and a
        failure
        """

        self.instance.find_project = Mock(return_value=None)
        result = self.instance.delete_project("", project_identifier="test")
        assert result is False

    @raises(MissingMandatoryParamError)
    def test_find_project_raises_missing_project_identifier(self):
        """
        Tests that a missing mandatory parameter is missing if a whitespace
        or empty string is passed
        """

        self.instance.find_project("set", " ")

    def test_find_project_forwards_result(self):
        """
        Tests that the call forwards the result as is, and the Openstack API
        is being used correctly
        """

        cloud_account, project_identifier = NonCallableMock(), NonCallableMock()
        found = self.instance.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

        self.mocked_connection.assert_called_once_with(cloud_account)
        self.identity_api.find_project.assert_called_once_with(
            project_identifier.strip(), ignore_missing=True
        )
        assert found == self.identity_api.find_project.return_value

    def test_find_mandatory_project_forwards(self):
        """
        Check the arguments are forwarded as-is and the result returned
        """
        self.instance.find_project = Mock()
        args = (NonCallableMock(), NonCallableMock())
        returned = self.instance.find_mandatory_project(*args)

        self.instance.find_project.assert_called_once_with(*args)
        assert returned == self.instance.find_project.return_value

    @raises(ItemNotFoundError)
    def test_find_mandatory_project_raises_for_missing(self):
        """
        Check that a missing project will raise correctly
        """
        self.instance.find_project = Mock(return_value=None)
        self.instance.find_mandatory_project(NonCallableMock(), NonCallableMock())

    def test_list_projects(self):
        """
        Checks list_projects uses the OpenStack API correctly
        """
        self.instance.list_projects("test")

        self.mocked_connection.assert_called_once_with("test")
        self.api.list_projects.assert_called_once()

    @raises(MissingMandatoryParamError)
    def test_find_user_missing_identifier(self):
        """
        Checks a missing user identifier will raise correctly
        """
        self.instance.find_user(NonCallableMock(), " \t", NonCallableMock())

    def test_find_user_returns_result(self):
        """
        Checks that find_user returns the correct result
        """
        cloud, user, domain = NonCallableMock(), NonCallableMock(), UserDomains.STFC
        returned = self.instance.find_user(cloud, user, domain)

        self.mocked_connection.assert_called_once_with(cloud)
        self.identity_api.find_domain.assert_called_once_with(
            domain.value.lower().strip(), ignore_missing=False
        )
        self.identity_api.find_user.assert_called_once_with(
            user.strip(),
            domain_id=self.identity_api.find_domain.return_value.id,
            ignore_missing=True,
        )
        expected = self.identity_api.find_user.return_value
        assert returned == expected

    @raises(MissingMandatoryParamError)
    def test_find_user_all_domains_missing_identifier(self):
        """
        Checks a missing user identifier will raise correctly
        """
        self.instance.find_user_all_domains(NonCallableMock(), " \t")

    def test_find_user_all_domains_returns_result(self):
        """
        Checks that find_user_all_domains returns the correct result
        """
        cloud, user = NonCallableMock(), NonCallableMock()
        returned = self.instance.find_user_all_domains(cloud, user)

        self.mocked_connection.assert_called_once_with(cloud)
        self.identity_api.find_user.assert_called_once_with(
            user.strip(),
            ignore_missing=True,
        )
        expected = self.identity_api.find_user.return_value
        assert returned == expected

    def test_get_project_email(self):
        """
        Checks that get_project_email functions correctly
        """
        expected_email = "Test@Test.com"
        mock_project = {"tags": ["Test", expected_email, "12123421"]}

        email = self.instance.get_project_email(mock_project)

        self.assertEqual(expected_email, email)

    def test_find_project_email(self):
        """
        Checks that find_project_email functions correctly
        """
        expected_email = "Test@Test.com"
        mock_project = {"tags": ["Test", expected_email, "12123421"]}

        cloud_account, project_identifier = NonCallableMock(), NonCallableMock()
        self.identity_api.find_project.return_value = mock_project
        found = self.instance.find_project_email(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

        self.mocked_connection.assert_called_once_with(cloud_account)
        self.identity_api.find_project.assert_called_once_with(
            project_identifier.strip(), ignore_missing=True
        )
        self.assertEqual(expected_email, found)

    def test_update_project_without_tags(self):
        """
        Tests that the params and result are forwarded as-is to/from the
        update_project API
        """
        mock_project = self.MockProject(tags=[])
        self.identity_api.find_project.return_value = mock_project

        expected_details = ProjectDetails(
            name=NonCallableMock(),
            email="Test@Test.com",
            description=NonCallableMock(),
            is_enabled=NonCallableMock(),
        )

        result = self.instance.update_project(
            cloud_account="test",
            project_identifier="ProjectID",
            project_details=expected_details,
        )

        self.mocked_connection.assert_called_with("test")
        mock_project.set_tags.assert_called_once_with(
            self.identity_api, [expected_details.email]
        )

        assert result == self.identity_api.update_project.return_value
        self.identity_api.update_project.assert_called_once_with(
            project=mock_project,
            name=expected_details.name,
            description=expected_details.description,
            is_enabled=expected_details.is_enabled,
            tags=[expected_details.email],
        )

    def test_update_project_with_tags(self):
        """
        Tests that the params and result are forwarded as-is to/from the
        update_project API
        """
        mock_project = self.MockProject(tags=["sometag", "anothertag"])
        self.identity_api.find_project.return_value = mock_project

        expected_details = ProjectDetails(
            name=NonCallableMock(),
            email="Test@Test.com",
            description=NonCallableMock(),
            is_enabled=NonCallableMock(),
        )

        result = self.instance.update_project(
            cloud_account="test",
            project_identifier="ProjectID",
            project_details=expected_details,
        )

        self.mocked_connection.assert_called_with("test")
        mock_project.set_tags.assert_called_once_with(
            self.identity_api, ["sometag", "anothertag", expected_details.email]
        )

        assert result == self.identity_api.update_project.return_value
        self.identity_api.update_project.assert_called_once_with(
            project=mock_project,
            name=expected_details.name,
            description=expected_details.description,
            is_enabled=expected_details.is_enabled,
            tags=["sometag", "anothertag", expected_details.email],
        )

    def test_update_project_email(self):
        """
        Tests that the params and result are forwarded as-is to/from the
        update_project API
        """
        mock_project = self.MockProject(
            tags=["sometag", "existing@email.com", "anothertag"]
        )

        self.identity_api.find_project.return_value = mock_project

        expected_details = ProjectDetails(
            name="",
            email="new@email.com",
            description="",
        )

        result = self.instance.update_project(
            cloud_account="test",
            project_identifier="ProjectID",
            project_details=expected_details,
        )

        self.mocked_connection.assert_called_with("test")
        mock_project.set_tags.assert_called_once_with(
            self.identity_api, ["sometag", expected_details.email, "anothertag"]
        )

        assert result == self.identity_api.update_project.return_value
        self.identity_api.update_project.assert_called_once_with(
            project=mock_project,
            tags=["sometag", expected_details.email, "anothertag"],
        )
