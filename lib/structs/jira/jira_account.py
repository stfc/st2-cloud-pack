from dataclasses import dataclass, fields
from typing import Dict


@dataclass
class JiraAccount:
    """
    Jira account Parameters dictating config info dictating how to create an issue.
    :param username: Atlassian username
    :param api_token: Atlassian Token
    :param atlassian_endpoint: Atlassian server name to use
    """

    username: str
    api_token: str
    atlassian_endpoint: str

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(JiraAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return JiraAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, jira_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param jira_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have jira_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) Jira account names and properties
        """
        jira_accounts_config = pack_config.get("jira_accounts", None)

        if jira_accounts_config is None:
            raise ValueError("Pack config must contain the 'jira_accounts' field")

        try:
            key_value = {config["name"]: config for config in jira_accounts_config}
            account_data = key_value[jira_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {jira_account_name} does not appear in the configuration"
            ) from exc

        return JiraAccount.from_dict(account_data)
