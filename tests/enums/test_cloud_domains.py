import pytest


from enums.cloud_domains import CloudDomains


@pytest.mark.parametrize("val", ["prod", "PROD", "PrOD"])
def test_prod_serialization(val):
    """
    Tests that variants of STFC can be serialized
    """
    assert CloudDomains.from_string(val) is CloudDomains.PROD


@pytest.mark.parametrize("val", ["dev", "DeV", "DEV"])
def test_dev_serialization(val):
    """
    Tests that variants of DEFAULT can be serialized
    """
    assert CloudDomains.from_string(val) is CloudDomains.DEV
