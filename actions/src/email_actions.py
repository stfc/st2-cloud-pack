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

    def send_email(self, **kwargs):
        """
        Sends an email
        :param kwargs: arguments for openstack actions
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        if "body" in kwargs and kwargs["body"]:
            return self._api.send_email(self.config, **kwargs)

    # pylint:disable=too-many-arguments
    def send_server_emails(
        self,
        cloud_account: str,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        **kwargs,
    ):
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all servers)
        :param query_preset: The query to use when searching for servers
        :param message: Message to add to the body of emails sent
        :param properties_to_select: The list of properties to select and output from the found servers
        :param get_html: When True tables returned are in html format
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
            True,
        )

        for key, value in emails.items():
            emails[key] = message + "<br><br>" + value

        self._api.send_emails(self.config, emails, send_as_html=True, **kwargs)
