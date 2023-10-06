from unittest.mock import MagicMock, patch

import pytest

from exceptions.query_preset_mapping_error import QueryPresetMappingError
from openstack_query.handlers.server_side_handler import ServerSideHandler
from tests.lib.openstack_query.mocks.mocked_props import MockProperties
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets


# pylint:disable=protected-access, unnecessary-lambda-assignment


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Prepares an instance to be used in tests
    """
    server_side_function_mappings = {
        MockQueryPresets.ITEM_1: {
            MockProperties.PROP_1: "item1-prop1-kwarg",
            MockProperties.PROP_2: "item2-prop2-kwarg",
        },
        MockQueryPresets.ITEM_2: {
            MockProperties.PROP_3: "item2-prop3-kwarg",
            MockProperties.PROP_4: "item2-prop4-kwarg",
        },
    }
    return ServerSideHandler(server_side_function_mappings)


def test_check_supported_true(instance):
    """
    Tests that check_supported method works expectedly
    returns True if Prop Enum and Preset Enum have server-side mapping
    """
    assert instance.check_supported(MockQueryPresets.ITEM_1, MockProperties.PROP_1)


def test_check_supported_false(instance):
    """
    Tests that check_supported method works expectedly
    returns False if either Preset is not supported or Preset-Prop does not have a mapping
    """

    # when preset is not supported
    assert not instance.check_supported(MockQueryPresets.ITEM_3, MockProperties.PROP_1)

    # when preset found, but prop is not supported
    assert not instance.check_supported(MockQueryPresets.ITEM_1, MockProperties.PROP_3)


def test_get_supported_props(instance):
    """
    Tests that get_supported_props method works expectedly
    returns a list of supported props for a given preset
    """
    assert instance.get_supported_props(MockQueryPresets.ITEM_1)


def test_get_mapping_valid(instance):
    """
    Tests that get_mapping method works expectedly
    returns server-side filter func if Prop Enum and Preset Enum are supported
    """
    assert (
        instance._get_mapping(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
        == "item1-prop1-kwarg"
    )


def test_get_mapping_invalid(instance):
    """
    Tests that get_mapping method works expectedly
    returns None if Prop Enum and Preset Enum are not supported or don't have a mapping
    """
    # when preset is not supported
    assert instance._get_mapping(MockQueryPresets.ITEM_3, MockProperties.PROP_1) is None

    # when preset found, but prop is not supported
    assert instance._get_mapping(MockQueryPresets.ITEM_1, MockProperties.PROP_3) is None


@patch(
    "openstack_query.handlers.server_side_handler.ServerSideHandler._check_filter_mapping"
)
@patch("openstack_query.handlers.server_side_handler.ServerSideHandler._get_mapping")
def test_get_filters_valid_list(mock_get_mapping, mock_check_filter_mapping, instance):
    """
    Tests that get_filters method works expectedly - filters returned are a list
    returns server-side filters as a set of kwargs
        - Prop Enum and Preset Enum are supported
        - and filter_params are valid
    """
    mock_params = {"arg1": "val1", "arg2": "val2"}
    mock_filter_func = MagicMock()

    mock_filters = ["filter1", "filter2"]
    mock_filter_func.return_value = mock_filters

    mock_check_filter_mapping.return_value = True, ""
    mock_get_mapping.return_value = mock_filter_func

    res = instance.get_filters(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
    )

    mock_check_filter_mapping.assert_called_once_with(mock_filter_func, mock_params)
    mock_filter_func.assert_called_once_with(**mock_params)
    assert res == mock_filters


@patch(
    "openstack_query.handlers.server_side_handler.ServerSideHandler._check_filter_mapping"
)
@patch("openstack_query.handlers.server_side_handler.ServerSideHandler._get_mapping")
def test_get_filters_valid_not_list(
    mock_get_mapping, mock_check_filter_mapping, instance
):
    """
    Tests that get_filters method works expectedly - filters returned are a not a list
    returns server-side filters as a set of kwargs
        - Prop Enum and Preset Enum are supported
        - and filter_params are valid
    """
    mock_params = {"arg1": "val1", "arg2": "val2"}
    mock_filter_func = MagicMock()

    mock_filters = "filter1"
    mock_filter_func.return_value = mock_filters

    mock_check_filter_mapping.return_value = True, ""
    mock_get_mapping.return_value = mock_filter_func

    res = instance.get_filters(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
    )

    mock_check_filter_mapping.assert_called_once_with(mock_filter_func, mock_params)
    mock_filter_func.assert_called_once_with(**mock_params)
    assert res == [mock_filters]


@patch(
    "openstack_query.handlers.server_side_handler.ServerSideHandler._check_filter_mapping"
)
def test_get_filters_invalid(mock_check_filter_mapping, instance):
    """
    Tests that get_filters method works expectedly
    raises QueryPresetMappingError if:
        - Prop Enum and Preset Enum are not supported
        - or filter_params is not valid
    """
    mock_params = {"arg1": "val1", "arg2": "val2"}

    # when preset/prop not supported
    res = instance.get_filters(
        MockQueryPresets.ITEM_3, MockProperties.PROP_1, mock_params
    )
    assert res is None

    # when preset/prop are supported, but wrong filter_params
    mock_check_filter_mapping.return_value = False, "some-reason"
    with pytest.raises(QueryPresetMappingError):
        instance.get_filters(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
        )


@pytest.mark.parametrize(
    "valid_params_to_test",
    [
        # "required args only",
        {"arg1": 12},
        # "required and default"
        {"arg1": 12, "arg2": "non-default"},
        # "required and kwarg"
        {"arg1": 12, "some_kwarg": "some-val"},
        # "all possible"
        {"arg1": 12, "arg2": "non-default", "some_kwarg": "some-val"},
        # "different order"
        {"arg2": "non-default", "some_kwarg": "some-val", "arg1": 12},
    ],
)
def test_check_filter_mapping_valid(valid_params_to_test, instance):
    """
    Tests that check_filter_mapping method works expectedly - valid
    returns True only if args match expected args required by filter function lambda
    """
    mock_server_side_mapping = lambda arg1, arg2="some-default", **kwargs: {
        "kwarg1": "val1"
    }
    assert instance._check_filter_mapping(
        mock_server_side_mapping, filter_params=valid_params_to_test
    )[0]


def test_check_filter_mapping_invalid_positional(instance):
    """
    Tests that check_filter_mapping method works expectedly - invalid positional args
    returns False if args don't match expected positional args required by filter function lambda
    """
    mock_server_side_mapping = lambda arg1: {"kwarg1": "val1"}
    assert not (
        instance._check_filter_mapping(
            mock_server_side_mapping, filter_params={"arg2": "val2"}
        )[0]
    )


def test_check_filter_mapping_invalid_kwargs(instance):
    """
    Tests that check_filter_mapping method works expectedly - invalid key-word args
    returns False if kwargs is passed and is used that is required
    """
    mock_server_side_mapping = lambda **kwargs: {"arg": kwargs["val1"]}
    assert not (
        instance._check_filter_mapping(
            mock_server_side_mapping, filter_params={"arg2": "val2"}
        )[0]
    )
