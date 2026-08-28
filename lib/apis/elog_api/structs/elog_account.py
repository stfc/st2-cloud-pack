from dataclasses import dataclass, fields
from typing import Dict
from requests import Session


@dataclass
class ElogAccount:
    """
    Elog account Parameters.
    :param username: Elog API username
    :param password: Elog API password
    :param elog_endpoint: Elog API endpoint url
    """

    username: str
    password: str
    elog_endpoint: str

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Returns instance of this dataclass from a dictionary (for loading from config)
        """
        field_set = {field.name for field in fields(ElogAccount) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return ElogAccount(**filtered_arg_dict)

    @staticmethod
    def from_pack_config(pack_config: dict, elog_account_name: str):
        """
        Returns instance of this dataclass from StackStorm pack config
        :param pack_config: The pack config
        :param elog_account_name: The account name to get from the config
        :raises ValueError: When the pack config does not have elog_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) Elog account names and properties
        """
        elog_accounts_config = pack_config.get("elog_accounts", None)

        if elog_accounts_config is None:
            raise ValueError("Pack config must contain the 'elog_accounts' field")

        try:
            key_value = {config["name"]: config for config in elog_accounts_config}
            account_data = key_value[elog_account_name]
        except KeyError as exc:
            raise KeyError(
                f"The account {elog_account_name} does not appear in the configuration"
            ) from exc

        return ElogAccount.from_dict(account_data)

    def authenticate(self) -> Session:
        """
        authenticate against the ELOG server

        This is the equivalent of this curl command to get a cookie
               curl -k -c cookies.txt \
                 --form 'cmd=Login' \
                 --form 'uname=<username>' \
                 --form 'upassword=<password>' \
                 '<ELOG server URL>'
        Using "files" with (None, value) causes requests to send
        multipart/form-data, matching curl --form.

        :return: a session object
        """
        login_data = {
            "cmd": "Login",
            "uname": self.username,
            "upassword": self.password,
        }
        session = Session()
        session.verify = False
        login_response = session.post(
            self.elog_endpoint,
            files={k: (None, v) for k, v in login_data.items()},
        )
        login_response.raise_for_status()
        return session
