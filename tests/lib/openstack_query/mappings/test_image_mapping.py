from unittest.mock import patch, call

from enums.query.props.image_properties import ImageProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsString,
    QueryPresetsInteger,
    QueryPresetsDateTime,
)
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.mappings.image_mapping import ImageMapping
from openstack_query.runners.image_runner import ImageRunner


def test_get_runner_mapping():
    """
    Tests get runner mapping returns ImageRunner
    """
    assert ImageMapping.get_runner_mapping() == ImageRunner


def test_get_prop_mapping():
    """
    Tests get prop mapping returns ImageProperties
    """
    assert ImageMapping.get_prop_mapping() == ImageProperties


def test_get_server_side_handler_returns_correct_type():
    """
    Tests get server side handler returns a server side handler
    """
    assert isinstance(ImageMapping.get_server_side_handler(), ServerSideHandler)


def test_server_side_handler_mappings_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for equal to params
    """
    mappings = {
        ImageProperties.IMAGE_NAME: "name",
        ImageProperties.IMAGE_STATUS: "status",
    }

    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().generic_handler,
        QueryPresetsGeneric.EQUAL_TO,
        mappings,
        test_case=(True, True),
    )


def test_server_side_handler_mappings_any_in(server_side_any_in_mappings):
    """
    Tests server side handler mappings are correct for ANY_IN, and line up to the expected
    server side params for equal to params
    Tests that mappings render multiple server-side filters if multiple values given.
    Tests that equivalent equal to server-side filter exists for each ANY_IN filter - since they
    produce equivalent filters
    """

    mappings = {
        ImageProperties.IMAGE_NAME: "name",
        ImageProperties.IMAGE_STATUS: "status",
    }
    server_side_any_in_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().generic_handler,
        mappings,
        {"test1": "test1", "test2": "test2"},
    )


@patch("openstack_query.mappings.image_mapping.TimeUtils")
def test_server_side_handler_mappings_older_than_or_equal_to(
    mock_time_utils, server_side_test_mappings
):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for older_than_or_equal_to params
    """
    mock_time_utils.convert_to_timestamp.return_value = "test"
    mappings = {
        ImageProperties.IMAGE_CREATION_DATE: "created_at",
        ImageProperties.IMAGE_LAST_UPDATED_DATE: "updated_at",
    }
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().datetime_handler,
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO,
        mappings,
        ("test", "lte:test"),
    )


@patch("openstack_query.mappings.image_mapping.TimeUtils")
def test_server_side_handler_mappings_older_than(
    mock_time_utils, server_side_test_mappings
):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for older_than params
    """
    mock_time_utils.convert_to_timestamp.return_value = "test"
    mappings = {
        ImageProperties.IMAGE_CREATION_DATE: "created_at",
        ImageProperties.IMAGE_LAST_UPDATED_DATE: "updated_at",
    }
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().datetime_handler,
        QueryPresetsDateTime.OLDER_THAN,
        mappings,
        ("test", "lt:test"),
    )


@patch("openstack_query.mappings.image_mapping.TimeUtils")
def test_server_side_handler_mappings_younger_than_or_equal_to(
    mock_time_utils, server_side_test_mappings
):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for younger_than_or_equal_to params
    """
    mock_time_utils.convert_to_timestamp.return_value = "test"
    mappings = {
        ImageProperties.IMAGE_CREATION_DATE: "created_at",
        ImageProperties.IMAGE_LAST_UPDATED_DATE: "updated_at",
    }
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().datetime_handler,
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO,
        mappings,
        ("test", "gte:test"),
    )


@patch("openstack_query.mappings.image_mapping.TimeUtils")
def test_server_side_handler_mappings_younger_than(
    mock_time_utils, server_side_test_mappings
):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for younger_than params
    """
    mock_time_utils.convert_to_timestamp.return_value = "test"
    mappings = {
        ImageProperties.IMAGE_CREATION_DATE: "created_at",
        ImageProperties.IMAGE_LAST_UPDATED_DATE: "updated_at",
    }
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().datetime_handler,
        QueryPresetsDateTime.YOUNGER_THAN,
        mappings,
        ("test", "gt:test"),
    )


def test_server_side_handler_less_than_or_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for less_than_or_equal_to params
    """
    mappings = {
        ImageProperties.IMAGE_SIZE: "size_max",
    }
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO,
        mappings,
        (10, 10),
    )

    # with strings which can convert to ints
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO,
        mappings,
        ("10", 10),
    )

    # with floats which can convert to ints
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO,
        mappings,
        (10.0, 10),
    )


def test_server_side_handler_greater_than_or_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for greater_than_or_equal_to params
    """
    mappings = {
        ImageProperties.IMAGE_SIZE: "size_min",
    }
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO,
        mappings,
        (10, 10),
    )

    # with strings which can convert to ints
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO,
        mappings,
        ("10", 10),
    )

    # with floats which can convert to ints
    server_side_test_mappings(
        ImageMapping.get_server_side_handler(),
        ImageMapping.get_client_side_handlers().integer_handler,
        QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO,
        mappings,
        (10.0, 10),
    )


def test_client_side_handlers_generic(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for generic presets
    """
    handler = ImageMapping.get_client_side_handlers().generic_handler
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
    handler = ImageMapping.get_client_side_handlers().string_handler
    mappings = {
        QueryPresetsString.MATCHES_REGEX: [
            ImageProperties.IMAGE_NAME,
        ]
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_datetime(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for string presets
    """
    date_prop_list = [
        ImageProperties.IMAGE_CREATION_DATE,
        ImageProperties.IMAGE_LAST_UPDATED_DATE,
    ]
    handler = ImageMapping.get_client_side_handlers().datetime_handler
    mappings = {
        QueryPresetsDateTime.OLDER_THAN: date_prop_list,
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: date_prop_list,
        QueryPresetsDateTime.YOUNGER_THAN: date_prop_list,
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: date_prop_list,
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_integer(client_side_test_mappings):
    """
    Tests client side handler mappings are correct
    shouldn't create an integer handler because there are no integer related properties for Server
    """
    integer_prop_list = [
        ImageProperties.IMAGE_SIZE,
        ImageProperties.IMAGE_MINIMUM_RAM,
        ImageProperties.IMAGE_MINIMUM_DISK,
        ImageProperties.IMAGE_CREATION_PROGRESS,
    ]
    handler = ImageMapping.get_client_side_handlers().integer_handler
    mappings = {
        QueryPresetsInteger.LESS_THAN: integer_prop_list,
        QueryPresetsInteger.GREATER_THAN: integer_prop_list,
        QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: integer_prop_list,
        QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: integer_prop_list,
    }
    client_side_test_mappings(handler, mappings)
