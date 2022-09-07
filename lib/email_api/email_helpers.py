from structs.smtp_account import SMTPAccount


class EmailHelpers:
    @staticmethod
    def load_smtp_account(config: dict, smtp_account: str) -> SMTPAccount:
        """
        Loads and returns an SMTPAccount from the pack config
        :param config: The pack config
        :param smtp_account: The account name to get from the config
        :raises KeyError: When the account does not appear in the given config
        :return: (Dictionary) SMTP account names and properties
        """
        smtp_accounts_config = config.get("smtp_accounts", None)

        try:
            key_value = {config["name"]: config for config in smtp_accounts_config}
            account_data = key_value[smtp_account]
        except KeyError as exc:
            raise KeyError(
                f"The account {smtp_account} does not appear in the configuration"
            ) from exc

        return SMTPAccount.from_dict(account_data)
