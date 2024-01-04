from unittest.mock import MagicMock, NonCallableMock

import pytest

from exceptions.query_preset_mapping_error import QueryPresetMappingError
from openstack_query.handlers.server_side_handler import ServerSideHandler
from tests.lib.openstack_query.mocks.mocked_props import MockProperties
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets


@pytest.fixture(name="mock_server_side_mappings")
def server_side_mapping_fixture():
    """
    Sets up a set of mock mappings between a preset-prop pair and
     a set of server side filters
    """

    return {
        MockQueryPresets.ITEM_1: {
            MockProperties.PROP_1: MagicMock(),
            MockProperties.PROP_2: MagicMock(),
        },
        MockQueryPresets.ITEM_2: {
            MockProperties.PROP_3: MagicMock(),
            MockProperties.PROP_4: MagicMock(),
        },
    }


@pytest.fixture(name="instance")
def instance_fixture(mock_server_side_mappings):
    """
    Prepares an instance to be used in tests
    """
    return ServerSideHandler(mock_server_side_mappings)


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


@pytest.fixture(name="get_filters_runner")
def get_filters_runner_fixture(mock_server_side_mappings, instance):
    """
    Fixture to setup and test get_filters function
    """

    def _get_filters_runner(preset, prop, filter_func_output, expected_out):
        mock_filter_func = mock_server_side_mappings[preset][prop]
        mock_filter_func.return_value = filter_func_output
        mock_params = {"arg1": "val1", "arg2": "val2"}

        res = instance.get_filters(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
        )

        mock_filter_func.assert_called_once_with(**mock_params)
        assert res == expected_out

    return _get_filters_runner


def test_get_filters_return_single_filter(get_filters_runner):
    """
    Tests that get_filters method, where a single set of server-side filters
    is returned appropriately for valid preset-property pair. Should return as a singleton list
    """
    mock_filter_return = NonCallableMock()
    get_filters_runner(
        MockQueryPresets.ITEM_1,
        MockProperties.PROP_1,
        mock_filter_return,
        [mock_filter_return],
    )


def test_get_filters_return_multi_filter(get_filters_runner):
    """
    Tests that get_filters method, where a list of server-side filters returned
    is returned appropriately for valid preset-property pair. Should return as is
    """
    mock_filter_return = [NonCallableMock()]
    get_filters_runner(
        MockQueryPresets.ITEM_1,
        MockProperties.PROP_1,
        mock_filter_return,
        mock_filter_return,
    )


def test_get_filters_no_mapping(instance):
    """
    Tests get_filters method, where there is no mapping for preset-property pair given
    """
    # preset has mappings, but property not compatible
    assert (
        instance.get_filters(
            MockQueryPresets.ITEM_1, MockProperties.PROP_4, {"arg1": "val1"}
        )
        is None
    )

    # preset does not have mappings
    assert (
        instance.get_filters(
            MockQueryPresets.ITEM_3, MockProperties.PROP_4, {"arg1": "val1"}
        )
        is None
    )


@pytest.mark.parametrize("error_type", [KeyError, TypeError])
def test_get_filters_filter_func_raises_error(
    error_type, mock_server_side_mappings, instance
):
    """
    Tests get_filters method, when trying to run the function to get server-side filters
    returns an error indicating that required parameters were missing/malformed. In this case, we should raise a
    QueryPresetMappingError
    """

    mock_filter_func = mock_server_side_mappings[MockQueryPresets.ITEM_1][
        MockProperties.PROP_1
    ]
    mock_filter_func.side_effect = error_type
    with pytest.raises(QueryPresetMappingError):
        instance.get_filters(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, {"arg1": "val1"}
        )


def test_get_filters_valid_not_list(mock_server_side_mappings, instance):
    """
    Tests that get_filters method, server-side filters returned appropriately for valid
    preset-property pair
    """
    mock_params = {"arg1": "val1", "arg2": "val2"}
    mock_filter = NonCallableMock()
    mock_filter_func = mock_server_side_mappings[MockQueryPresets.ITEM_1][
        MockProperties.PROP_1
    ]
    mock_filter_func.return_value = mock_filter

    res = instance.get_filters(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
    )

    mock_filter_func.assert_called_once_with(**mock_params)
    assert res == [mock_filter]


def test_get_filters_valid_list(mock_server_side_mappings, instance):
    """
    Tests that get_filters method, server-side filters returned appropriately for valid
    preset-property pair where filters returned by filter_func is a list
    """
    mock_params = {"arg1": "val1", "arg2": "val2"}
    mock_filter = NonCallableMock()
    mock_filter_func = mock_server_side_mappings[MockQueryPresets.ITEM_1][
        MockProperties.PROP_1
    ]
    mock_filter_func.return_value = [mock_filter]

    res = instance.get_filters(
        MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
    )

    mock_filter_func.assert_called_once_with(**mock_params)
    assert res == [mock_filter]
