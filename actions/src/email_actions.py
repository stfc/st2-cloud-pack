from dataclasses import dataclass
from typing import Callable, Dict, List, Union
from email_api.email_api import EmailApi
from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from openstack_api.openstack_image import OpenstackImage
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_server import OpenstackServer

from st2common.runners.base_action import Action


class EmailActions(Action):
    @dataclass
    class EmailActionParams:
        """
        Structure containing the information needed to _email_users for a particular OpenstackResource
        :param: required_email_property: The name of the property that must be obtained to get the email of the
                                         user associated with the object. An error is thrown if it is not in the
                                         properties_to_select.
        :param: valid_search_queries_no_project: List of query_preset's that can be run without a project. An error
                                                 will be thrown if one of them is used without a project.
        :param: search_api: API wrapper that contains the search methods that can be used
        :param: object_type: Type of object to be passed to OpenstackQuery's parse_and_output_table function
        :return:
        """

        required_email_property: str
        valid_search_queries_no_project: List[str]
        search_api: Union[OpenstackServer, OpenstackFloatingIP, OpenstackImage]
        object_type: str

    def __init__(self, *args, config: Dict = None, **kwargs):
        super().__init__(*args, config=config, **kwargs)
        self._api: EmailApi = config.get("email_api", EmailApi())
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
    def _email_users(
        self,
        action_params: EmailActionParams,
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
        if action_params.required_email_property not in properties_to_select:
            raise ValueError(
                f"properties_to_select must contain '{action_params.required_email_property}'"
            )

        # Ensure only a valid query preset is used when there is no project
        # (try and prevent mistakenly emailing loads of people)
        if project_identifier == "":
            if query_preset not in action_params.valid_search_queries_no_project:
                raise ValueError(
                    f"project_identifier needed for the query type '{query_preset}'"
                )

        openstack_objects = action_params.search_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        emails = self._query_api.parse_and_output_table(
            cloud_account=cloud_account,
            items=openstack_objects,
            object_type=action_params.object_type,
            properties_to_select=properties_to_select,
            group_by=action_params.required_email_property,
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

        action_params = self.EmailActionParams(
            required_email_property="user_email",
            valid_search_queries_no_project=OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT,
            search_api=self._server_api,
            object_type="server",
        )

        self._email_users(
            action_params=action_params,
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
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
        action_params = self.EmailActionParams(
            required_email_property="project_email",
            valid_search_queries_no_project=OpenstackFloatingIP.SEARCH_QUERY_PRESETS_NO_PROJECT,
            search_api=self._floating_ip_api,
            object_type="floating_ip",
        )

        self._email_users(
            action_params=action_params,
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
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

        action_params = self.EmailActionParams(
            required_email_property="project_email",
            valid_search_queries_no_project=OpenstackImage.SEARCH_QUERY_PRESETS_NO_PROJECT,
            search_api=self._image_api,
            object_type="image",
        )

        self._email_users(
            action_params=action_params,
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
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
            **kwargs,
        )
