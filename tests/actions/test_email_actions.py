from unittest.mock import create_autospec, NonCallableMock
from email_api.email_api import EmailApi

from openstack_api.openstack_server import OpenstackServer
from openstack_api.openstack_query import OpenstackQuery
from src.email_actions import EmailActions
from nose.tools import raises

from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestServerActions(OpenstackActionTestBase):
    """
    Unit tests for the Email.* actions
    """

    action_cls = EmailActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.email_mock = create_autospec(EmailApi)
        self.server_mock = create_autospec(OpenstackServer)

        # Want to keep mock of __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.server_mock.__getitem__ = OpenstackServer.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)

        self.action: EmailActions = self.get_action_instance(
            api_mocks={
                "openstack_server_api": self.server_mock,
                "email_api": self.email_mock,
                "openstack_query_api": self.query_mock,
            },
        )

    def test_send_email(self):
        """
        Tests the action that sends an email
        """
        self.action.send_email(
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        self.email_mock.send_email.assert_called_once()

    @raises(ValueError)
    def test_email_server_users_no_email_error(self):
        """
        Tests the action that sends emails to server users gives a value error when user_email
        is not present in the `properties_to_select`
        """
        self.action.email_server_users(
            cloud_account="test_account",
            project_identifier="",
            query_preset="servers_older_than",
            message="Message",
            properties_to_select=["id"],
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            smtp_account="",
            test_override=False,
            test_override_email="",
            send_as_html=False,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    def _email_server_users(self, query_preset: str):
        """
        Helper for checking email_server_users works correctly
        """
        return self.action.email_server_users(
            cloud_account="test_account",
            project_identifier="",
            query_preset=query_preset,
            message="Message",
            properties_to_select=["user_email"],
            subject="Subject",
            email_from="testemail",
            email_cc=[],
            header="",
            footer="",
            attachment_filepaths=[],
            smtp_account="",
            test_override=False,
            test_override_email="",
            send_as_html=False,
            days=60,
            ids=None,
            names=None,
            name_snippets=None,
        )

    def test_email_server_users_no_project(self):
        """
        Tests the action that sends emails to server does not give a value error when project is
        required for the query type
        """

        for query_preset in OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT:
            self._email_server_users(query_preset)

    @raises(ValueError)
    def _check_email_server_users_raises(self, query_preset):
        """
        Helper for checking email_server_users raises a ValueError when needed
        (needed to allow multiple to be checked in the same test otherwise it stops
         after the first error)
        """
        self.assertRaises(ValueError, self._email_server_users(query_preset))

    def test_email_server_users_no_project_error(self):
        """
        Tests the action that sends emails to server users gives a value error when project is
        required for the query type
        """

        # Should raise an error for all but servers_older_than and servers_last_updated_before
        should_pass = OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT
        should_not_pass = OpenstackServer.SEARCH_QUERY_PRESETS
        for x in should_pass:
            should_not_pass.remove(x)

        for query_preset in should_not_pass:
            self._check_email_server_users_raises(query_preset)

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = ["send_email", "email_server_users"]
        self._test_run_dynamic_dispatch(expected_methods)
