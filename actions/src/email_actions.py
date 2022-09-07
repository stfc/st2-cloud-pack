from dataclasses import dataclass
from typing import Callable, Dict, List, Union
from email_api.email_api import EmailApi
from email_api.email_helpers import EmailHelpers
from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from openstack_api.openstack_image import OpenstackImage
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_server import OpenstackServer

from st2common.runners.base_action import Action

from structs.email_query_params import EmailQueryParams

from structs.email_params import EmailParams


class EmailActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        super().__init__(*args, config=config, **kwargs)
        self._api = config.get("email_api", EmailApi())
        self._server_api: OpenstackServer = config.get(
            "openstack_server_api", OpenstackServer()
        )
        self._floating_ip_api: OpenstackServer = config.get(
            "openstack_floating_ip_api", OpenstackFloatingIP()
        )
        self._image_api: OpenstackImage = config.get(
            "openstack_image_api", OpenstackImage()
        )
        self._query_api: OpenstackQuery = config.get(
            "openstack_query_api", OpenstackQuery()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint:disable=too-many-arguments
    def send_email(
        self,
        subject: str,
        email_to: List[str],
        email_from: str,
        email_cc: List[str],
        header: str,
        footer: str,
        body: str,
        attachment_filepaths: List[str],
        smtp_account: str,
        send_as_html: bool,
    ):
        """
        Sends an email
        :param: subject (String): Subject of the email
        :param: email_to (List[String]): Email addresses to send the email to
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: send_as_html (Bool): If true will send in HTML format
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        email_params = EmailParams(
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            attachment_filepaths=attachment_filepaths,
            test_override=False,
            test_override_email=[""],
            send_as_html=send_as_html,
        )

        return self._api.send_email(
            smtp_account=EmailHelpers.load_smtp_account(self.config, smtp_account),
            email_params=email_params,
            email_to=email_to,
            body=body,
        )

    # pylint:disable=too-many-arguments,too-many-locals
    def email_server_users(
        self,
        cloud_account: str,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        subject: str,
        email_from: str,
        email_cc: List[str],
        header: str,
        footer: str,
        attachment_filepaths: List[str],
        smtp_account: str,
        test_override: bool,
        test_override_email: List[str],
        send_as_html: bool,
        **kwargs,
    ):
        """
        Finds all servers matching a query and then sends emails to their users
        :param: cloud_account: The account from the clouds configuration to use
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: query_preset: The query to use when searching for servers
        :param: message: Message to add to the body of emails sent
        :param: properties_to_select: The list of properties to select and output from the found servers
        :param: subject (String): Subject of the emails
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: test_override (Boolean): send all emails to test emails
        :param: test_override_email (List[String]): send to this email if test_override enabled
        :param: send_as_html (Bool): If true will send in HTML format
        :return:
        """

        email_params = EmailParams(
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            attachment_filepaths=attachment_filepaths,
            test_override=test_override,
            test_override_email=test_override_email,
            send_as_html=send_as_html,
        )

        self._server_api.email_users(
            cloud_account=cloud_account,
            smtp_account=EmailHelpers.load_smtp_account(self.config, smtp_account),
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
            email_params=email_params,
            **kwargs,
        )

    # pylint:disable=too-many-arguments,too-many-locals
    def email_floating_ip_users(
        self,
        cloud_account: str,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        subject: str,
        email_from: str,
        email_cc: List[str],
        header: str,
        footer: str,
        attachment_filepaths: List[str],
        smtp_account: str,
        test_override: bool,
        test_override_email: List[str],
        send_as_html: bool,
        **kwargs,
    ):
        """
        Finds all floating ips matching a query and then sends emails to their project's contact
        :param: cloud_account: The account from the clouds configuration to use
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: query_preset: The query to use when searching for floating ips
        :param: message: Message to add to the body of emails sent
        :param: properties_to_select: The list of properties to select and output from the found servers
        :param: subject (String): Subject of the emails
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: test_override (Boolean): send all emails to test emails
        :param: test_override_email (List[String]): send to this email if test_override enabled
        :param: send_as_html (Bool): If true will send in HTML format
        :return:
        """

        email_params = EmailParams(
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            attachment_filepaths=attachment_filepaths,
            test_override=test_override,
            test_override_email=test_override_email,
            send_as_html=send_as_html,
        )

        self._floating_ip_api.email_users(
            cloud_account=cloud_account,
            smtp_account=EmailHelpers.load_smtp_account(self.config, smtp_account),
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
            email_params=email_params,
            **kwargs,
        )

    # pylint:disable=too-many-arguments,too-many-locals
    def email_image_users(
        self,
        cloud_account: str,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        subject: str,
        email_from: str,
        email_cc: List[str],
        header: str,
        footer: str,
        attachment_filepaths: List[str],
        smtp_account: str,
        test_override: bool,
        test_override_email: List[str],
        send_as_html: bool,
        **kwargs,
    ):
        """
        Finds all images matching a query and then sends emails to their project's contact
        :param: cloud_account: The account from the clouds configuration to use
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: query_preset: The query to use when searching for images
        :param: message: Message to add to the body of emails sent
        :param: properties_to_select: The list of properties to select and output from the found servers
        :param: subject (String): Subject of the emails
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: test_override (Boolean): send all emails to test emails
        :param: test_override_email (List[String]): send to this email if test_override enabled
        :param: send_as_html (Bool): If true will send in HTML format
        :return:
        """

        email_params = EmailParams(
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            attachment_filepaths=attachment_filepaths,
            test_override=test_override,
            test_override_email=test_override_email,
            send_as_html=send_as_html,
        )

        self._image_api.email_users(
            cloud_account=cloud_account,
            smtp_account=EmailHelpers.load_smtp_account(self.config, smtp_account),
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
            email_params=email_params,
            **kwargs,
        )
