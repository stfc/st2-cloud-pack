import pytest
from enums.user_domains import UserDomains


@pytest.mark.parametrize("domain", ["stfc", "StFC", "STFC"])
def test_stfc_serialization(domain):
    """
    Tests that variants of STFC can be serialized
    """
    assert UserDomains.from_string(domain) is UserDomains.STFC


@pytest.mark.parametrize("domain", ["default", "deFauLt", "DEFAULT"])
def test_default_serialization(domain):
    """
    Tests that variants of DEFAULT can be serialized
    """
    assert UserDomains.from_string(domain) is UserDomains.DEFAULT
