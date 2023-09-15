from unittest.mock import patch

from enums.query.props.user_properties import UserProperties
from openstack_query.queries.user_query import UserQuery


def test_user_query_enum_type():
    """
    Checks that server query returns the correct PropEnum type
    """
    assert UserQuery().prop_mapping == UserProperties


def test_user_query_runner_is_initialized():
    """
    Checks that server query runner is initialized
    with the correct prop_mapping
    """
    with patch("openstack_query.queries.user_query.UserRunner") as constructor:
        runner = UserQuery().query_runner

    constructor.assert_called_with(UserProperties)
    assert runner == constructor.return_value
