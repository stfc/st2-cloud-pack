from dataclasses import dataclass, fields
from typing import Dict
from requests.auth import HTTPBasicAuth


@dataclass
class AlertManagerAccount:
    """
    AlertManager account Parameters dictating config info for interacting with AlertManager.
    :param username: AlertManager username
    :param password: AlertManager password
    :param alertmanager_endpoint: AlertManager API endpoint
    """

    username: str
    password: str
    alertmanager_endpoint: str

    @property
    def auth(self):
        return HTTPBasicAuth(self.username, self.password)

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(AlertManagerAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return AlertManagerAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, alertmanager_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param alertmanager_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have alertmanager_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: alertmanager account names and properties
        :rtype: dictionary
        """
        alertmanager_accounts_config = pack_config.get("alertmanager_accounts", None)

        if alertmanager_accounts_config is None:
            raise ValueError(
                "Pack config must contain the 'alertmanager_accounts' field"
            )

        try:
            key_value = {
                config["name"]: config for config in alertmanager_accounts_config
            }
            account_data = key_value[alertmanager_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {alertmanager_account_name} does not appear in the configuration"
            ) from exc

        return AlertManagerAccount.from_dict(account_data)
