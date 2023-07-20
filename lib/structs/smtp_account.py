from dataclasses import dataclass, fields
from typing import Dict


@dataclass
class SMTPAccount:
    username: str
    password: str
    server: str
    port: int
    secure: bool
    smtp_auth: bool

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(SMTPAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return SMTPAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, smtp_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param smtp_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have smtp_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) SMTP account names and properties
        """
        smtp_accounts_config = pack_config.get("smtp_accounts", None)

        if smtp_accounts_config is None:
            raise ValueError("Pack config must contain the 'smtp_accounts' field")

        try:
            key_value = {config["name"]: config for config in smtp_accounts_config}
            account_data = key_value[smtp_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {smtp_account_name} does not appear in the configuration"
            ) from exc

        return SMTPAccount.from_dict(account_data)
