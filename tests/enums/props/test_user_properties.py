import pytest


from enums.query.props.user_properties import UserProperties


@pytest.mark.parametrize("val", ["user_domain_id", "User_Domain_ID", "UsEr_DoMaIn_iD"])
def test_user_domain_id_serialization(val):
    """
    Tests that variants of USER_DOMAIN_ID can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_DOMAIN_ID


@pytest.mark.parametrize("val", ["USER_EMAIL", "User_Email", "UsEr_EmAiL"])
def test_user_email_serialization(val):
    """
    Tests that variants of USER_EMAIL can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_EMAIL


@pytest.mark.parametrize("val", ["USER_DESCRIPTION", "User_Description", "UsEr_DeScRiPtIoN"])
def test_user_description_serialization(val):
    """
    Tests that variants of USER_DESCRIPTION can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_DESCRIPTION


@pytest.mark.parametrize("val", ["USER_NAME", "User_Name", "UsEr_NaMe"])
def test_user_name_serialization(val):
    """
    Tests that variants of USER_NAME can be serialized
    """
    assert UserProperties.from_string(val) is UserProperties.USER_NAME
