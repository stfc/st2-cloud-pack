from structs.smtp_account import SMTPAccount


# pylint:disable=too-few-public-methods
class EmailHelpers:
    @staticmethod
    def load_smtp_account(pack_config: dict, smtp_account: str) -> SMTPAccount:
        """
        Loads and returns an SMTPAccount from the pack config
        :param pack_config: The pack config
        :param smtp_account: The account name to get from the config
        :raises ValueError: When the pack config does not have smtp_accounts defined
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) SMTP account names and properties
        """
        smtp_accounts_config = pack_config.get("smtp_accounts", None)

        if smtp_accounts_config is None:
            raise ValueError("Pack config must contain the 'smtp_accounts' field")

        try:
            key_value = {config["name"]: config for config in smtp_accounts_config}
            account_data = key_value[smtp_account]
        except KeyError as exc:
            raise KeyError(
                f"The account {smtp_account} does not appear in the configuration"
            ) from exc

        return SMTPAccount.from_dict(account_data)
