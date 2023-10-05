from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsString
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.mappings.user_mapping import UserMapping
from openstack_query.runners.user_runner import UserRunner


def test_get_runner_mapping():
    """
    Tests get runner mapping returns a user runner
    """
    assert UserMapping.get_runner_mapping() == UserRunner


def test_get_prop_mapping():
    """
    Tests get prop mapping returns a server properties
    """
    assert UserMapping.get_prop_mapping() == UserProperties


def test_get_server_side_handler_returns_correct_type():
    """
    Tests get server side handler returns a server side handler
    """
    assert isinstance(UserMapping.get_server_side_handler(), ServerSideHandler)


def test_server_side_handler_mappings_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for equal to params
    """
    mappings = {
        UserProperties.USER_DOMAIN_ID: "domain_id",
        UserProperties.USER_NAME: "name",
        UserProperties.USER_ID: "id",
    }

    server_side_test_mappings(
        UserMapping.get_server_side_handler(),
        UserMapping.get_client_side_handlers().generic_handler,
        QueryPresetsGeneric.EQUAL_TO,
        mappings,
    )


def test_client_side_handlers_generic(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for generic presets
    """
    handler = UserMapping.get_client_side_handlers().generic_handler
    mappings = {
        QueryPresetsGeneric.EQUAL_TO: ["*"],
        QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_string(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for string presets
    """
    handler = UserMapping.get_client_side_handlers().string_handler
    mappings = {
        QueryPresetsString.MATCHES_REGEX: [
            UserProperties.USER_EMAIL,
            UserProperties.USER_NAME,
        ]
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_integer():
    """
    Tests client side handler mappings are correct
    shouldn't create an integer handler because there are no integer related properties for User
    """
    handler = UserMapping.get_client_side_handlers().integer_handler
    assert not handler


def test_client_side_handlers_datetime():
    """
    Tests client side handler mappings are correct
    shouldn't create a datetime handler because there are no datetime related properties for User
    """
    handler = UserMapping.get_client_side_handlers().datetime_handler
    assert not handler
