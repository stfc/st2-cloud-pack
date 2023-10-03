import pytest
from enums.cloud_domains import CloudDomains


@pytest.mark.parametrize("domain", ["prod", "PROD", "PrOD"])
def test_prod_serialization(domain):
    """
    Tests that variants of STFC can be serialized
    """
    assert CloudDomains.from_string(domain) is CloudDomains.PROD


@pytest.mark.parametrize("domain", ["dev", "DeV", "DEV"])
def test_dev_serialization(domain):
    """
    Tests that variants of DEFAULT can be serialized
    """
    assert CloudDomains.from_string(domain) is CloudDomains.DEV
