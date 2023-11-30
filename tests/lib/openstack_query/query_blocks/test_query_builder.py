from unittest.mock import MagicMock, patch, NonCallableMock
import pytest

from openstack_query.query_blocks.query_builder import QueryBuilder

from exceptions.query_preset_mapping_error import QueryPresetMappingError
from exceptions.query_property_mapping_error import QueryPropertyMappingError

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="mock_invalid_client_handler")
def mock_invalid_client_handler_fixture():
    """
    Return a client handler - mocks one handler which does not contain preset
    """
    mock_invalid_client_handler = MagicMock()
    mock_invalid_client_handler.preset_known.return_value = False
    mock_invalid_client_handler.check_supported.return_value = False
    return mock_invalid_client_handler


@pytest.fixture(name="mock_valid_client_handler")
def mock_valid_client_handler_fixture():
    """
    Return a client handler - mocks one handler which does contain preset
    """

    def _mock_preset_known(preset):
        """A dummy function to mock the preset_known method on the client handler"""
        return (
            True
            if preset in [MockQueryPresets.ITEM_1, MockQueryPresets.ITEM_3]
            else False
        )

    def _mock_check_supported(preset, prop):
        """A dummy function to mock the check_supported method on the client handler"""
        if preset == MockQueryPresets.ITEM_1 and prop == MockProperties.PROP_1:
            return True
        return False

    mock_invalid_client_handler = MagicMock()
    mock_invalid_client_handler.preset_known = MagicMock(wraps=_mock_preset_known)
    mock_invalid_client_handler.check_supported = MagicMock(wraps=_mock_check_supported)
    return mock_invalid_client_handler


@pytest.fixture(name="mock_server_side_handler")
def mock_valid_server_handler_fixture():
    """
    Return a server-side handler
    """
    return MagicMock()


@pytest.fixture(name="instance")
def instance_fixture(
    mock_server_side_handler, mock_invalid_client_handler, mock_valid_client_handler
):
    """
    Returns an instance with mocked client_side_handlers and
    server_side_handler injects
    """

    client_handlers = [mock_invalid_client_handler, mock_valid_client_handler]

    return QueryBuilder(
        prop_enum_cls=MockProperties,
        client_side_handlers=client_handlers,
        server_side_handler=mock_server_side_handler,
    )


@pytest.fixture(name="run_parse_where_test")
def run_parse_where_test_fixture(
    instance, mock_server_side_handler, mock_valid_client_handler
):
    """
    This fixture runs test cases of parse_where, where we expect it to complete successfully,
    In each test case we change what server_side_handler.get_filters and client_side_handler.get_filter_func returns
    This will change what is set in the client_side_filters and server_side_filters properties at the end
    """
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    # pylint:disable=too-many-arguments
    def _run_parse_where_test_case(
        mock_get_filter_return,
        mock_get_filter_func_return,
        expected_server_side_filters,
        expected_client_side_filters,
        expected_fallback_filters,
        test_instance=instance,
    ):
        """
        runs a test case of parse_where
        :param mock_get_filter_return: setting what server_side_handler.get_filters returns
        :param mock_get_filter_return: setting what client_side_handler.get_filter_func returns
        :param expected_server_side_filters: expected value of server_side_filters property
        :param expected_client_side_filters: expected value of client_side_filters property
        :param expected_fallback_filters: expected value of server_filter_fallback property
        :param test_instance (optional): a modified version of QueryBuilder to run test on
            - if left blank it creates a new instance
        """
        mock_server_side_handler.get_filters.return_value = mock_get_filter_return
        mock_valid_client_handler.get_filter_func.return_value = (
            mock_get_filter_func_return
        )

        with patch.object(MockProperties, "get_prop_mapping") as mock_get_prop_mapping:
            test_instance.parse_where(
                MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_kwargs
            )

        mock_valid_client_handler.get_filter_func.assert_called_once_with(
            preset=MockQueryPresets.ITEM_1,
            prop=MockProperties.PROP_1,
            prop_func=mock_get_prop_mapping.return_value,
            filter_func_kwargs=mock_kwargs,
        )
        mock_server_side_handler.get_filters.assert_called_once_with(
            preset=MockQueryPresets.ITEM_1,
            prop=MockProperties.PROP_1,
            params=mock_kwargs,
        )

        assert test_instance.client_side_filters == expected_client_side_filters
        assert test_instance.server_side_filters == expected_server_side_filters
        assert test_instance.server_filter_fallback == expected_fallback_filters

    return _run_parse_where_test_case


def test_parse_where_with_single_filter(run_parse_where_test):
    """
    Tests that parse_where where server-side-handler get_filters returns a single filter set
    """
    mock_client_filter = NonCallableMock()
    run_parse_where_test(
        mock_get_filter_return=[{"filter1": "val1", "filter2": "val2"}],
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=[{"filter1": "val1", "filter2": "val2"}],
        expected_client_side_filters=[],
        expected_fallback_filters=[mock_client_filter],
    )


def test_parse_where_with_filter_list(run_parse_where_test):
    """
    Tests that parse_where where server-side-handler get_filters returns a list of filters
    """
    mock_client_filter = NonCallableMock()
    mock_server_filter = [{"filter1": "val1"}, {"filter2": "val2"}]
    run_parse_where_test(
        mock_get_filter_return=mock_server_filter,
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=mock_server_filter,
        expected_client_side_filters=[],
        expected_fallback_filters=[mock_client_filter],
    )


def test_parse_where_with_no_filters(run_parse_where_test):
    """
    Tests that parse_where where server-side-handler get_filters returns no filters
    """
    mock_client_filter = NonCallableMock()
    mock_server_filter = None
    run_parse_where_test(
        mock_get_filter_return=mock_server_filter,
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=[],
        expected_client_side_filters=[mock_client_filter],
        expected_fallback_filters=[],
    )


@pytest.mark.parametrize(
    "existing_filters, new_filters, expected_out",
    [
        # one (non-overlapping) server-side filter set
        # one server-side filter set to add
        (
            [{"filter1": "val1"}],
            [{"filter2": "val2"}],
            [{"filter1": "val1", "filter2": "val2"}],
        ),
        # multiple (non-overlapping) server-side filters set, one
        # one server-side filter set to add
        (
            [{"filter1": "val1"}, {"filter2": "val2"}],
            [{"filter3": "val3"}],
            [
                {"filter1": "val1", "filter3": "val3"},
                {"filter2": "val2", "filter3": "val3"},
            ],
        ),
        # multiple (non-overlapping) server-side filters set
        # multiple server-side filter sets to add
        (
            [{"filter1": "val1"}, {"filter2": "val2"}],
            [{"filter3": "val3"}, {"filter4": "val4"}],
            [
                {"filter1": "val1", "filter3": "val3"},
                {"filter1": "val1", "filter4": "val4"},
                {"filter2": "val2", "filter3": "val3"},
                {"filter2": "val2", "filter4": "val4"},
            ],
        ),
    ],
)
def test_parse_where_when_filter_exists(
    existing_filters, new_filters, expected_out, instance, run_parse_where_test
):
    """
    Tests parse_where, for various cases where adding new preset requires a new
    server-side filter to be added, to an already populated server_side_filters property from previous presets
    Tests that the two filters are concatenated properly
    """
    instance.server_side_filters = existing_filters

    filter1_fallback_func = NonCallableMock()
    instance.server_filter_fallback = [filter1_fallback_func]

    mock_client_filter = NonCallableMock()
    run_parse_where_test(
        mock_get_filter_return=new_filters,
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=expected_out,
        expected_client_side_filters=[],
        expected_fallback_filters=[filter1_fallback_func, mock_client_filter],
    )


@pytest.mark.parametrize(
    "existing_filters, new_filters",
    [
        # one server-side filter set
        # same filter to add again - conflicting
        (
            [{"filter1": "val1"}],
            [{"filter1": "val2"}],
        ),
        # multiple server-side filters set
        # one to add which conflicts with existing filter in set
        (
            [{"filter1": "val1"}, {"filter2": "val2"}],
            [{"filter2": "val3"}],
        ),
        # multiple server-side filters with multiple items in them
        # one to add which conflicts with one filter of one item in set
        (
            [
                {"filter1": "val1", "filter3": "val3"},
                {"filter1": "val1", "filter4": "val4"},
                {"filter2": "val2", "filter3": "val3"},
                {"filter2": "val2", "filter4": "val4"},
            ],
            [{"filter3": "val4"}],
        ),
    ],
)
def test_add_filter_conflicting_presets(
    existing_filters, new_filters, instance, run_parse_where_test
):
    """
    Tests parse_where - when a conflict occurs between server-side filter params
    In this case, we add the new client_side filter to client_side_filters attribute instead
    """
    instance.server_side_filters = existing_filters

    filter1_fallback_func = NonCallableMock()
    instance.server_filter_fallback = [filter1_fallback_func]

    mock_client_filter = NonCallableMock()
    run_parse_where_test(
        mock_get_filter_return=new_filters,
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=existing_filters,
        expected_client_side_filters=[mock_client_filter],
        expected_fallback_filters=[filter1_fallback_func],
    )


def test_parse_where_preset_unknown(instance):
    """
    Tests that parse_where errors if no handler found which supports given preset
    """

    # when preset_known returns false
    with patch.object(MockProperties, "get_prop_mapping") as mock_prop_func:
        with pytest.raises(QueryPresetMappingError):
            instance.parse_where(MockQueryPresets.ITEM_2, MockProperties.PROP_1)
    mock_prop_func.assert_called_once_with(MockProperties.PROP_1)


def test_parse_where_preset_misconfigured(instance):
    """
    Tests that parse_where errors if preset should be handled by handler, but
    no client-side mapping found for property
    """

    # when preset_known returns True, but client_side filter missing
    with patch.object(MockProperties, "get_prop_mapping") as mock_prop_func:
        with pytest.raises(QueryPresetMappingError):
            instance.parse_where(MockQueryPresets.ITEM_2, MockProperties.PROP_1)
    mock_prop_func.assert_called_once_with(MockProperties.PROP_1)


def test_parse_where_prop_invalid(instance):
    """
    Tests that parse_where errors if a handler is found for a given preset,
    but it does not support the given property

    """
    with patch.object(MockProperties, "get_prop_mapping") as mock_prop_func:
        mock_prop_func.return_value = None
        with pytest.raises(QueryPropertyMappingError):
            instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
    mock_prop_func.assert_called_once_with(MockProperties.PROP_1)


def test_client_side_filters(instance):
    """
    Tests client_side_filter property methods
    """
    instance.client_side_filter = ["some-client-side-filter"]
    res = instance.client_side_filter
    assert res == ["some-client-side-filter"]


def test_server_side_filters(instance):
    """
    Tests server_side_filters property methods
    """
    instance.server_side_filters = ["some-server-side-filter"]
    res = instance.server_side_filters
    assert res == ["some-server-side-filter"]


def test_server_filter_fallback(instance):
    """
    Tests server_filter_fallback property methods
    """
    instance.server_filter_fallback = ["some-client-side-filter"]
    res = instance.server_filter_fallback
    assert res == ["some-client-side-filter"]
