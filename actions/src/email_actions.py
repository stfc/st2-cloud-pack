from typing import Callable, Dict, List
from email_api.email_api import EmailApi
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_server import OpenstackServer

from st2common.runners.base_action import Action


class SendEmail(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        super().__init__(*args, config=config, **kwargs)
        self._api: EmailApi = config.get("email_api", EmailApi())
        self._server_api: OpenstackServer = config.get(
            "openstack_api", OpenstackServer()
        )
        self._query_api: OpenstackQuery = config.get("openstack_api", OpenstackQuery())

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
        email_to: str,
        email_from: str,
        email_cc: List[str],
        header: str,
        footer: str,
        body: str,
        attachment_filepaths: List[str],
        smtp_account: str,
        test_override: bool,
        test_override_email: List[str],
        send_as_html: bool,
    ):
        """
        Sends an email
        :param: email_to (List[String]): Email addresses to send the email to
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: header (String): filepath to header file,
        :param: footer (String): filepath to footer file,
        :param: attachment (List): list of attachment filepaths,
        :param: smtp_account (String): email config to use,
        :param: test_override (Boolean): send all emails to test emails
        :param: test_override_email (List[String]): send to this email if test_override enabled
        :param: send_as_html (Bool): If true will send in HTML format
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        return self._api.send_email(
            self.config,
            subject=subject,
            email_to=email_to,
            email_from=email_from,
            email_cc=email_cc,
            header=header,
            footer=footer,
            body=body,
            attachment_filepaths=attachment_filepaths,
            smtp_account=smtp_account,
            test_override=test_override,
            test_override_email=test_override_email,
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
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all servers)
        :param query_preset: The query to use when searching for servers
        :param message: Message to add to the body of emails sent
        :param properties_to_select: The list of properties to select and output from the found servers
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
        servers = self._server_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        if not "user_email" in properties_to_select:
            raise ValueError("properties_to_select must contain 'user_email'")

        # Ensure only a valid query preset is used when there is no project
        # (try and prevent mistakingly emailing loads of people)
        if project_identifier == "":
            if not query_preset in [
                "servers_last_updated_before",
                "servers_older_than",
            ]:
                raise ValueError(
                    f"project_identifier needed for the query type '{query_preset}'"
                )

        emails = self._query_api.parse_and_output_table(
            cloud_account,
            servers,
            "server",
            properties_to_select,
            "user_email",
            send_as_html,
        )

        for key, value in emails.items():
            separator = "<br><br>" if send_as_html else "\n\n"
            emails[key] = f"{message}{separator}{value}"

        return self._api.send_emails(
            self.config,
            emails,
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
