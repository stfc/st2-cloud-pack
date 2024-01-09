from typing import Dict, List, Tuple
import pytest

from custom_types.openstack_query.aliases import PresetPropMappings
from enums.query.props.prop_enum import PropEnum
from enums.query.query_presets import QueryPresets, QueryPresetsGeneric
from openstack_query.handlers.client_side_handler import ClientSideHandler
from openstack_query.handlers.server_side_handler import ServerSideHandler


@pytest.fixture(scope="function", name="client_side_test_mappings")
def client_side_test_mappings_fixture():
    """
    Fixture to test client side mappings using different handlers
    """

    def _client_side_test_case(
        handler: ClientSideHandler, expected_mappings: PresetPropMappings
    ):
        """
        Tests client side handler mappings are correct, ensure that each handler has appropriate presets
        and each is lined up with expected prop enums or '[*]' meaning it can be used for any valid prop enum
        :param handler: client-side handler to test
        :param expected_mappings: expected list of prop enums or '[*]' - should match the mapping set
        """
        for test_preset in expected_mappings:
            assert set(handler.get_supported_props(test_preset)) == set(
                expected_mappings[test_preset]
            )

    return _client_side_test_case


@pytest.fixture(scope="function", name="client_side_match")
def client_side_match_fixture():
    """
    Fixture to test that for a given set of server-side preset mappings,
    there is an equivalent client side mapping in a given client-side handler
    """

    def _client_side_match(
        handler: ClientSideHandler,
        test_preset: QueryPresets,
        expected_props: List[PropEnum],
    ):
        """
        Tests that a client side handler has a preset mapping and supports a given set of properties
        :param handler: client-side handler to test
        :param test_preset: preset to test against
        :param expected_props: list of prop enums that the client handler preset should map to
        """
        assert handler.preset_known(test_preset)
        supported_props = handler.get_supported_props(test_preset)
        if supported_props == ["*"]:
            # this denotes that preset will support all properties
            assert True
        else:
            assert all(prop in supported_props for prop in expected_props)

    return _client_side_match


@pytest.fixture(scope="function", name="server_side_test_mappings")
def server_side_test_mappings_fixture(client_side_match):
    """
    Fixture to test server side mappings using different presets
    """

    def _server_side_test_case(
        server_side_handler: ServerSideHandler,
        client_side_handler: ClientSideHandler,
        preset_to_test: QueryPresets,
        expected_mappings: Dict[PropEnum, str],
        test_case: Tuple = ("test", "test"),
    ):
        """
        Tests server side handler mappings are correct, and line up to the expected
        server side params for equal to params. Also tests that server-side mapping has equivalent
        client-side mapping.
        :param server_side_handler: server-side handler to test
        :param client_side_handler: equivalent client-side handler to test
        :param preset_to_test: preset to test against
        :param expected_mappings: dictionary mapping expected properties to the filter param they should output
        :param test_case: tuple of value to test mapping with and expected value that
        it will map to when running get_filters
        """
        supported_props = server_side_handler.get_supported_props(preset_to_test)
        assert all(
            key_to_check in supported_props for key_to_check in expected_mappings
        )
        for prop, expected in expected_mappings.items():
            server_filter = server_side_handler.get_filters(
                preset_to_test, prop, {"value": test_case[0]}
            )
            assert server_filter == [{expected: test_case[1]}]
        client_side_match(
            client_side_handler, preset_to_test, list(expected_mappings.keys())
        )

    return _server_side_test_case


@pytest.fixture(scope="function", name="server_side_any_in_mappings")
def server_side_test_any_in_mappings_fixture(
    client_side_match, server_side_test_mappings
):
    """
    Fixture to test server side mappings for ANY_IN
    """

    def _server_side_any_in_test_case(
        server_side_handler: ServerSideHandler,
        client_side_handler: ClientSideHandler,
        expected_mappings: Dict[PropEnum, str],
        test_cases: Dict,
    ):
        """
        Tests server side handler mappings for ANY_IN preset are correct, and line up to the expected
        server side params for equal to params. Will test with one and with multiple values
        Also tests that server-side mapping has equivalent client-side mapping.
        :param server_side_handler: server-side handler to test
        :param client_side_handler: equivalent client-side handler to test
        :param expected_mappings: dictionary mapping expected properties to the filter param they should output
        :param test_cases: tuple of value to test mapping with and expected value that
        it will map to when running get_filters
        """
        supported_props = server_side_handler.get_supported_props(
            QueryPresetsGeneric.ANY_IN
        )

        assert all(
            key_to_check in supported_props for key_to_check in expected_mappings
        )
        for prop, expected in expected_mappings.items():
            # test with one value
            server_filter = server_side_handler.get_filters(
                QueryPresetsGeneric.ANY_IN,
                prop,
                {"values": [list(test_cases.keys())[0]]},
            )
            assert server_filter == [{expected: list(test_cases.values())[0]}]

            # test with multiple values
            server_filter = server_side_handler.get_filters(
                QueryPresetsGeneric.ANY_IN,
                prop,
                {"values": list(test_cases.keys())},
            )
            assert server_filter == [
                {expected: test_exp} for test_exp in list(test_cases.values())
            ]

        # EQUAL_TO should have the same mappings for ANY_IN
        server_side_test_mappings(
            server_side_handler,
            client_side_handler,
            QueryPresetsGeneric.EQUAL_TO,
            expected_mappings,
            test_case=(list(test_cases.keys())[0], list(test_cases.values())[0]),
        )

        client_side_match(
            client_side_handler,
            QueryPresetsGeneric.ANY_IN,
            list(expected_mappings.keys()),
        )

    return _server_side_any_in_test_case
