from typing import Any, Callable, Dict
from unittest.mock import create_autospec, NonCallableMock
from email_api.email_api import EmailApi
from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from openstack_api.openstack_image import OpenstackImage

from openstack_api.openstack_server import OpenstackServer
from openstack_api.openstack_query import OpenstackQuery
from src.email_actions import EmailActions
from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount

from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestServerActions(OpenstackActionTestBase):
    """
    Unit tests for the Email.* actions
    """

    action_cls = EmailActions

    def _create_search_api_mock(self, spec):
        # Want to keep mock of __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        mock = create_autospec(spec)
        mock.__getitem__ = spec.__getitem__
        return mock

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.email_mock = create_autospec(EmailApi)
        self.server_mock = self._create_search_api_mock(OpenstackServer)
        self.floating_ip_mock = self._create_search_api_mock(OpenstackFloatingIP)
        self.image_mock = self._create_search_api_mock(OpenstackImage)

        self.query_mock = create_autospec(OpenstackQuery)

        self.action: EmailActions = self.get_action_instance(
            api_mocks={
                "email_api": self.email_mock,
                "openstack_server_api": self.server_mock,
                "openstack_floating_ip_api": self.floating_ip_mock,
                "openstack_image_api": self.image_mock,
                "openstack_query_api": self.query_mock,
            },
        )

        # Assign some mock config
        self.action.config = {
            "smtp_accounts": [
                {
                    "name": "default",
                    "username": "test",
                    "password": "password",
                    "server": "test.server",
                    "port": 123,
                    "secure": False,
                    "smtp_auth": False,
                }
            ]
        }

    def test_send_email(self):
        """
        Tests the action that sends an email
        """
        smtp_account = SMTPAccount.from_dict(self.action.config["smtp_accounts"][0])
        email_params = EmailParams(
            subject=NonCallableMock(),
            email_from=NonCallableMock(),
            email_cc=NonCallableMock(),
            header=NonCallableMock(),
            footer=NonCallableMock(),
            attachment_filepaths=NonCallableMock(),
            send_as_html=NonCallableMock(),
            test_override=False,
            test_override_email=[""],
        )
        email_to = NonCallableMock()
        body = NonCallableMock()
        self.action.send_email(
            subject=email_params.subject,
            email_to=email_to,
            email_from=email_params.email_from,
            email_cc=email_params.email_cc,
            header=email_params.header,
            footer=email_params.footer,
            body=body,
            attachment_filepaths=email_params.attachment_filepaths,
            smtp_account="default",
            send_as_html=email_params.send_as_html,
        )
        self.email_mock.send_email.assert_called_once_with(
            smtp_account=smtp_account,
            email_params=email_params,
            email_to=email_to,
            body=body,
        )

    def _test_email_users(
        self,
        arguments: Dict,
        action_function: Callable,
        search_api_mock: Any,
    ):
        """
        Helper function that checks an email_users action works correctly
        """
        action_function(**arguments)

        smtp_account = SMTPAccount.from_dict(self.action.config["smtp_accounts"][0])
        del arguments["smtp_account"]

        email_params = EmailParams(
            subject=arguments.pop("subject"),
            email_from=arguments.pop("email_from"),
            email_cc=arguments.pop("email_cc"),
            header=arguments.pop("header"),
            footer=arguments.pop("footer"),
            attachment_filepaths=arguments.pop("attachment_filepaths"),
            test_override=arguments.pop("test_override"),
            test_override_email=arguments.pop("test_override_email"),
            send_as_html=arguments.pop("send_as_html"),
        )
        search_api_mock.email_users.assert_called_once_with(
            cloud_account=arguments.pop("cloud_account"),
            smtp_account=smtp_account,
            project_identifier=arguments.pop("project_identifier"),
            query_preset=arguments.pop("query_preset"),
            message=arguments.pop("message"),
            properties_to_select=arguments.pop("properties_to_select"),
            email_params=email_params,
            **arguments
        )

    def test_email_server_users(self):
        """
        Tests the action that sends emails to server users works correctly
        """
        arguments = {
            "cloud_account": "test_account",
            "project_identifier": "test_project",
            "query_preset": "servers_older_than",
            "message": "Message",
            "properties_to_select": ["id", "user_email"],
            "subject": "Subject",
            "email_from": "testemail",
            "email_cc": [],
            "header": "",
            "footer": "",
            "attachment_filepaths": [],
            "smtp_account": "default",
            "test_override": False,
            "test_override_email": [""],
            "send_as_html": False,
            "days": 60,
            "ids": None,
            "names": None,
            "name_snippets": None,
        }
        self._test_email_users(
            arguments, self.action.email_server_users, self.server_mock
        )

    def test_email_floating_ip_users(self):
        """
        Tests the action that sends emails to floating ip project contacts works correctly
        """
        arguments = {
            "cloud_account": "test_account",
            "project_identifier": "test_project",
            "query_preset": "fips_older_than",
            "message": "Message",
            "properties_to_select": ["id", "project_email"],
            "subject": "Subject",
            "email_from": "testemail",
            "email_cc": [],
            "header": "",
            "footer": "",
            "attachment_filepaths": [],
            "smtp_account": "default",
            "test_override": False,
            "test_override_email": [""],
            "send_as_html": False,
            "days": 60,
            "ids": None,
            "names": None,
            "name_snippets": None,
        }
        self._test_email_users(
            arguments, self.action.email_floating_ip_users, self.floating_ip_mock
        )

    def test_email_image_users(self):
        """
        Tests the action that sends emails to image project contacts works correctly
        """
        arguments = {
            "cloud_account": "test_account",
            "project_identifier": "test_project",
            "query_preset": "images_older_than",
            "message": "Message",
            "properties_to_select": ["id", "project_email"],
            "subject": "Subject",
            "email_from": "testemail",
            "email_cc": [],
            "header": "",
            "footer": "",
            "attachment_filepaths": [],
            "smtp_account": "default",
            "test_override": False,
            "test_override_email": [""],
            "send_as_html": False,
            "days": 60,
            "ids": None,
            "names": None,
            "name_snippets": None,
        }
        self._test_email_users(
            arguments, self.action.email_image_users, self.image_mock
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "send_email",
            "email_server_users",
            "email_floating_ip_users",
            "email_image_users",
        ]
        self._test_run_dynamic_dispatch(expected_methods)
