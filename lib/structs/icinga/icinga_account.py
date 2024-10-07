from dataclasses import dataclass, fields
from typing import Dict


@dataclass
class IcingaAccount:
    """
    Icinga account Parameters dictating config info for interacting with Icinga.
    :param username: Icinga username
    :param password: Icinga password
    :param icinga_endpoint: Icinga API endpoint
    """

    username: str
    password: str
    icinga_endpoint: str

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(IcingaAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return IcingaAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, icinga_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param icinga_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have icinga_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) icinga account names and properties
        """
        icinga_accounts_config = pack_config.get("icinga_accounts", None)

        if icinga_accounts_config is None:
            raise ValueError("Pack config must contain the 'icinga_accounts' field")

        try:
            key_value = {config["name"]: config for config in icinga_accounts_config}
            account_data = key_value[icinga_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {icinga_account_name} does not appear in the configuration"
            ) from exc

        return IcingaAccount.from_dict(account_data)
