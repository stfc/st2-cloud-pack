import unittest
from typing import Any
from unittest.mock import MagicMock, patch, NonCallableMock

import pytest

from openstack_query.handlers.client_side_handler import ClientSideHandler
from exceptions.query_preset_mapping_error import QueryPresetMappingError

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


@pytest.fixture
def mock_filter_func(scope="function", autouse=True):
    def _mock_filter_func(prop, *args, **kwargs):
        pass
    return _mock_filter_func

@pytest.fixture
def instance():
    _filter_function_mappings = {
        MockQueryPresets.ITEM_1: ["*"],
        MockQueryPresets.ITEM_2: [MockProperties.PROP_1, MockProperties.PROP_2],
        MockQueryPresets.ITEM_3: [MockProperties.PROP_3, MockProperties.PROP_4],
    }
    instance = ClientSideHandler(_filter_function_mappings)
    
    instance._filter_functions = {
        MockQueryPresets.ITEM_1: mock_filter_func,
    }
    return instance



def test_check_supported_true(instance):
    """
    Tests that check_supported method works expectedly
    returns True if Prop Enum and Preset Enum have client-side mapping
    """
    # when preset has '*' mapping - accepts all props
    assert instance.check_supported(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1
        )

    # when preset has explicit prop mapping
    assert instance.check_supported(
            MockQueryPresets.ITEM_2, MockProperties.PROP_2
        )

def test_check_preset_supported_false(instance):
    """
    Tests that check_supported method works expectedly
    returns False if either Preset is not supported or Preset-Prop does not have a mapping
    """

    # when preset is not supported
    assert not instance.check_supported(
            MockQueryPresets.ITEM_4, MockProperties.PROP_1
    )

    # when preset found, but prop is not supported
    assert not instance.check_supported(
            MockQueryPresets.ITEM_2, MockProperties.PROP_3
    )

@patch(
    "openstack_query.handlers.client_side_handler.ClientSideHandler._check_filter_func"
)
@patch(
    "openstack_query.handlers.client_side_handler.ClientSideHandler._filter_func_wrapper"
)
def test_get_filter_func_valid(
    mock_filter_func_wrapper, mock_check_filter_func, instance
):
    """
    Tests that get_filter_func method works expectedly - with valid inputs
    sets up and returns a function that when given an openstack object will return a boolean value on
    whether it passes the filter
    """
    # define inputs
    mock_prop_func = MagicMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    # mock function return values
    mock_check_filter_func.return_value = True, ""
    mock_filter_func_wrapper.return_value = "a-boolean-value"

    res = instance.get_filter_func(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_prop_func, mock_kwargs
    )
    val = res("test-openstack-res")

    # MockQueryPresets.ITEM_1 and MockProperties.PROP_1 are valid and should return 'item1_func'
    # - which represents a function mapping
    mock_check_filter_func.assert_called_once_with(
        mock_filter_func, mock_kwargs
    )
    mock_filter_func_wrapper.assert_called_once_with(
        "test-openstack-res", mock_filter_func, mock_prop_func, mock_kwargs
    )

    assert val == "a-boolean-value"

def test_get_filter_func_preset_invalid(instance):
    """
    Tests that get_filter_func method works expectedly - with invalid inputs
    raises QueryPresetMappingError if preset invalid
    """
    mock_prop_func = MagicMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    # when preset is invalid
    with pytest.raises(QueryPresetMappingError):
        instance.get_filter_func(
            MockQueryPresets.ITEM_4,
            MockProperties.PROP_1,
            mock_prop_func,
            mock_kwargs,
        )

def test_get_filter_func_prop_invalid(instance):
    """
    Tests that get_filter_func method works expectedly - with invalid inputs
    raises QueryPresetMappingError if prop invalid
    """

    # when the preset is valid, but property is invalid
    with pytest.raises(QueryPresetMappingError):
        mock_prop_func = MagicMock()
        mock_kwargs = {"arg1": "val1", "arg2": "val2"}
        instance.get_filter_func(
            MockQueryPresets.ITEM_2,
            MockProperties.PROP_3,
            mock_prop_func,
            mock_kwargs,
        )

@patch(
    "openstack_query.handlers.client_side_handler.ClientSideHandler._check_filter_func"
)
def test_get_filter_func_arguments_invalid( mock_check_filter_func, instance):
    """
    Tests that get_filter_func method works expectedly - with invalid inputs
    raises QueryPresetMappingError if filter_func_kwargs are invalid
    """
    mock_prop_func = MagicMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    # when check_filter_func is false
    mock_check_filter_func.return_value = False, "some-error"
    with pytest.raises(QueryPresetMappingError):
        instance.get_filter_func(
            MockQueryPresets.ITEM_1,
            MockProperties.PROP_1,
            mock_prop_func,
            mock_kwargs,
        )

def test_filter_func_wrapper_prop_func_error(instance):
    """
    Tests that get_filter_func method works expectedly - with invalid inputs
    raises QueryPresetMappingError if filter_func_kwargs are invalid
    """
    mock_item = NonCallableMock()

    mock_filter_func = MagicMock()
    mock_filter_func.return_value = "a-boolean-value"

    mock_prop_func = MagicMock()
    mock_filter_func_kwargs = {"arg1": "val1", "arg2": "val2"}

    # when prop_func raises exception - i.e. property not found
    mock_prop_func.side_effect = AttributeError()
    res = instance._filter_func_wrapper(
        mock_item, mock_filter_func, mock_prop_func, mock_filter_func_kwargs
    )
    assert not res

def test_filter_func_wrapper_valid(instance):
    """
    Tests that filter_func_wrapper method works expectedly - with valid inputs
    returns a function that takes an openstack item as input and returns either True or False
    on whether that item passes the set filter condition.
        - Prop Enum and Preset Enum are supported
        - and filter_func_kwargs are valid
    """
    mock_item = NonCallableMock()

    mock_filter_func = MagicMock()
    mock_filter_func.return_value = "a-boolean-value"

    mock_prop_func = MagicMock()
    mock_filter_func_kwargs = {"arg1": "val1", "arg2": "val2"}

    # when prop_func is valid and filter_kwargs given
    mock_prop_func.return_value = "some-prop-val"
    mock_prop_func.side_effect = None
    res = instance._filter_func_wrapper(
        mock_item, mock_filter_func, mock_prop_func, mock_filter_func_kwargs
    )
    assert res == "a-boolean-value"
    mock_filter_func.assert_called_once_with(
        "some-prop-val", **mock_filter_func_kwargs
    )

    # when prop_func is valid and filter_kwargs not given
    mock_prop_func.reset_mock()
    mock_filter_func.reset_mock()
    mock_prop_func.return_value = "some-prop-val"
    mock_prop_func.side_effect = None
    res = instance._filter_func_wrapper(
        mock_item, mock_filter_func, mock_prop_func
    )
    assert res == "a-boolean-value"
    mock_filter_func.assert_called_once_with("some-prop-val")

@pytest.mark.parametrize("input_val",
    [
        # required args only
        {"arg1": 12},
        # required and default
        {"arg1": 12, "arg2": "non-default"},
        # required and kwarg
        {"arg1": 12, "some_kwarg": "some-val"},
        # all possible
        {"arg1": 12, "arg2": "non-default", "some_kwarg": "some-val"},
        # different order
        {"arg2": "non-default", "some_kwarg": "some-val", "arg1": 12},
    ]
)
def test_check_filter_func_valid_filters(input_val, instance):
    """
    Tests that check_filter_func method works expectedly - for filter_func which takes extra params
    returns True only if args match expected args required by client-side filter function
    """

    # pylint:disable=unused-argument
    def _mock_filter_func(prop, arg1: int, arg2: str = "some-default", **kwargs):
        return None

    res = instance._check_filter_func(
        _mock_filter_func, func_kwargs=input_val
    )
    assert res[0]
    assert res[1] == ""

@pytest.mark.parametrize("input_val",[
        # no but required"
        {},
        # required wrong type
        {"arg1": "non-default"},
        #optional wrong type
        {"arg1": 12, "arg2": 12},
    ]
)
def test_check_filter_func_invalid_entry( input_val, instance):
    """
    Tests that check_filter_func method works expectedly - for filter_func which takes extra params
    when args don't match expected args required by client-side filter function
    """

    # pylint:disable=unused-argument
    def _mock_filter_func(prop, arg1: int, arg2: str = "some-default", **kwargs):
        return None

    res = instance._check_filter_func(
        _mock_filter_func, func_kwargs=input_val
    )
    assert not res[0]
    assert isinstance(res[1], str) and len(res[1]) > 0

def test_check_filter_func_with_no_args(instance):
    """
    Tests that check_filter_func method works expectedly - for filter_func which takes no extra params
    returns True if args match expected args required by client-side filter function
    """
    # pylint:disable=unused-argument
    def _mock_filter_func(prop):
        return None

    res = instance._check_filter_func(
        _mock_filter_func, func_kwargs={}
    )
    assert res[0]
    
def test_check_filter_func_with_extra_arg( instance):
    """
    Tests that check_filter_func method works expectedly - for filter_func which takes no extra params
    if the user tries to pass one that doesn't exist
    """

    # pylint:disable=unused-argument
    def _mock_filter_func(prop):
        return None

    res = instance._check_filter_func(
        _mock_filter_func, func_kwargs={"arg1": "not-there"}
    )
    assert not res[0]

def test_check_filter_func_with_any_typing(instance):
    """
    Tests that check_filter_func method works expectedly - for filter_func which takes a param with Any
    returns True for any args which match.
    Also tests that variables with no type definition are also accepted (and type checking is ignored)
    """

    # pylint:disable=unused-argument
    def _mock_filter_func(prop, arg1, arg2, arg3: Any):
        return None

    res = instance._check_filter_func(
        _mock_filter_func, func_kwargs={"arg1": 1, "arg2": bool, "arg3": "string"}
    )
    assert  res[0]

    res = instance._check_filter_func(
        _mock_filter_func, func_kwargs={"arg1": 1, "arg2": bool, "arg3": "string"}
    )
    assert  res[0]
