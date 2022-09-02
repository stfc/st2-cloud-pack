from unittest.mock import patch

from free_ipa.freeipa_helpers import FreeIpaHelpers


def test_secret_module_used():
    with patch("free_ipa.freeipa_helpers.secrets") as patched_secrets:
        returned = FreeIpaHelpers.generate_password(1, 10)
        patched_secrets.token_urlsafe.assert_called_once_with(10)
        assert patched_secrets.token_urlsafe.return_value in returned


def test_secret_module_multiple_passwords():
    with patch("free_ipa.freeipa_helpers.secrets") as patched_secrets:
        returned = FreeIpaHelpers.generate_password(3, 10)
        patched_secrets.token_urlsafe.assert_called_with(10)
        assert patched_secrets.token_urlsafe.call_count == 3
        assert patched_secrets.token_urlsafe.return_value in returned
        assert len(returned) == 3


def test_generate_users():
    base_name = "test"
    expected = ["test-5", "test-6", "test-7"]
    returned = FreeIpaHelpers.generate_users(base_name, 5, 7)
    assert expected == returned
