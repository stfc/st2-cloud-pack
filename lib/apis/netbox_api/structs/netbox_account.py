from dataclasses import dataclass, fields
from typing import Dict


@dataclass
class NetboxAccount:
    """
    Netbox account Parameters allowing API calls to be made to netbox.
    :param api_token: Netbox API Token
    :param netbox_endpoint: Netbox endpoint e.g. https://netbox.example.com
    """

    api_token: str
    netbox_endpoint: str

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(NetboxAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return NetboxAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, netbox_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param netbox_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have jira_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) Netbox account names and properties
        """
        netbox_accounts_config = pack_config.get("netbox_accounts", None)

        if netbox_accounts_config is None:
            raise ValueError("Pack config must contain the 'netbox_accounts' field")

        try:
            key_value = {config["name"]: config for config in netbox_accounts_config}
            account_data = key_value[netbox_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {netbox_account_name} does not appear in the configuration"
            ) from exc

        return NetboxAccount.from_dict(account_data)
