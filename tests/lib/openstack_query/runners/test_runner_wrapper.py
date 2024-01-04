from unittest.mock import MagicMock
import pytest

from exceptions.parse_query_error import ParseQueryError
from openstack_query.runners.runner_wrapper import RunnerWrapper


@pytest.fixture(name="instance")
def instance_fixture(mock_marker_prop_func):
    """
    Returns an instance to run tests with
    """
    return RunnerWrapper(marker_prop_func=mock_marker_prop_func)


def test_parse_subset_one_item_pass(instance):
    """
    tests parse_subset method with one item which should pass
    """
    instance.RESOURCE_TYPE = MagicMock
    mock_item = MagicMock()
    assert instance.parse_subset([mock_item]) == [mock_item]


def test_parse_subset_one_item_fails(instance):
    """
    tests parse_subset method with one item which should pass
    """
    instance.RESOURCE_TYPE = int
    with pytest.raises(ParseQueryError):
        instance.parse_subset([MagicMock()])


def test_parse_subset_many_items_valid(instance):
    """
    tests parse_subset method with one item where all should pass
    """

    instance.RESOURCE_TYPE = MagicMock
    mock_subset = [MagicMock(), MagicMock()]
    assert instance.parse_subset(mock_subset) == mock_subset


def test_run_with_subset_many_items_invalid(instance):
    """
    tests parse_subset method with one item invalid
    """
    instance.RESOURCE_TYPE = MagicMock
    invalid = 10
    with pytest.raises(ParseQueryError):
        instance.parse_subset([MagicMock(), MagicMock(), invalid])
