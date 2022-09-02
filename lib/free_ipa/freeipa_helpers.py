import secrets
from typing import List


class FreeIpaHelpers:
    @staticmethod
    def generate_users(
        base_username: str, start_index: int, end_index: int
    ) -> List[str]:
        """
        Generates a list of username strings, including the final index
        :param base_username: The base name without the hypen
        :param start_index: The first user to generate
        :param end_index: The last user ID to generate, inclusive
        :return: The list of usernames
        """
        users = []
        for i in range(start_index, end_index + 1):
            users.append(f"{base_username}-{i}")
        return users

    @staticmethod
    def generate_password(num_of_passwords: int, password_length: int) -> List[str]:
        """
        Generate a random password
        :param num_of_passwords: The number of passwords to generate
        :param password_length: Length of the password
        :return: Random password
        """
        return [secrets.token_urlsafe(password_length) for _ in range(num_of_passwords)]
