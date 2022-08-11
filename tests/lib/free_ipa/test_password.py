from unittest.mock import patch

from free_ipa.password import generate_password


def test_secret_module_used():
    with patch("free_ipa.password.secrets") as patched_secrets:
        returned = generate_password(10)
        patched_secrets.token_urlsafe.assert_called_once_with(10)
        assert returned == patched_secrets.token_urlsafe.return_value
