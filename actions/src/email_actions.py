from typing import Callable, Dict, List
from email_api.email_api import EmailApi
from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_server import OpenstackServer

from st2common.runners.base_action import Action


class EmailActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        super().__init__(*args, config=config, **kwargs)
        self._api: EmailApi = config.get("email_api", EmailApi())
        self._server_api: OpenstackServer = config.get(
            "openstack_server_api", OpenstackServer()
        )
        self._floating_ip_api: OpenstackServer = config.get(
            "openstack_floating_ip_api", OpenstackFloatingIP()
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
        return self._api.send_email(
            smtp_accounts=self.config.get("smtp_accounts", None),
            subject=subject,
            email_to=email_to,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            body=body,
            attachment_filepaths=attachment_filepaths,
            smtp_account=smtp_account,
            send_as_html=send_as_html,
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
        :param: project_identifier: The project this applies to (or empty for all servers)
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
        if "user_email" not in properties_to_select:
            raise ValueError("properties_to_select must contain 'user_email'")

        # Ensure only a valid query preset is used when there is no project
        # (try and prevent mistakenly emailing loads of people)
        if project_identifier == "":
            if query_preset not in OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT:
                raise ValueError(
                    f"project_identifier needed for the query type '{query_preset}'"
                )

        servers = self._server_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        emails = self._query_api.parse_and_output_table(
            cloud_account=cloud_account,
            items=servers,
            object_type="server",
            properties_to_select=properties_to_select,
            group_by="user_email",
            get_html=send_as_html,
        )

        for key, value in emails.items():
            separator = "<br><br>" if send_as_html else "\n\n"
            emails[key] = f"{message}{separator}{value}"

        return self._api.send_emails(
            smtp_accounts=self.config.get("smtp_accounts", None),
            emails=emails,
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            attachment_filepaths=attachment_filepaths,
            smtp_account=smtp_account,
            test_override=test_override,
            test_override_email=test_override_email,
            send_as_html=send_as_html,
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
        :param: project_identifier: The project this applies to (or empty for all servers)
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
        if "project_email" not in properties_to_select:
            raise ValueError("properties_to_select must contain 'project_email'")

        # Ensure only a valid query preset is used when there is no project
        # (try and prevent mistakenly emailing loads of people)
        if project_identifier == "":
            if query_preset not in OpenstackFloatingIP.SEARCH_QUERY_PRESETS_NO_PROJECT:
                raise ValueError(
                    f"project_identifier needed for the query type '{query_preset}'"
                )

        floating_ips = self._floating_ip_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        emails = self._query_api.parse_and_output_table(
            cloud_account=cloud_account,
            items=floating_ips,
            object_type="floating_ip",
            properties_to_select=properties_to_select,
            group_by="project_email",
            get_html=send_as_html,
        )

        for key, value in emails.items():
            separator = "<br><br>" if send_as_html else "\n\n"
            emails[key] = f"{message}{separator}{value}"

        return self._api.send_emails(
            smtp_accounts=self.config.get("smtp_accounts", None),
            emails=emails,
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            attachment_filepaths=attachment_filepaths,
            smtp_account=smtp_account,
            test_override=test_override,
            test_override_email=test_override_email,
            send_as_html=send_as_html,
        )
