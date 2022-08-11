import secrets


def generate_password(password_length: int) -> str:
    """
    Generate a random password
    :param password_length: Length of the password
    :return: Random password
    """
    return secrets.token_urlsafe(password_length)
