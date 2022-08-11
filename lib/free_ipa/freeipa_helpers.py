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
            users.append(base_username + str(i))
        return users
