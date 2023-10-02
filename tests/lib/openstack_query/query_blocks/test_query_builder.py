from unittest.mock import MagicMock, patch
import pytest

from openstack_query.query_blocks.query_builder import QueryBuilder

from exceptions.parse_query_error import ParseQueryError
from exceptions.query_preset_mapping_error import QueryPresetMappingError
from exceptions.query_property_mapping_error import QueryPropertyMappingError

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="mock_client_side_handlers")
def client_side_handlers_fixture():
    """
    Returns a dictionary of mocked client_side_handler objects
    """
    return {"mock_client_handler_1": MagicMock(), "mock_client_handler_2": MagicMock()}


@pytest.fixture(name="mock_server_side_handler")
def server_side_handler_fixture():
    """
    Returns a mocked server_side_handler_object
    """
    return MagicMock()


@pytest.fixture(name="instance")
def instance_fixture(mock_client_side_handlers, mock_server_side_handler):
    """
    Returns an instance with mocked client_side_handlers and
    server_side_handler injects
    """
    mock_prop_enum_cls = MockProperties
    instance = QueryBuilder(
        prop_enum_cls=mock_prop_enum_cls,
        client_side_handlers=list(mock_client_side_handlers.values()),
        server_side_handler=mock_server_side_handler,
    )
    return instance


@pytest.mark.parametrize(
    "mock_server_side_filter", [None, {"filter1": "val1", "filter2": "val2"}]
)
def test_parse_where_valid(mock_server_side_filter, instance, mock_server_side_handler):
    """
    Tests that parse_where functions expectedly - where inputs valid
    method finds and sets client_side_filter and server_side_filters internal attributes
    """

    # setup mocks
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_client_side_handler = MagicMock()
    mock_client_filter_func = MagicMock()
    mock_client_side_handler.get_filter_func.return_value = mock_client_filter_func
    mock_server_side_handler.get_filters.return_value = mock_server_side_filter

    with patch(
        "openstack_query.query_blocks.query_builder.QueryBuilder._get_preset_handler"
    ) as mock_get_preset_handler:
        mock_get_preset_handler.return_value = mock_client_side_handler
        with patch.object(MockProperties, "get_prop_mapping") as mock_prop_func:
            instance.parse_where(
                MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_kwargs
            )

    mock_get_preset_handler.assert_called_once_with(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1
    )
    mock_client_side_handler.get_filter_func.assert_called_once_with(
        preset=MockQueryPresets.ITEM_1,
        prop=MockProperties.PROP_1,
        prop_func=mock_prop_func.return_value,
        filter_func_kwargs=mock_kwargs,
    )
    mock_server_side_handler.get_filters.assert_called_once_with(
        preset=MockQueryPresets.ITEM_1,
        prop=MockProperties.PROP_1,
        params=mock_kwargs,
    )

    assert instance.client_side_filter == mock_client_filter_func
    assert instance.server_side_filters == mock_server_side_filter


def test_parse_where_filter_already_set(instance):
    """
    Tests that parse_where functions expectedly
    method raises ParseQueryError when client_side_filter already set
    """

    instance.client_side_filter = "previously-set-func"

    with pytest.raises(ParseQueryError):
        instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)


def test_parse_where_prop_invalid(instance):
    """
    Tests that parse_where functions expectedly - where inputs invalid
    method raises QueryPropertyMappingError when prop_handler.get_prop_mapping returns None
    """

    # test if prop_mapping doesn't exist
    instance.client_side_filter = None

    with patch.object(MockProperties, "get_prop_mapping") as mock_prop_func:
        mock_prop_func.return_value = None
        with pytest.raises(QueryPropertyMappingError):
            instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
    mock_prop_func.assert_called_once_with(MockProperties.PROP_1)


def test_get_preset_handler_valid(instance, mock_client_side_handlers):
    """
    Tests that get_preset_handler functions expectedly - where inputs invalid
    method should return a client_handler that supports a given preset-property pair
    """
    mock_client_side_handlers[
        "mock_client_handler_1"
    ].check_supported.return_value = False
    mock_client_side_handlers[
        "mock_client_handler_2"
    ].check_supported.return_value = True

    # pylint:disable=protected-access
    # check when preset found
    res = instance._get_preset_handler(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
    assert res == mock_client_side_handlers["mock_client_handler_2"]


def test_get_preset_handler_invalid_prop(instance, mock_client_side_handlers):
    """
    Tests that get_preset_handler functions expectedly - where preset valid but prop invalid
    method raises QueryPresetMappingError when no client-side handler available has mapping for preset-property pair
    """
    mock_client_side_handlers["mock_client_handler_1"].preset_known.return_value = False
    mock_client_side_handlers["mock_client_handler_2"].preset_known.return_value = True

    mock_client_side_handlers[
        "mock_client_handler_1"
    ].check_supported.return_value = False
    mock_client_side_handlers[
        "mock_client_handler_2"
    ].check_supported.return_value = False

    with pytest.raises(QueryPresetMappingError):
        # pylint:disable=protected-access
        instance._get_preset_handler(MockQueryPresets.ITEM_1, MockProperties.PROP_1)


def test_client_side_filter(instance):
    """
    Tests client_side_filter property methods
    """
    instance.client_side_filter = "some-client-side-filter"
    res = instance.client_side_filter
    assert res == "some-client-side-filter"


def test_server_side_filters(instance):
    """
    Tests server_side_filters property methods
    """
    instance.server_side_filters = "some-server-side-filter"
    res = instance.server_side_filters
    assert res == "some-server-side-filter"
