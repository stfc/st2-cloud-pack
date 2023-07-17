from parameterized import parameterized

from enums.query.props.server_properties import ServerProperties


@parameterized(["flavor_id", "Flavor_ID", "FlAvOr_Id"])
def test_flavor_id_serialization(val):
    """
    Tests that variants of FLAVOR_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.FLAVOR_ID


@parameterized(["hypervisor_id", "Hypervisor_ID", "HyPerVisor_ID"])
def test_hypervisor_id_serialization(val):
    """
    Tests that variants of HYPERVISOR_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.HYPERVISOR_ID


@parameterized(["image_id", "Image_ID", "ImaGe_iD"])
def test_image_id_serialization(val):
    """
    Tests that variants of IMAGE_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.IMAGE_ID


@parameterized(["project_id", "Project_Id", "PrOjEcT_Id"])
def test_project_id_serialization(val):
    """
    Tests that variants of PROJECT_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.PROJECT_ID


@parameterized(["server_creation_date", "Server_Creation_Date", "SeRvEr_CrEaTiOn_DAte"])
def test_server_creation_date_serialization(val):
    """
    Tests that variants of SERVER_CREATION_DATE can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_CREATION_DATE


@parameterized(["server_description", "Server_Description", "SeRvEr_DeScrIpTion"])
def test_server_description_serialization(val):
    """
    Tests that variants of SERVER_DESCRIPTION can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_DESCRIPTION


@parameterized(["server_id", "Server_Id", "SeRvEr_iD"])
def test_server_id_serialization(val):
    """
    Tests that variants of SERVER_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_ID


@parameterized(
    ["server_last_updated_date", "Server_Last_Updated_Date", "SerVer_LasT_UpDatED_DaTe"]
)
def test_server_last_updated_date_serialization(val):
    """
    Tests that variants of SERVER_LAST_UPDATED_DATE can be serialized
    """
    assert (
        ServerProperties.from_string(val) is ServerProperties.SERVER_LAST_UPDATED_DATE
    )


@parameterized(["server_name", "Server_NaMe", "Server_Name"])
def test_server_name_serialization(val):
    """
    Tests that variants of SERVER_NAME can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_NAME


@parameterized(["server_status", "Server_Status", "SerVer_StAtUs"])
def test_server_status_serialization(val):
    """
    Tests that variants of SERVER_STATUS can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.SERVER_STATUS


@parameterized(["user_id", "User_Id", "UsEr_iD"])
def test_user_id_serialization(val):
    """
    Tests that variants of USER_ID can be serialized
    """
    assert ServerProperties.from_string(val) is ServerProperties.USER_ID
