from typing import List

from openstack_api.dataclasses import QueryParams, EmailQueryParams
from openstack_api.openstack_query_base import OpenstackQueryBase
from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount


# pylint:disable=too-few-public-methods
class OpenstackQueryEmailBase(OpenstackQueryBase):
    """
    Base class for Openstack API wrappers to obtain query and email functionality
    """

    _email_query_params: EmailQueryParams

    def __init__(self, connection_cls, email_query_params: EmailQueryParams):
        super().__init__(connection_cls)
        self._email_query_params = email_query_params

    def _validate_query_params(
        self,
        query_params: QueryParams,
        properties_to_select: List[str],
        project_identifier: str,
        **_,
    ):
        """
        Checks query parameters are valid before searching and emailing users
        :param: query_params: See QueryParams
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: properties_to_select: The list of properties to select and output from the found resources
        :param: kwargs: Additional parameters required for the query_preset chosen
        :raises ValueError: If action_params.required_email_property is not present in properties_to_select
        :raises ValueError: If project_identifier is empty and query_preset is not present in
                            action_params.valid_search_queries_no_project
        """
        if self._email_query_params.required_email_property not in properties_to_select:
            raise ValueError(
                f"properties_to_select must contain '{self._email_query_params.required_email_property}'"
            )

        if (
            query_params.query_preset
            not in self._email_query_params.valid_search_queries
        ):
            raise ValueError(
                f"query_preset is invalid, must be one of {','.join(self._email_query_params.valid_search_queries)}"
            )

        # Ensure only a valid query preset is used when there is no project
        # (try and prevent mistakenly emailing loads of people)
        if project_identifier == "":
            if (
                query_params.query_preset
                not in self._email_query_params.valid_search_queries_no_project
            ):
                raise ValueError(
                    f"project_identifier needed for the query type '{query_params.query_preset}'"
                )

    # pylint:disable=too-many-arguments
    def query_and_email_users(
        self,
        cloud_account: str,
        smtp_account: SMTPAccount,
        query_preset: str,
        properties_to_select: List[str],
        message: str,
        email_params: EmailParams,
        **kwargs,
    ):
        """
        Finds all OpenStack resources matching a query and then sends emails to their users
        :param: cloud_account: The account from the clouds configuration to use
        :param: smtp_account (SMTPAccount): SMTP config
        :param: query_preset: The query to use when searching for servers
        :param: properties_to_select: The list of properties to select and output from the found resources
        :param: message: Message to add to the body of emails sent
        :param: email_params: See EmailParams
        :param: kwargs: Additional parameters required for the query_preset chosen
        :return:
        """
        query_params = QueryParams(
            query_preset=query_preset,
            properties_to_select=properties_to_select,
            group_by=self._email_query_params.required_email_property,
            get_html=email_params.send_as_html,
        )

        self._validate_query_params(
            query_params=query_params,
            properties_to_select=properties_to_select,
            **kwargs,
        )

        result_tables = self.search(
            cloud_account=cloud_account, query_params=query_params, **kwargs
        )

        self._query_api.email_users(
            smtp_account=smtp_account,
            email_params=email_params,
            message=message,
            result_tables=result_tables,
        )
