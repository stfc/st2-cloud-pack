from unittest.mock import patch

from enums.query.props.image_properties import ImageProperties
import pytest

from exceptions.query_property_mapping_error import QueryPropertyMappingError
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.mark.parametrize("prop", list(ImageProperties))
def test_get_prop_mapping(prop):
    """
    Tests that all image properties have a property function mapping
    """
    ImageProperties.get_prop_mapping(prop)


def test_get_prop_mapping_invalid():
    """
    Tests that get_prop_mapping returns Error if property not supported
    """
    with pytest.raises(QueryPropertyMappingError):
        ImageProperties.get_prop_mapping(MockProperties.PROP_1)


@patch("enums.query.props.image_properties.ImageProperties.get_prop_mapping")
def test_get_marker_prop_func(mock_get_prop_mapping):
    """
    Tests that marker_prop_func returns get_prop_mapping called with IMAGE_ID
    """
    val = ImageProperties.get_marker_prop_func()
    mock_get_prop_mapping.assert_called_once_with(ImageProperties.IMAGE_ID)
    assert val == mock_get_prop_mapping.return_value


@pytest.mark.parametrize(
    "val",
    ["image_creation_date", "Image_Creation_Date", "ImAgE_CrEaTiOn_DaTe", "created_at"],
)
def test_image_creation_date_serialization(val):
    """
    Tests that variants of IMAGE_CREATION_DATE can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_CREATION_DATE


@pytest.mark.parametrize(
    "val",
    [
        "image_creation_progress",
        "Image_creation_Progress",
        "ImAgE_CrEaTiOn_PrOgReSs",
        "progress",
    ],
)
def test_image_creation_progress_serialization(val):
    """
    Tests that variants of IMAGE_CREATION_PROGRESS can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_CREATION_PROGRESS


@pytest.mark.parametrize("val", ["image_id", "Image_Id", "ImAgE_Id", "id", "uuid"])
def test_image_id_serialization(val):
    """
    Tests that variants of IMAGE_ID can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_ID


@pytest.mark.parametrize(
    "val",
    [
        "image_last_updated_date",
        "Image_Last_Updated_Date",
        "ImAgE_LaSt_UpDaTeD_DaTe",
        "updated_at",
    ],
)
def test_image_last_updated_date_serialization(val):
    """
    Tests that variants of IMAGE_LAST_UPDATED_DATE can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_LAST_UPDATED_DATE


@pytest.mark.parametrize(
    "val",
    ["image_minimum_ram", "Image_Minimum_RAM", "ImAgE_MiNiMuM_RaM", "min_ram", "ram"],
)
def test_image_minimum_ram_serialization(val):
    """
    Tests that variants of IMAGE_MINIMUM_RAM can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_MINIMUM_RAM


@pytest.mark.parametrize(
    "val",
    [
        "image_minimum_disk",
        "Image_Minimum_Disk",
        "ImAgE_MiNiMuM_DiSk",
        "min_disk",
        "disk",
    ],
)
def test_image_minimum_disk_serialization(val):
    """
    Tests that variants of IMAGE_MINIMUM_DISK can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_MINIMUM_DISK


@pytest.mark.parametrize("val", ["image_name", "Image_Name", "ImAgE_NaMe", "name"])
def test_image_name_serialization(val):
    """
    Tests that variants of IMAGE_NAME can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_NAME


@pytest.mark.parametrize("val", ["image_size", "Image_Size", "ImAgE_SiZe", "size"])
def test_image_size_serialization(val):
    """
    Tests that variants of IMAGE_SIZE can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_SIZE


@pytest.mark.parametrize(
    "val", ["image_status", "Image_Status", "ImAgE_StAtUs", "status"]
)
def test_image_status_serialization(val):
    """
    Tests that variants of IMAGE_STATUS can be serialized
    """
    assert ImageProperties.from_string(val) is ImageProperties.IMAGE_STATUS
