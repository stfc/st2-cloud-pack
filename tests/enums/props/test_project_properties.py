from unittest.mock import patch

from enums.query.props.project_properties import ProjectProperties
import pytest

from exceptions.query_property_mapping_error import QueryPropertyMappingError
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.mark.parametrize("prop", list(ProjectProperties))
def test_get_prop_mapping(prop):
    """
    Tests that all project properties have a property function mapping
    """
    ProjectProperties.get_prop_mapping(prop)


def test_get_prop_mapping_invalid():
    """
    Tests that get_prop_mapping returns Error if property not supported
    """
    with pytest.raises(QueryPropertyMappingError):
        ProjectProperties.get_prop_mapping(MockProperties.PROP_1)


@patch("enums.query.props.project_properties.ProjectProperties.get_prop_mapping")
def test_get_marker_prop_func(mock_get_prop_mapping):
    """
    Tests that marker_prop_func returns get_prop_mapping called with FLAVOR_ID
    """
    val = ProjectProperties.get_marker_prop_func()
    mock_get_prop_mapping.assert_called_once_with(ProjectProperties.PROJECT_ID)
    assert val == mock_get_prop_mapping.return_value


@pytest.mark.parametrize(
    "val", ["project_description", "Project_Description", "PrOjEcT_DeScRiPtIoN"]
)
def test_project_description_serialization(val):
    """
    Tests that variants of PROJECT_DESCRIPTION can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_DESCRIPTION


@pytest.mark.parametrize(
    "val", ["project_domain_id", "Project_Domain_Id", "PrOjEcT_DoMaIn_Id"]
)
def test_project_domain_id_serialization(val):
    """
    Tests that variants of PROJECT_DOMAIN_ID can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_DOMAIN_ID


@pytest.mark.parametrize("val", ["project_id", "Project_Id", "PrOjEcT_Id"])
def test_project_id_serialization(val):
    """
    Tests that variants of PROJECT_ID can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_ID


@pytest.mark.parametrize(
    "val", ["project_is_domain", "Project_Is_Domain", "PrOjEcT_Is_DoMaIn"]
)
def test_project_is_domain_serialization(val):
    """
    Tests that variants of PROJECT_IS_DOMAIN can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_IS_DOMAIN


@pytest.mark.parametrize(
    "val", ["project_is_enabled", "Project_Is_Enabled", "PrOjEcT_Is_EnAbLeD"]
)
def test_project_is_enabled_serialization(val):
    """
    Tests that variants of PROJECT_IS_ENABLED can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_IS_ENABLED


@pytest.mark.parametrize("val", ["project_name", "Project_Name", "PrOjEcT_NaMe"])
def test_project_name_serialization(val):
    """
    Tests that variants of PROJECT_NAME can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_NAME


@pytest.mark.parametrize(
    "val", ["project_parent_id", "Project_Parent_Id", "PrOjEcT_PaReNt_Id"]
)
def test_project_parent_id_serialization(val):
    """
    Tests that variants of PROJECT_NAME can be serialized
    """
    assert ProjectProperties.from_string(val) is ProjectProperties.PROJECT_PARENT_ID
