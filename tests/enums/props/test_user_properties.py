from unittest.mock import patch
from parameterized import parameterized
from enums.query.props.user_properties import UserProperties
from nose.tools import raises

from exceptions.parse_query_error import ParseQueryError
from exceptions.query_property_mapping_error import QueryPropertyMappingError
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@parameterized(list(UserProperties))
def test_get_prop_func(prop):
    """
    Tests that all user properties have a property function mapping
    """
    UserProperties.get_prop_func(prop)


@raises(QueryPropertyMappingError)
def test_get_prop_func_invalid():
    """
    Tests that get_prop_func_invalid returns Error if property not supported
    """
    UserProperties.get_prop_func(MockProperties.PROP_1)


@patch("enums.query.props.user_properties.UserProperties.get_prop_func")
def test_get_marker_prop_func(mock_get_prop_func):
    """
    Tests that marker_prop_func returns get_prop_func called with USER_ID
    """
    val = UserProperties.get_marker_prop_func()
    mock_get_prop_func.assert_called_once_with(UserProperties.USER_ID)
    assert val == mock_get_prop_func.return_value


@parameterized(["user_domain_id", "User_Domain_ID", "UsEr_DoMaIn_iD"])
def test_user_domain_id_serialization(val):
    """
    Tests that variants of USER_DOMAIN_ID can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_DOMAIN_ID


@parameterized(["USER_EMAIL", "User_Email", "UsEr_EmAiL"])
def test_user_email_serialization(val):
    """
    Tests that variants of USER_EMAIL can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_EMAIL


@parameterized(["USER_DESCRIPTION", "User_Description", "UsEr_DeScRiPtIoN"])
def test_user_description_serialization(val):
    """
    Tests that variants of USER_DESCRIPTION can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_DESCRIPTION


@parameterized(["USER_NAME", "User_Name", "UsEr_NaMe"])
def test_user_name_serialization(val):
    """
    Tests that variants of USER_NAME can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_NAME


@raises(ParseQueryError)
def test_invalid_serialization():
    """
    Tests that error is raised when passes invalid string to all preset classes
    """
    UserProperties.from_string("some-invalid-string")
