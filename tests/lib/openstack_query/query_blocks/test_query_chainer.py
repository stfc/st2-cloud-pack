from unittest.mock import MagicMock, patch

import pytest

from enums.query.query_presets import QueryPresetsGeneric
from exceptions.query_chaining_error import QueryChainingError
from openstack_query.query_blocks.query_chainer import QueryChainer
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance of QueryChainer with mocked chain mappings
    """

    # sets mock chain mappings
    # mocks MockProperties PROP_1 to PROP_2 - contrived example since
    # the properties should belong to 2 different Queries to be useful
    # - but this is just a test
    _chain_mappings = {MockProperties.PROP_1: MockProperties.PROP_2}
    return QueryChainer(_chain_mappings)


@pytest.fixture(name="run_parse_then_query_valid")
def run_parse_then_query_valid_fixture(instance):
    """
    Fixture that runs a then_query() method test case
    """

    @patch("openstack_query.query_factory.QueryFactory")
    @patch("openstack_query.api.query_api.QueryAPI")
    @patch("openstack_query.query_blocks.query_chainer.QueryTypes")
    def _run_parse_then_query_valid(
        mock_keep_previous_results,
        mock_query_types_cls,
        mock_query_api,
        mock_query_factory,
    ):
        """
        runs a then_query() test case with keep_previous_results being either True or False
        """
        mock_curr_query = MagicMock()
        mock_curr_query.chainer.get_link_props.return_value = ("curr-prop", "new-prop")

        mock_curr_query_results = {"prop-val1": "out1", "prop-val2": "out2"}
        mock_curr_query.group_by.return_value.to_list.return_value = (
            mock_curr_query_results
        )

        to_forward = None
        if mock_keep_previous_results:
            to_forward = ("new-prop", mock_curr_query_results)

        res = instance.parse_then(
            curr_query=mock_curr_query,
            query_type="query-type",
            keep_previous_results=mock_keep_previous_results,
        )

        mock_query_types_cls.from_string.assert_called_once_with("query-type")

        mock_curr_query.group_by.assert_called_once_with("curr-prop")
        mock_curr_query.group_by.return_value.to_list.assert_called_once()

        mock_query_factory.build_query_deps.assert_called_once_with(
            mock_query_types_cls.from_string.return_value.value, to_forward
        )

        mock_query_api.assert_called_once_with(
            mock_query_factory.build_query_deps.return_value
        )

        mock_query_api.return_value.where.assert_called_once_with(
            QueryPresetsGeneric.ANY_IN, "new-prop", values=["prop-val1", "prop-val2"]
        )
        assert res == mock_query_api.return_value.where.return_value

    return _run_parse_then_query_valid


def test_get_chaining_props(instance):
    """
    Tests that get_chaining_props method works as expected
    should return a list of chain_mapping keys
    """
    assert instance.get_chaining_props() == [MockProperties.PROP_1]


def test_check_prop_supported_valid(instance):
    """
    Tests check_prop_supported method - with a valid property
    should return True since property is key in chain_mappings
    """
    assert instance.check_prop_supported(MockProperties.PROP_1)


def test_check_prop_supported_invalid(instance):
    """
    Tests check_prop_supported method - with an invalid property
    should return False since property is not a key in chain_mappings
    """
    assert not instance.check_prop_supported(MockProperties.PROP_2)


def test_get_link_props_valid_query(instance):
    """
    Tests get_link_props method - with valid query - which has a chain mapping
    should return link props
    """
    # a set of mock_properties that the input query returns
    mock_props = [MockProperties.PROP_2, MockProperties.PROP_3]

    mock_query = MagicMock()
    mock_query.value.get_prop_mapping.return_value = mock_props

    mock_link_props = instance.get_link_props(mock_query)
    assert mock_link_props[0] == MockProperties.PROP_1
    assert mock_link_props[1] == MockProperties.PROP_2


def test_get_link_props_no_mapping(instance):
    """
    Tests get_link_props method - with invalid query chain mappings
    should return none
    """
    mock_props = [MockProperties.PROP_3, MockProperties.PROP_4]

    mock_query = MagicMock()
    mock_query.value.get_prop_mapping.return_value = mock_props

    assert instance.get_link_props(mock_query) is None


def test_parse_then_query_valid_no_forward(run_parse_then_query_valid):
    """
    Tests parse_then method - with valid params
    should run parse_then with keep_previous_results = False
    """
    run_parse_then_query_valid(False)


def test_parse_then_query_valid_with_forward(run_parse_then_query_valid):
    """
    Tests parse_then method - with valid params
    should run parse_then with forward outputs = True
    """
    run_parse_then_query_valid(True)


def test_parse_then_no_link_props(instance):
    """
    Tests parse_then method - where no link props available
    should raise error
    """
    mock_curr_query = MagicMock()
    mock_curr_query.chainer.get_link_props.return_value = None

    mock_query_type = MagicMock()

    with pytest.raises(QueryChainingError):
        instance.parse_then(
            curr_query=mock_curr_query,
            query_type=mock_query_type,
            keep_previous_results=False,
        )
        mock_curr_query.chainer.get_link_props.assert_called_once_with(mock_query_type)


def test_parse_then_no_results(instance):
    """
    Tests parse_then method - where no results found
    should raise error
    """
    mock_curr_query = MagicMock()
    mock_curr_query.chainer.get_link_props.return_value = ("curr-prop", "new-prop")
    mock_curr_query.group_by.return_value.to_list.return_value = None
    mock_query_type = MagicMock()

    with pytest.raises(QueryChainingError):
        instance.parse_then(
            curr_query=mock_curr_query,
            query_type=mock_query_type,
            keep_previous_results=False,
        )
        mock_curr_query.chainer.get_link_props.assert_called_once_with(mock_query_type)
        mock_curr_query.group_by.assert_called_once_with("curr-prop")
        mock_curr_query.group_by.return_value.to_list.assert_called_once()
