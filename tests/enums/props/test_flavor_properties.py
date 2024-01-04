from unittest.mock import patch

from enums.query.props.flavor_properties import FlavorProperties
import pytest

from exceptions.query_property_mapping_error import QueryPropertyMappingError
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.mark.parametrize("prop", list(FlavorProperties))
def test_get_prop_mapping(prop):
    """
    Tests that all flavor properties have a property function mapping
    """
    FlavorProperties.get_prop_mapping(prop)


def test_get_prop_mapping_invalid():
    """
    Tests that get_prop_mapping returns Error if property not supported
    """
    with pytest.raises(QueryPropertyMappingError):
        FlavorProperties.get_prop_mapping(MockProperties.PROP_1)


@patch("enums.query.props.flavor_properties.FlavorProperties.get_prop_mapping")
def test_get_marker_prop_func(mock_get_prop_mapping):
    """
    Tests that marker_prop_func returns get_prop_mapping called with FLAVOR_ID
    """
    val = FlavorProperties.get_marker_prop_func()
    mock_get_prop_mapping.assert_called_once_with(FlavorProperties.FLAVOR_ID)
    assert val == mock_get_prop_mapping.return_value


@pytest.mark.parametrize(
    "val",
    [
        "flavor_description",
        "Flavor_Description",
        "FlAvOr_DeScRiPtIoN",
        "description",
        "desc",
    ],
)
def test_flavor_description_serialization(val):
    """
    Tests that variants of FLAVOR_DESCRIPTION can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_DESCRIPTION


@pytest.mark.parametrize(
    "val", ["flavor_disk", "Flavor_Disk", "FlAvOr_DiSk", "disk", "disk_size"]
)
def test_flavor_disk_serialization(val):
    """
    Tests that variants of FLAVOR_DISK can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_DISK


@pytest.mark.parametrize(
    "val",
    [
        "flavor_ephemeral",
        "Flavor_Ephemeral",
        "FlAvOr_EpHeMeRaL",
        "ephemeral",
        "ephemeral_disk",
        "ephemeral_disk_size",
    ],
)
def test_flavor_ephemeral_serialization(val):
    """
    Tests that variants of FLAVOR_EPHEMERAL can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_EPHEMERAL


@pytest.mark.parametrize("val", ["flavor_id", "Flavor_ID", "FlAvOr_Id", "id", "uuid"])
def test_flavor_id_serialization(val):
    """
    Tests that variants of FLAVOR_ID can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_ID


@pytest.mark.parametrize(
    "val",
    ["flavor_is_disabled", "Flavor_Is_Disabled", "Flavor_Is_DiSaBlEd", "is_disabled"],
)
def test_flavor_is_disabled_serialization(val):
    """
    Tests that variants of FLAVOR_IS_DISABLED can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_IS_DISABLED


@pytest.mark.parametrize(
    "val", ["flavor_is_public", "Flavor_Is_Public", "FlAvOr_Is_PuBlIc", "is_public"]
)
def test_flavor_is_public_serialization(val):
    """
    Tests that variants of FLAVOR_IS_PUBLIC can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_IS_PUBLIC


@pytest.mark.parametrize("val", ["flavor_name", "Flavor_Name", "FlAvOr_NaMe", "name"])
def test_flavor_name_serialization(val):
    """
    Tests that variants of FLAVOR_NAME can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_NAME


@pytest.mark.parametrize(
    "val", ["flavor_ram", "Flavor_RAM", "FlAvOr_RaM", "ram", "ram_size"]
)
def test_flavor_ram_serialization(val):
    """
    Tests that variants of FLAVOR_RAM can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_RAM


@pytest.mark.parametrize("val", ["flavor_swap", "Flavor_Swap", "FlAvOr_SwAp"])
def test_flavor_swap_serialization(val):
    """
    Tests that variants of FLAVOR_SWAP can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_SWAP


@pytest.mark.parametrize(
    "val", ["flavor_vcpu", "Flavor_VCPU", "FlAvOr_VcPu", "vcpu", "vcpus"]
)
def test_flavor_vcpu_serialization(val):
    """
    Tests that variants of FLAVOR_VCPU can be serialized
    """
    assert FlavorProperties.from_string(val) is FlavorProperties.FLAVOR_VCPU
