from enums.query.props.flavor_properties import FlavorProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsString,
    QueryPresetsInteger,
)
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.mappings.flavor_mapping import FlavorMapping
from openstack_query.runners.flavor_runner import FlavorRunner


def test_get_runner_mapping():
    """
    Tests get runner mapping returns a server runner
    """
    assert FlavorMapping.get_runner_mapping() == FlavorRunner


def test_get_prop_mapping():
    """
    Tests get prop mapping returns a server properties
    """
    assert FlavorMapping.get_prop_mapping() == FlavorProperties


def test_get_server_side_handler_returns_correct_type():
    """
    Tests get server side handler returns a server side handler
    """
    assert isinstance(FlavorMapping.get_server_side_handler(), ServerSideHandler)


def test_server_side_handler_mappings_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for equal to params
    """
    mappings = {FlavorProperties.FLAVOR_IS_PUBLIC: "is_public"}
    server_side_test_mappings(
        FlavorMapping.get_server_side_handler(),
        FlavorMapping.get_client_side_handlers().generic_handler,
        QueryPresetsGeneric.EQUAL_TO,
        mappings,
        test_case=(True, True),
    )


def test_server_side_handler_less_than_or_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for less_than_or_equal_to params
    """
    mappings = {
        FlavorProperties.FLAVOR_DISK: "minDisk",
        FlavorProperties.FLAVOR_RAM: "minRam",
    }
    server_side_test_mappings(
        FlavorMapping.get_server_side_handler(),
        FlavorMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO,
        mappings,
        (10, 10),
    )

    # with strings which can convert to ints
    server_side_test_mappings(
        FlavorMapping.get_server_side_handler(),
        FlavorMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO,
        mappings,
        ("10", 10),
    )

    # with floats which can convert to ints
    server_side_test_mappings(
        FlavorMapping.get_server_side_handler(),
        FlavorMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO,
        mappings,
        (10.0, 10),
    )


def test_server_side_handler_not_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for not_equal_to params
    """
    mappings = {
        FlavorProperties.FLAVOR_IS_PUBLIC: "is_public",
    }
    server_side_test_mappings(
        FlavorMapping.get_server_side_handler(),
        FlavorMapping.get_client_side_handlers().generic_handler,
        QueryPresetsGeneric.NOT_EQUAL_TO,
        mappings,
        (True, False),
    )


def test_client_side_handlers_generic(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for generic presets
    """
    handler = FlavorMapping.get_client_side_handlers().generic_handler
    mappings = {
        QueryPresetsGeneric.EQUAL_TO: ["*"],
        QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
        QueryPresetsGeneric.ANY_IN: ["*"],
        QueryPresetsGeneric.NOT_ANY_IN: ["*"],
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_string(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for string presets
    """
    handler = FlavorMapping.get_client_side_handlers().string_handler
    mappings = {QueryPresetsString.MATCHES_REGEX: [FlavorProperties.FLAVOR_NAME]}
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_datetime():
    """
    Tests client side handler mappings are correct, and line up to the expected
    shouldn't create a datetime handler because there are no datetime related properties for Flavor
    """
    handler = FlavorMapping.get_client_side_handlers().datetime_handler
    assert not handler


def test_client_side_handlers_integer(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for integer presets
    """
    integer_prop_list = [
        FlavorProperties.FLAVOR_RAM,
        FlavorProperties.FLAVOR_DISK,
        FlavorProperties.FLAVOR_EPHEMERAL,
        FlavorProperties.FLAVOR_SWAP,
        FlavorProperties.FLAVOR_VCPU,
    ]
    handler = FlavorMapping.get_client_side_handlers().integer_handler
    mappings = {
        QueryPresetsInteger.LESS_THAN: integer_prop_list,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: integer_prop_list,
        QueryPresetsInteger.GREATER_THAN: integer_prop_list,
        QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: integer_prop_list,
    }
    client_side_test_mappings(handler, mappings)
