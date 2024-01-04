from unittest.mock import MagicMock, NonCallableMock, call

import pytest

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from exceptions.parse_query_error import ParseQueryError
from exceptions.query_preset_mapping_error import QueryPresetMappingError

from openstack_query.handlers.client_side_handler import ClientSideHandler

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="mock_preset_prop_mappings")
def preset_prop_mappings_fixture():
    """
    Sets up a set of mock mappings of valid presets for handler against a
    list of mock properties that preset can work on
    """
    return {
        MockQueryPresets.ITEM_1: ["*"],
        MockQueryPresets.ITEM_2: [MockProperties.PROP_1, MockProperties.PROP_2],
        MockQueryPresets.ITEM_3: [MockProperties.PROP_3, MockProperties.PROP_4],
    }


@pytest.fixture(name="mock_filter")
def mock_filter_instance():
    """
    Returns a mocked filter that will always fail
    """

    return MagicMock()


@pytest.fixture(name="instance")
def instance_fixture(mock_preset_prop_mappings, mock_filter):
    """
    Returns a function that will setup a client_side_handler with mocks
    """

    mock_filter_mappings = {
        MockQueryPresets.ITEM_1: mock_filter,
    }
    return ClientSideHandler(mock_filter_mappings, mock_preset_prop_mappings)


def test_get_supported_props(instance):
    """
    Tests that get_supported_props method works expectedly
    returns the props mapped to a preset
    """
    assert instance.get_supported_props(MockQueryPresets.ITEM_1) == ["*"]
    assert instance.get_supported_props(MockQueryPresets.ITEM_2) == [
        MockProperties.PROP_1,
        MockProperties.PROP_2,
    ]


def test_check_supported_preset_unknown(instance):
    """
    Tests that check_supported method, when preset_known returns False, return False
    """
    mock_preset = MockQueryPresets.ITEM_4
    mock_prop = NonCallableMock()
    res = instance.check_supported(mock_preset, mock_prop)
    assert not res


def test_check_supported_prop_unknown(instance):
    """
    Tests that check_supported method, when prop not supported by preset, return False
    """
    mock_preset = MockQueryPresets.ITEM_4
    mock_prop = NonCallableMock()
    res = instance.check_supported(mock_preset, mock_prop)
    assert not res


def test_check_supported_for_preset_that_supports_all(instance):
    """
    Tests that check_supported method, for a preset with '*' - check that it supports all props,
    all props should return True
    """
    mock_preset = MockQueryPresets.ITEM_1
    assert all(instance.check_supported(mock_preset, i) for i in list(MockProperties))


def test_check_preset_and_prop_supported(instance):
    """
    Tests that check_supported method works expectedly
    returns False if either Preset is not supported or Preset-Prop does not have a mapping
    """
    assert instance.check_supported(MockQueryPresets.ITEM_2, MockProperties.PROP_1)
    assert instance.check_supported(MockQueryPresets.ITEM_2, MockProperties.PROP_2)
    assert instance.check_supported(MockQueryPresets.ITEM_3, MockProperties.PROP_3)
    assert instance.check_supported(MockQueryPresets.ITEM_3, MockProperties.PROP_4)


@pytest.fixture(name="get_filter_func_runner")
def get_filter_func_runner_fixture(instance):
    """fixture that runs get_filter_func with valid kwargs"""

    def _get_filter_func_runner(mock_prop_func, mock_filter_func_kwargs=None):
        """
        function that runs get_filter_func with valid kwargs
        :param mock_prop_func: a mocked prop func
        :param mock_filter_func_kwargs: a mocked set of filter kwargs
        """

        filter_func = instance.get_filter_func(
            MockQueryPresets.ITEM_1,
            MockProperties.PROP_1,
            mock_prop_func,
            mock_filter_func_kwargs,
        )

        # run the filter function - invokes _filter_func_wrapper
        mock_obj = NonCallableMock()
        res = filter_func(mock_obj)
        mock_prop_func.assert_called_once_with(mock_obj)
        return res

    return _get_filter_func_runner


def test_get_filter_func_valid_kwargs(get_filter_func_runner, mock_filter):
    """
    Tests calling get_filter_func with valid kwargs.
    get_filter_func will get a simple stub method that will output whatever value that kwarg "out" holds
    """
    mock_prop_func = MagicMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    res = get_filter_func_runner(mock_prop_func, mock_kwargs)

    mock_filter.assert_has_calls(
        [
            # first call from _check_filter_func
            call(None, **mock_kwargs),
            # second call from _filter_func_wrapper
            call(mock_prop_func.return_value, **mock_kwargs),
        ]
    )
    assert res == mock_filter.return_value


def test_get_filter_func_valid_kwargs_no_params(mock_filter, get_filter_func_runner):
    """
    Tests calling get_filter_func with valid kwargs - filter takes no extra params.
    get_filter_func will get a simple stub method that will output whatever value that kwarg "out" holds
    """
    mock_prop_func = MagicMock()
    mock_kwargs = None

    res = get_filter_func_runner(mock_prop_func, mock_kwargs)

    mock_filter.assert_has_calls(
        [
            # first call from _check_filter_func
            call(None),
            # second call from _filter_func_wrapper
            call(mock_prop_func.return_value),
        ]
    )
    assert res == mock_filter.return_value


def test_get_filter_func_prop_func_raises_error(mock_filter, get_filter_func_runner):
    """
    Tests calling get_filter_func with prop func that raises AttributeError when invoked
    filter_func_wrapper should return False in this case
    """
    mock_prop_func = MagicMock()
    mock_prop_func.side_effect = AttributeError
    mock_kwargs = None

    res = get_filter_func_runner(mock_prop_func, mock_kwargs)

    mock_filter.assert_has_calls(
        [
            # first call from _check_filter_func
            call(None),
            # second call doesn't happen since prop func fails
        ]
    )
    assert res is False


def test_get_filter_func_preset_invalid(instance):
    """
    Tests get_filter_func method with invalid preset
    should raise QueryPresetMappingError
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
    Tests get_filter_func when prop is not valid.
    Should raise QueryPresetMappingError
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


@pytest.mark.parametrize(
    "error_type", [ParseQueryError, TypeError, NameError, MissingMandatoryParamError]
)
def test_get_filter_func_filter_raises_error(error_type, instance, mock_filter):
    """
    Tests get_filter_func method when filter function raises an error.
    Should raise QueryPresetMappingError
    """
    mock_prop_func = MagicMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    mock_filter.side_effect = error_type

    with pytest.raises(QueryPresetMappingError):
        instance.get_filter_func(
            MockQueryPresets.ITEM_1,
            MockProperties.PROP_1,
            mock_prop_func,
            mock_kwargs,
        )

    mock_filter.assert_called_once_with(None, **mock_kwargs)
