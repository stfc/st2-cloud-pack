from unittest.mock import patch, NonCallableMock
import pytest

from openstack_query.query_blocks.query_parser import QueryParser


@pytest.fixture(name="instance")
@patch("openstack_query.query_blocks.query_parser.QueryGrouper")
@patch("openstack_query.query_blocks.query_parser.QuerySorter")
def instance_fixture(mock_sorter, mock_grouper):
    """
    Returns an instance of QueryParser with mocked injects
    """
    mock_prop_enum_cls = NonCallableMock()
    parser = QueryParser(mock_prop_enum_cls)
    mock_sorter.assert_called_once_with(mock_prop_enum_cls)
    mock_grouper.assert_called_once_with(mock_prop_enum_cls)
    return parser


def test_parse_group_by(instance):
    """
    Tests parse_group_by method forwards onto grouper
    """
    mock_group_by = NonCallableMock()
    mock_group_ranges = NonCallableMock()
    mock_include_missing = NonCallableMock()
    instance.parse_group_by(mock_group_by, mock_group_ranges, mock_include_missing)
    instance.grouper.parse_group_by.assert_called_once_with(
        mock_group_by, mock_group_ranges, mock_include_missing
    )


def test_parse_sort_by(instance):
    """
    Tests parse_sort_by method forwards onto sorter
    """
    mock_sort_by = NonCallableMock()
    instance.parse_sort_by(mock_sort_by)
    instance.sorter.parse_sort_by(mock_sort_by)


def test_run_parser_sort_by_only(instance):
    """
    Tests run_parser method with only sort_by being set
    """
    instance.parse_sort_by(NonCallableMock())
    mock_obj_list = NonCallableMock()
    res = instance.run_parser(mock_obj_list)
    instance.sorter.run_sort_by.assert_called_once_with(mock_obj_list)
    assert res == instance.sorter.run_sort_by.return_value


def test_run_parser_group_by_only(instance):
    """
    Tests run_parser method with only group_by being set
    """
    instance.parse_group_by(NonCallableMock())
    mock_obj_list = NonCallableMock()
    res = instance.run_parser(mock_obj_list)
    instance.grouper.run_group_by.assert_called_once_with(mock_obj_list)
    assert res == instance.grouper.run_group_by.return_value


def test_run_parser_both_group_and_sort(instance):
    """
    Tests run_parser method with sort_by and group_by being set
    """
    instance.parse_sort_by(NonCallableMock())
    instance.parse_group_by(NonCallableMock())

    mock_obj_list = NonCallableMock()
    res = instance.run_parser(mock_obj_list)
    instance.sorter.run_sort_by.assert_called_once_with(mock_obj_list)
    instance.grouper.run_group_by.assert_called_once_with(
        instance.sorter.run_sort_by.return_value
    )
    assert res == instance.grouper.run_group_by.return_value


def test_run_parser_neither_set(instance):
    """
    Tests run_parser method with neither sort_by or group_by being set
    """
    mock_obj_list = NonCallableMock()
    res = instance.run_parser(mock_obj_list)
    assert res == mock_obj_list
