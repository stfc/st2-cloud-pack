from unittest.mock import patch

from enums.query.props.flavor_properties import FlavorProperties
from enums.query.props.hypervisor_properties import HypervisorProperties
from enums.query.props.image_properties import ImageProperties
from enums.query.props.project_properties import ProjectProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsDateTime,
    QueryPresetsString,
)
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


def test_server_side_handler_mappings_equal_to(server_side_test_mappings):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for equal to params
    """
    mappings = {
        ServerProperties.USER_ID: "user_id",
        ServerProperties.SERVER_ID: "uuid",
        ServerProperties.SERVER_NAME: "hostname",
        ServerProperties.SERVER_STATUS: "status",
        ServerProperties.SERVER_DESCRIPTION: "description",
        ServerProperties.SERVER_CREATION_DATE: "created_at",
        ServerProperties.FLAVOR_ID: "flavor",
        ServerProperties.IMAGE_ID: "image",
        ServerProperties.PROJECT_ID: "project_id",
    }
    server_side_test_mappings(
        ServerMapping.get_server_side_handler(),
        ServerMapping.get_client_side_handlers().generic_handler,
        QueryPresetsGeneric.EQUAL_TO,
        mappings,
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
        ServerProperties.USER_ID: "user_id",
        ServerProperties.SERVER_ID: "uuid",
        ServerProperties.SERVER_NAME: "hostname",
        ServerProperties.SERVER_STATUS: "status",
        ServerProperties.SERVER_DESCRIPTION: "description",
        ServerProperties.SERVER_CREATION_DATE: "created_at",
        ServerProperties.FLAVOR_ID: "flavor",
        ServerProperties.IMAGE_ID: "image",
        ServerProperties.PROJECT_ID: "project_id",
    }
    server_side_any_in_mappings(
        ServerMapping.get_server_side_handler(),
        ServerMapping.get_client_side_handlers().generic_handler,
        mappings,
        {"test1": "test1", "test2": "test2"},
    )


@patch("openstack_query.mappings.server_mapping.TimeUtils")
def test_server_side_handler_mappings_older_than_or_equal_to(
    mock_time_utils, server_side_test_mappings
):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for older_than_or_equal_to params
    """
    mock_time_utils.convert_to_timestamp.return_value = "test"
    mappings = {
        ServerProperties.SERVER_LAST_UPDATED_DATE: "changes-before",
    }
    server_side_test_mappings(
        ServerMapping.get_server_side_handler(),
        ServerMapping.get_client_side_handlers().datetime_handler,
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO,
        mappings,
    )

    # filter_func is evaluated twice, but convert_to_timestamp is only called once
    mock_time_utils.convert_to_timestamp.assert_called_once_with(value="test")


@patch("openstack_query.mappings.server_mapping.TimeUtils")
def test_server_side_handler_mappings_younger_than_or_equal_to(
    mock_time_utils, server_side_test_mappings
):
    """
    Tests server side handler mappings are correct, and line up to the expected
    server side params for younger_than_or_equal_to params
    """
    mock_time_utils.convert_to_timestamp.return_value = "test"
    mappings = {
        ServerProperties.SERVER_LAST_UPDATED_DATE: "changes-since",
    }
    server_side_test_mappings(
        ServerMapping.get_server_side_handler(),
        ServerMapping.get_client_side_handlers().datetime_handler,
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO,
        mappings,
    )

    # filter_func is evaluated twice, but convert_to_timestamp is only called once
    mock_time_utils.convert_to_timestamp.assert_called_once_with(value="test")


def test_client_side_handlers_generic(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for generic presets
    """
    handler = ServerMapping.get_client_side_handlers().generic_handler
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
    handler = ServerMapping.get_client_side_handlers().string_handler
    mappings = {
        QueryPresetsString.MATCHES_REGEX: [
            ServerProperties.SERVER_NAME,
            ServerProperties.ADDRESSES,
        ]
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_datetime(client_side_test_mappings):
    """
    Tests client side handler mappings are correct, and line up to the expected
    client side params for string presets
    """
    handler = ServerMapping.get_client_side_handlers().datetime_handler
    mappings = {
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_LAST_UPDATED_DATE,
            ServerProperties.SERVER_CREATION_DATE,
        ],
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_LAST_UPDATED_DATE,
            ServerProperties.SERVER_CREATION_DATE,
        ],
        QueryPresetsDateTime.YOUNGER_THAN: [
            ServerProperties.SERVER_LAST_UPDATED_DATE,
            ServerProperties.SERVER_CREATION_DATE,
        ],
        QueryPresetsDateTime.OLDER_THAN: [
            ServerProperties.SERVER_LAST_UPDATED_DATE,
            ServerProperties.SERVER_CREATION_DATE,
        ],
    }
    client_side_test_mappings(handler, mappings)


def test_client_side_handlers_integer():
    """
    Tests client side handler mappings are correct
    shouldn't create an integer handler because there are no integer related properties for Server
    """
    handler = ServerMapping.get_client_side_handlers().integer_handler
    assert not handler


def test_get_chain_mappings():
    """
    Tests get_chain_mapping outputs correctly
    """
    expected_mappings = {
        ServerProperties.USER_ID: UserProperties.USER_ID,
        ServerProperties.PROJECT_ID: ProjectProperties.PROJECT_ID,
        ServerProperties.FLAVOR_ID: FlavorProperties.FLAVOR_ID,
        ServerProperties.IMAGE_ID: ImageProperties.IMAGE_ID,
        ServerProperties.HYPERVISOR_ID: HypervisorProperties.HYPERVISOR_ID,
    }

    assert ServerMapping.get_chain_mappings() == expected_mappings
