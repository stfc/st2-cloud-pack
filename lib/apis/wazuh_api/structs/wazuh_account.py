from dataclasses import dataclass, fields
from typing import Dict
import requests
from keepercommander.service.util import api_key


@dataclass
class WazuhAccount:
    """
    Wazuh account Parameters.
    :param api_username: Wazuh API username
    :param api_password: Wazuh API password
    :param indexer_username: Wazuh Indexer username
    :param indexer_password: Wazuh Indexer password
    :param api_endpoint: Wazuh API endpoint url
    :param indexer_endpoint: Wazuh Indexer endpoint url
    """

    api_username: str
    api_password: str
    api_endpoint: str

    indexer_username: str
    indexer_password: str
    indexer_endpoint: str

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(WazuhAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return WazuhAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, wazuh_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param wazuh_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have wazuh_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) Wazuh account names and properties
        """
        wazuh_accounts_config = pack_config.get("wazuh_accounts", None)

        if wazuh_accounts_config is None:
            raise ValueError("Pack config must contain the 'wazuh_accounts' field")

        try:
            key_value = {config["name"]: config for config in wazuh_accounts_config}
            account_data = key_value[wazuh_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {wazuh_account_name} does not appear in the configuration"
            ) from exc

        return WazuhAccount.from_dict(account_data)

    def get_api_token(self) -> str:
        """
        Authenticates with the Wazuh API and returns a JWT token.
        returns: API JWT token
        """
        url = f"{self.api_endpoint}/security/user/authenticate"
        try:
            # Wazuh uses Basic Auth to fetch the initial token
            response = requests.get(
                url, auth=(self.api_username, self.api_password), verify=False, timeout=60
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError("Unable to retrieve a valid token: %s") from e
        try:
            token = response.json()["data"]["token"]
        except (KeyError, TypeError, requests.exceptions.JSONDecodeError) as e:
            raise RuntimeError("Wazuh API response did not contain a token") from e
        return token
