from unittest.mock import patch

from free_ipa.freeipa_helpers import FreeIpaHelpers


def test_secret_module_used():
    with patch("free_ipa.freeipa_helpers.secrets") as patched_secrets:
        returned = FreeIpaHelpers.generate_password(10)
        patched_secrets.token_urlsafe.assert_called_once_with(10)
        assert returned == patched_secrets.token_urlsafe.return_value


def test_generate_users():
    base_name = "test"
    expected = ["test5", "test6", "test7"]
    returned = FreeIpaHelpers.generate_users(base_name, 5, 7)
    assert expected == returned
