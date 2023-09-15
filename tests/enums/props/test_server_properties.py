from unittest.mock import patch

import pytest

from enums.query.props.server_properties import ServerProperties
from exceptions.parse_query_error import ParseQueryError
from exceptions.query_property_mapping_error import QueryPropertyMappingError
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.mark.parametrize("prop", list(ServerProperties))
def test_get_prop_mapping(prop):
    """
    Tests that all server properties have a property function mapping
    """
    ServerProperties.get_prop_mapping(prop)


def test_get_prop_mapping_invalid():
    """
    Tests that get_prop_mapping returns Error if property not supported
    """
    with pytest.raises(QueryPropertyMappingError):
        ServerProperties.get_prop_mapping(MockProperties.PROP_1)


@patch("enums.query.props.server_properties.ServerProperties.get_prop_mapping")
def test_get_marker_prop_func(mock_get_prop_func):
    """
    Tests that marker_prop_func returns get_prop_mapping called with SERVER_ID
    """
    val = ServerProperties.get_marker_prop_func()
    mock_get_prop_func.assert_called_once_with(ServerProperties.SERVER_ID)
    assert val == mock_get_prop_func.return_value


@pytest.mark.parametrize("val", ["flavor_id", "Flavor_ID", "FlAvOr_Id"])
def test_flavor_id_serialization(val):
    """
    Tests that variants of FLAVOR_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.FLAVOR_ID


@pytest.mark.parametrize("val", ["hypervisor_id", "Hypervisor_ID", "HyPerVisor_ID"])
def test_hypervisor_id_serialization(val):
    """
    Tests that variants of HYPERVISOR_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.HYPERVISOR_ID


@pytest.mark.parametrize("val", ["image_id", "Image_ID", "ImaGe_iD"])
def test_image_id_serialization(val):
    """
    Tests that variants of IMAGE_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.IMAGE_ID


@pytest.mark.parametrize("val", ["project_id", "Project_Id", "PrOjEcT_Id"])
def test_project_id_serialization(val):
    """
    Tests that variants of PROJECT_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.PROJECT_ID


@pytest.mark.parametrize(
    "val", ["server_creation_date", "Server_Creation_Date", "SeRvEr_CrEaTiOn_DAte"]
)
def test_server_creation_date_serialization(val):
    """
    Tests that variants of SERVER_CREATION_DATE can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_CREATION_DATE


@pytest.mark.parametrize(
    "val", ["server_description", "Server_Description", "SeRvEr_DeScrIpTion"]
)
def test_server_description_serialization(val):
    """
    Tests that variants of SERVER_DESCRIPTION can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_DESCRIPTION


@pytest.mark.parametrize("val", ["server_id", "Server_Id", "SeRvEr_iD"])
def test_server_id_serialization(val):
    """
    Tests that variants of SERVER_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_ID


@pytest.mark.parametrize(
    "val",
    [
        "server_last_updated_date",
        "Server_Last_Updated_Date",
        "SerVer_LasT_UpDatED_DaTe",
    ],
)
def test_server_last_updated_date_serialization(val):
    """
    Tests that variants of SERVER_LAST_UPDATED_DATE can be serialized
    """
    assert (
        ServerProperties.from_string(val) is ServerProperties.SERVER_LAST_UPDATED_DATE
    )


@pytest.mark.parametrize("val", ["server_name", "Server_NaMe", "Server_Name"])
def test_server_name_serialization(val):
    """
    Tests that variants of SERVER_NAME can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_NAME


@pytest.mark.parametrize("val", ["server_status", "Server_Status", "SerVer_StAtUs"])
def test_server_status_serialization(val):
    """
    Tests that variants of SERVER_STATUS can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_STATUS


@pytest.mark.parametrize("val", ["user_id", "User_Id", "UsEr_iD"])
def test_user_id_serialization(val):
    """
    Tests that variants of USER_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.USER_ID


def test_invalid_serialization():
    """
    Tests that error is raised when passes invalid string to all preset classes
    """
    with pytest.raises(ParseQueryError):
        ServerProperties.from_string("some-invalid-string")
