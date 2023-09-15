from unittest.mock import patch

from enums.query.props.server_properties import ServerProperties
from openstack_query.queries.server_query import ServerQuery


def test_server_query_enum_type():
    """
    Checks that server query returns the correct PropEnum type
    """
    assert ServerQuery().prop_mapping == ServerProperties


def test_server_query_runner_is_initialized():
    """
    Checks that server query runner is initialized
    with the correct prop_mapping
    """
    with patch("openstack_query.queries.server_query.ServerRunner") as constructor:
        runner = ServerQuery().query_runner

    constructor.assert_called_with(ServerProperties)
    assert runner == constructor.return_value
