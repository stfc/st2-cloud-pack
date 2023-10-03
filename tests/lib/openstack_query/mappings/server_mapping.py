from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import QueryPresetsGeneric
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.mappings.server_mapping import ServerMapping
from openstack_query.runners.server_runner import ServerRunner


def test_get_runner_mapping():
    """
    Tests get runner mapping returns a server runner
    """
    assert ServerMapping.get_runner_mapping() == ServerRunner


def test_get_prop_mapping():
    """
    Tests get prop mapping returns a server properties
    """
    assert ServerMapping.get_prop_mapping() == ServerProperties


def test_get_server_side_handler_returns_correct_type():
    """
    Tests get server side handler returns a server side handler
    """
    assert isinstance(ServerMapping.get_server_side_handler(), ServerSideHandler)


def test_server_side_handler_mappings_equal_to():
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for equal to params
    """
    handler = ServerMapping.get_server_side_handler()
    mappings = {
        ServerProperties.USER_ID: "user_id",
        ServerProperties.SERVER_ID: "uuid",
        ServerProperties.SERVER_NAME: "hostname",
        ServerProperties.SERVER_STATUS: "vm_state",
        ServerProperties.SERVER_DESCRIPTION: "description",
        ServerProperties.PROJECT_ID: "project_id",
    }

    supported_props = handler.get_supported_props(QueryPresetsGeneric.EQUAL_TO)
    assert all(key_to_check in supported_props for key_to_check in mappings.keys())
    for prop, expected in mappings.items():
        filter = handler.get_filters(
            QueryPresetsGeneric.EQUAL_TO, prop, {"value": "test"}
        )
        assert filter == {expected: "test"}
