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
        return preset in [MockQueryPresets.ITEM_1, MockQueryPresets.ITEM_3]

    def _mock_check_supported(preset, prop):
        """A dummy function to mock the check_supported method on the client handler"""
        return preset == MockQueryPresets.ITEM_1 and prop == MockProperties.PROP_1

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


@pytest.fixture(name="parse_where_runner")
def parse_where_runner_fixture(
    instance, mock_server_side_handler, mock_valid_client_handler
):
    """
    This is a helper function that runs test cases of parse_where, where we expect it to complete successfully,
    In each test case we change what server_side_handler.get_filters and client_side_handler.get_filter_func returns
    This will change what is set in the client_side_filters and server_side_filters properties at the end
    """
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    # pylint:disable=too-many-arguments
    def _parse_where_runner(
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

    return _parse_where_runner


def test_parse_where_with_single_filter(parse_where_runner):
    """
    Tests parse_where where server-side-handler get_filters returns a single filter set
    """
    mock_client_filter = NonCallableMock()
    parse_where_runner(
        mock_get_filter_return=[{"filter1": "val1", "filter2": "val2"}],
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=[{"filter1": "val1", "filter2": "val2"}],
        expected_client_side_filters=[],
        expected_fallback_filters=[mock_client_filter],
    )


def test_parse_where_with_filter_list(parse_where_runner):
    """
    Tests parse_where where server-side-handler get_filters returns a list of filters
    """
    mock_client_filter = NonCallableMock()
    mock_server_filter = [{"filter1": "val1"}, {"filter2": "val2"}]
    parse_where_runner(
        mock_get_filter_return=mock_server_filter,
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=mock_server_filter,
        expected_client_side_filters=[],
        expected_fallback_filters=[mock_client_filter],
    )


def test_parse_where_with_no_filters(parse_where_runner):
    """
    Tests parse_where where server-side-handler get_filters returns no filters
    """
    mock_client_filter = NonCallableMock()
    mock_server_filter = None
    parse_where_runner(
        mock_get_filter_return=mock_server_filter,
        mock_get_filter_func_return=mock_client_filter,
        expected_server_side_filters=[],
        expected_client_side_filters=[mock_client_filter],
        expected_fallback_filters=[],
    )


@pytest.fixture(name="parse_where_runner_with_server_side_filter_set")
def parse_where_runner_with_server_side_filter_set_fixture(
    instance, parse_where_runner
):
    """
    A fixture to setup and test different test-cases for parse_where when server side filter is already set
    """

    def _server_side_filter_set_runner(
        expected_server_side_filters,
        current_server_side_filters,
        new_server_side_filters,
        expect_conflict=False,
    ):
        """
        function to setup and test different test-cases for parse_where when server side filter is already set.

        :param expected_server_side_filters: a list of server-side-filters we expect the parse_where method to set
        after calling it
        :param current_server_side_filters: a list of filters that have already been set
        :param new_server_side_filters: a list of filters to add
        :param expect_conflict: whether we expect server-side filter conflict to be detected
            - (If we expect a conflict, we expect that client-side filter will be set
            and the new server-side filters to be ignored)

        """
        instance.server_side_filters = current_server_side_filters

        filter1_fallback_func = NonCallableMock()
        instance.server_filter_fallback = [filter1_fallback_func]

        mock_client_filter = NonCallableMock()
        if expect_conflict:
            parse_where_runner(
                mock_get_filter_return=new_server_side_filters,
                mock_get_filter_func_return=mock_client_filter,
                expected_server_side_filters=expected_server_side_filters,
                expected_client_side_filters=[mock_client_filter],
                expected_fallback_filters=[filter1_fallback_func],
            )
        else:
            # conflict occurred - don't add server-side filter, instead add client_side filter
            parse_where_runner(
                mock_get_filter_return=new_server_side_filters,
                mock_get_filter_func_return=mock_client_filter,
                expected_server_side_filters=expected_server_side_filters,
                expected_client_side_filters=[],
                expected_fallback_filters=[filter1_fallback_func, mock_client_filter],
            )

    return _server_side_filter_set_runner


def test_parse_where_single_filter_set_non_conflicting(
    parse_where_runner_with_server_side_filter_set,
):
    """
    Tests parse_where where server-side-handler get_filters returns a single server-side filter, when another
    (non-conflicting) filter is already set - should concatenate the two filter sets into one set
    """
    parse_where_runner_with_server_side_filter_set(
        expected_server_side_filters=[{"filter1": "val1", "filter2": "val2"}],
        current_server_side_filters=[{"filter1": "val1"}],
        new_server_side_filters=[{"filter2": "val2"}],
    )


def test_parse_where_multi_filter_set_non_conflicting_add_single(
    parse_where_runner_with_server_side_filter_set,
):
    """
    Tests parse_where where server-side-handler get_filters returns a single server-side filter, when
    multiple (non-conflicting) filters already set - should concatenate new filter set onto each currently existing set
    """

    parse_where_runner_with_server_side_filter_set(
        expected_server_side_filters=[
            {"filter1": "val1", "filter3": "val3"},
            {"filter2": "val2", "filter3": "val3"},
        ],
        current_server_side_filters=[{"filter1": "val1"}, {"filter2": "val2"}],
        new_server_side_filters=[{"filter3": "val3"}],
    )


def test_parse_where_multi_filter_set_non_conflicting_add_multi(
    parse_where_runner_with_server_side_filter_set,
):
    """
    Tests parse_where where server-side-handler get_filters returns multiple server-side filters, when
    multiple (non-conflicting) filters already set - should create a list with all unique combinations of filters
    between the two lists
    """
    parse_where_runner_with_server_side_filter_set(
        expected_server_side_filters=[
            {"filter1": "val1", "filter3": "val3"},
            {"filter1": "val1", "filter4": "val4"},
            {"filter2": "val2", "filter3": "val3"},
            {"filter2": "val2", "filter4": "val4"},
        ],
        current_server_side_filters=[{"filter1": "val1"}, {"filter2": "val2"}],
        new_server_side_filters=[{"filter3": "val3"}, {"filter4": "val4"}],
    )


def test_parse_where_single_filter_set_conflicting(
    parse_where_runner_with_server_side_filter_set,
):
    """
    Tests parse_where where server-side-handler get_filters returns a single server-side filter, when another
    (conflicting) filter is already set - should add the new filter as a client-side filter
    """
    current_filters = [{"filter1": "val1"}]
    parse_where_runner_with_server_side_filter_set(
        expected_server_side_filters=current_filters,
        current_server_side_filters=current_filters,
        new_server_side_filters=[{"filter1": "val2"}],
        expect_conflict=True,
    )


def test_parse_where_multi_filter_set_conflicting_add_single(
    parse_where_runner_with_server_side_filter_set,
):
    """
    Tests parse_where where server-side-handler get_filters returns a single server-side filter, when
    multiple filters already set which are conflicting - should add a the new filter as a client-side filter
    """
    current_filters = [{"filter1": "val1"}, {"filter2": "val2"}]
    parse_where_runner_with_server_side_filter_set(
        expected_server_side_filters=current_filters,
        current_server_side_filters=current_filters,
        new_server_side_filters=[{"filter2": "val3"}],
        expect_conflict=True,
    )


def test_parse_where_multi_filter_set_conflicting_add_multi(
    parse_where_runner_with_server_side_filter_set,
):
    """
    Tests parse_where where server-side-handler get_filters returns multiple server-side filters, when
    multiple filters already set which conflict - should add the new filter as a client-side filter
    """
    current_filters = [
        {"filter1": "val1", "filter3": "val3"},
        {"filter1": "val1", "filter4": "val4"},
        {"filter2": "val2", "filter3": "val3"},
        {"filter2": "val2", "filter4": "val4"},
    ]
    parse_where_runner_with_server_side_filter_set(
        expected_server_side_filters=current_filters,
        current_server_side_filters=current_filters,
        new_server_side_filters=[{"filter3": "val4"}],
        expect_conflict=True,
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
            instance.parse_where(MockQueryPresets.ITEM_3, MockProperties.PROP_1)
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
