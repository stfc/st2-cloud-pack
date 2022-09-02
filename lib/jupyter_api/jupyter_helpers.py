class JupyterHelpers:
    @staticmethod
    def get_token(
        jupyter_env: str,
        jupyter_keys: str,
    ) -> str:
        """
        Returns the appropriate API token based on the Jupyter environment
        :param jupyter_env: The Jupyter environment name
        :param jupyter_keys: Dictionary of Jupyter API tokens
        """
        key_name = None
        env = jupyter_env.casefold()
        if env == "prod".casefold():
            key_name = "prod_token"
        if env == "training".casefold():
            key_name = "training_token"
        if env == "dev".casefold():
            key_name = "dev_token"
        if not key_name:
            raise KeyError("Unknown Jupyter environment")

        token = jupyter_keys[key_name]
        return token
