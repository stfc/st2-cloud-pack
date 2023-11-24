from pathlib import WindowsPath, Path
from unittest.mock import MagicMock, patch, call, NonCallableMock, mock_open
import pytest

from exceptions.parse_query_error import ParseQueryError
from openstack_query.query_blocks.query_output import QueryOutput
from enums.query.props.server_properties import ServerProperties
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with mocked prop_enum_cls inject
    """
    mock_prop_enum_cls = MockProperties
    return QueryOutput(prop_enum_cls=mock_prop_enum_cls)


def test_selected_props(instance):
    """
    Tests that property method to get selected props works expectedly
    method should return self._props as a list
    """

    val = {
        MockProperties.PROP_1,
        MockProperties.PROP_2,
        MockProperties.PROP_3,
    }
    instance.selected_props = val
    assert instance.selected_props == list(val)


def test_selected_props_empty(instance):
    """
    Tests selected property method returns empty list when no props selected
    """
    assert instance.selected_props == []


def test_validate_groups_empty(instance):
    """
    Tests validate groups returns result if groups empty
    """
    mock_results = {"group1": "val1", "group2": "val2", "group3": "val3"}
    mock_groups = None
    # pylint:disable=protected-access
    assert instance._validate_groups(mock_results, mock_groups) == mock_results


def test_validate_groups_valid(instance):
    """
    Tests validate groups returns subset of results that match given set of groups
    """
    mock_results = {"group1": "val1", "group2": "val2", "group3": "val3"}
    mock_groups = ["group1", "group2"]

    # pylint:disable=protected-access
    assert instance._validate_groups(mock_results, mock_groups) == {
        "group1": "val1",
        "group2": "val2",
    }


def test_validate_groups_invalid_keys(instance):
    """
    Tests validate groups returns error if value given in groups does not exist
    as a key in results
    """
    mock_results = {"group1": "val1", "group2": "val2", "group3": "val3"}
    mock_groups = ["invalid_group"]
    with pytest.raises(ParseQueryError):
        # pylint:disable=protected-access
        instance._validate_groups(mock_results, mock_groups)


def test_validate_groups_results_not_dict(instance):
    """
    Tests validate groups returns error if results given is not a dictionary
    """
    mock_results = ["val1", "val2"]
    with pytest.raises(ParseQueryError):
        # pylint:disable=protected-access
        instance._validate_groups(mock_results, NonCallableMock())


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
def test_to_objects(mock_validate_groups, instance):
    """
    Tests that to_objects method calls results_container.to_objects and martials
    results into _validate_groups() then outputs the result
    """
    mock_results_container = MagicMock()
    mock_groups = NonCallableMock()

    res = instance.to_objects(mock_results_container, mock_groups)
    mock_results_container.to_objects.assert_called_once_with()
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_objects.return_value, mock_groups
    )
    assert res == mock_validate_groups.return_value


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput.flatten")
def test_to_props_no_flatten(mock_flatten, mock_validate_groups, instance):
    """
    Tests that to_props method calls results_container.to_props and martials
    results into _validate_groups() then outputs the result. Does not call flatten
    """
    mock_results_container = MagicMock()
    mock_groups = NonCallableMock()
    instance.selected_props = ["prop1", "prop2", "prop3"]

    res = instance.to_props(mock_results_container, False, mock_groups)
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )
    mock_flatten.assert_not_called()
    assert res == mock_validate_groups.return_value


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput.flatten")
def test_to_props_with_flatten(mock_flatten, mock_validate_groups, instance):
    """
    Tests that to_props method calls results_container.to_props, martials
    results into _validate_groups(), then flatten() and returns results
    """
    mock_results_container = MagicMock()
    mock_groups = NonCallableMock()
    instance.selected_props = ["prop1", "prop2", "prop3"]

    res = instance.to_props(mock_results_container, True, mock_groups)
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )
    mock_flatten.assert_called_once_with(mock_validate_groups.return_value)
    assert res == mock_flatten.return_value


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_html_with_list_results(mock_generate_table, mock_validate_groups, instance):
    """
    Tests that to_html function - when results are outputted as a list
    method should call generate_table with return_html = True once
    """
    mock_results_container = MagicMock()
    mock_title = "mock title"
    mock_groups = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    instance.selected_props = ["prop1", "prop2", "prop3"]
    mock_generate_table.return_value = "mock out"

    res = instance.to_html(
        mock_results_container, mock_title, mock_groups, **mock_kwargs
    )
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )

    mock_generate_table.assert_called_once_with(
        mock_validate_groups.return_value, return_html=True, title=None, **mock_kwargs
    )
    assert res == "<b> mock title: </b><br/> mock out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_html_with_no_title(mock_generate_table, mock_validate_groups, instance):
    """
    Tests that to_html function works expectedly - when given list as results and no title
    method should call generate_table with return_html once
    """
    mock_results_container = MagicMock()
    mock_groups = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    instance.selected_props = ["prop1", "prop2", "prop3"]
    mock_generate_table.return_value = "mock out"

    res = instance.to_html(mock_results_container, groups=mock_groups, **mock_kwargs)
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )

    mock_generate_table.assert_called_once_with(
        mock_validate_groups.return_value, return_html=True, title=None, **mock_kwargs
    )
    assert res == "mock out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_html_with_grouped_results(
    mock_generate_table, mock_validate_groups, instance
):
    """
    Tests that to_html function works expectedly - when results are grouped - outputted as a dict
    method should call generate_table with return_html for each group
    """

    mock_results_container = MagicMock()
    mock_title = "mock title"
    mock_groups = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    instance.selected_props = ["prop1", "prop2", "prop3"]

    mocked_results = {"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]}
    mock_validate_groups.return_value = mocked_results
    mock_generate_table.side_effect = ["1 out, ", "2 out"]

    res = instance.to_html(
        mock_results_container, mock_title, mock_groups, **mock_kwargs
    )
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )

    mock_generate_table.assert_has_calls(
        [
            call(
                ["obj1", "obj2"],
                return_html=True,
                title="<b> group1: </b><br/> ",
                **mock_kwargs
            ),
            call(
                ["obj3", "obj4"],
                return_html=True,
                title="<b> group2: </b><br/> ",
                **mock_kwargs
            ),
        ]
    )
    assert res == "<b> mock title: </b><br/> 1 out, 2 out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_string_with_list_results(
    mock_generate_table, mock_validate_groups, instance
):
    """
    Tests that to_string function - when results are outputted as a list
    method should call generate_table with return_html = False once
    """
    mock_results_container = MagicMock()
    mock_title = "mock title"
    mock_groups = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    instance.selected_props = ["prop1", "prop2", "prop3"]
    mock_generate_table.return_value = "mock out"

    res = instance.to_string(
        mock_results_container, mock_title, mock_groups, **mock_kwargs
    )
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )

    mock_generate_table.assert_called_once_with(
        mock_validate_groups.return_value, return_html=False, title=None, **mock_kwargs
    )

    assert "mock title:\nmock out" == res


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_string_with_no_title(mock_generate_table, mock_validate_groups, instance):
    """
    Tests that to_string - when given list as results and no title
    method should call generate_table with return_html once
    """
    mock_results_container = MagicMock()
    mock_groups = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    instance.selected_props = ["prop1", "prop2", "prop3"]
    mock_generate_table.return_value = "mock out"

    res = instance.to_string(mock_results_container, groups=mock_groups, **mock_kwargs)
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )

    mock_generate_table.assert_called_once_with(
        mock_validate_groups.return_value, return_html=False, title=None, **mock_kwargs
    )
    assert res == "mock out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._validate_groups")
@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_string_with_grouped_results(
    mock_generate_table, mock_validate_groups, instance
):
    """
    Tests that to_html function works expectedly - when results are grouped - outputted as a dict
    method should call generate_table with return_html for each group
    """

    mock_results_container = MagicMock()
    mock_title = "mock title"
    mock_groups = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    instance.selected_props = ["prop1", "prop2", "prop3"]

    mocked_results = {"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]}
    mock_validate_groups.return_value = mocked_results
    mock_generate_table.side_effect = ["1 out, ", "2 out"]

    res = instance.to_string(
        mock_results_container, mock_title, mock_groups, **mock_kwargs
    )
    mock_results_container.to_props.assert_called_once_with("prop1", "prop2", "prop3")
    mock_validate_groups.assert_called_once_with(
        mock_results_container.to_props.return_value, mock_groups
    )

    mock_generate_table.assert_has_calls(
        [
            call(["obj1", "obj2"], return_html=False, title="group1:\n", **mock_kwargs),
            call(["obj3", "obj4"], return_html=False, title="group2:\n", **mock_kwargs),
        ]
    )
    assert "mock title:\n1 out, 2 out" == res


def test_generate_table_no_vals(instance):
    """
    Tests that generate_table function works expectedly - when results empty
    method should return No results found
    """
    results_dict_0 = []

    # pylint:disable=protected-access
    res = instance._generate_table(
        results_dict_0, title="mock title", return_html=False
    )
    assert "mock titleNo results found" == res


@pytest.mark.parametrize(
    "return_html, expected_tablefmt", [(True, "html"), (False, "grid")]
)
@patch("openstack_query.query_blocks.query_output.tabulate")
def test_generate_table_single_row_single_col(
    mock_tabulate, return_html, expected_tablefmt, instance
):
    """
    Tests that generate_table function works expectedly - with single result, single selected prop
    method should format results dict and call tabulate and return a string of the tabled results
    """
    mock_results = [{"prop1": "val1"}]
    mock_tabulate.return_value = "mock out"

    # pylint:disable=protected-access
    res = instance._generate_table(mock_results, return_html=return_html, title=None)
    mock_tabulate.assert_called_once_with(
        [["val1"]], ["prop1"], tablefmt=expected_tablefmt
    )
    assert res == "mock out\n\n"


@pytest.mark.parametrize(
    "return_html, expected_tablefmt", [(True, "html"), (False, "grid")]
)
@patch("openstack_query.query_blocks.query_output.tabulate")
def test_generate_table_multi_row_single_col(
    mock_tabulate, return_html, expected_tablefmt, instance
):
    """
    Tests that generate_table function works expectedly - with multiple results, single selected prop
    method should format results dict and call tabulate and return a string of the tabled results
    """
    mock_results = [{"prop1": "val1"}, {"prop1": "val2"}]
    mock_tabulate.return_value = "mock out"

    # pylint:disable=protected-access
    res = instance._generate_table(mock_results, return_html=return_html, title=None)
    mock_tabulate.assert_called_once_with(
        [["val1"], ["val2"]], ["prop1"], tablefmt=expected_tablefmt
    )
    assert res == "mock out\n\n"


@pytest.mark.parametrize(
    "return_html, expected_tablefmt", [(True, "html"), (False, "grid")]
)
@patch("openstack_query.query_blocks.query_output.tabulate")
def test_generate_table_single_row_multi_col(
    mock_tabulate, return_html, expected_tablefmt, instance
):
    """
    Tests that generate_table function works expectedly - with single result, multiple selected prop
    method should format results dict and call tabulate and return a string of the tabled results
    """
    mock_results = [{"prop1": "val1", "prop2": "val2"}]
    mock_tabulate.return_value = "mock out"

    # pylint:disable=protected-access
    res = instance._generate_table(mock_results, return_html=return_html, title=None)
    mock_tabulate.assert_called_once_with(
        [["val1", "val2"]], ["prop1", "prop2"], tablefmt=expected_tablefmt
    )
    assert res == "mock out\n\n"


@pytest.mark.parametrize(
    "return_html, expected_tablefmt", [(True, "html"), (False, "grid")]
)
@patch("openstack_query.query_blocks.query_output.tabulate")
def test_generate_table_multi_row_multi_col(
    mock_tabulate, return_html, expected_tablefmt, instance
):
    """
    Tests that generate_table function works expectedly - with multiple results, multiple selected prop
    method should format results dict and call tabulate and return a string of the tabled results
    """
    mock_results = [
        {"prop1": "val1", "prop2": "val2"},
        {"prop1": "val3", "prop2": "val4"},
    ]
    mock_tabulate.return_value = "mock out"

    # pylint:disable=protected-access
    res = instance._generate_table(mock_results, return_html=return_html, title=None)
    mock_tabulate.assert_called_once_with(
        [["val1", "val2"], ["val3", "val4"]],
        ["prop1", "prop2"],
        tablefmt=expected_tablefmt,
    )
    assert res == "mock out\n\n"


def test_parse_select_with_select_all(instance):
    """
    tests that parse select works expectedly - when called from select_all() - no props given
    method should set props internal attribute to all available props supported by prop_handler
    """
    # if select_all flag set, get all props
    instance.parse_select(select_all=True)
    assert instance.selected_props == list(set(MockProperties))


def test_parse_select_given_args(instance):
    """
    tests that parse select works expectedly - when called from select() - where props args given
    method should set check each given prop to see if mapping exists in prop_handler and
    add to internal attribute set props
    """
    # if given props
    instance.parse_select(MockProperties.PROP_1, MockProperties.PROP_2)
    assert instance.selected_props, [MockProperties.PROP_1, MockProperties.PROP_2]


def test_parse_select_given_invalid(instance):
    """
    Tests that parse_select works expectedly
    method should raise error when given an invalid prop enum
    """

    # server prop enums are invalid here and should be picked up
    with pytest.raises(ParseQueryError):
        instance.parse_select(MockProperties.PROP_1, ServerProperties.SERVER_ID)


def test_parse_select_overwrites_old(instance):
    """
    Tests that parse_select overwrites old selected_props
    method should overwrite internal attribute selected_props if already set
    """
    instance.selected_props = [MockProperties.PROP_1]
    instance.parse_select(MockProperties.PROP_2)
    assert instance.selected_props == [MockProperties.PROP_2]


def test_flatten_empty(instance):
    """
    Tests that flatten() function works expectedly - with empty list/dict
    """
    assert instance.flatten([]) is None
    assert instance.flatten({}) is None


def test_flatten_with_list(instance):
    """
    Tests that flatten() functions works expectedly - with a non-empty list
    should call flatten_list
    """
    with patch(
        "openstack_query.query_blocks.query_output.QueryOutput._flatten_list"
    ) as mock_flatten_list:
        res = instance.flatten(["obj1", "obj2"])
    mock_flatten_list.assert_called_once_with(["obj1", "obj2"])
    assert res == mock_flatten_list.return_value


def test_flatten_with_dict_one_group(instance):
    """
    Tests that flatten() functions works expectedly
    with a non-empty results with one group - should call flatten list once
    """
    with patch(
        "openstack_query.query_blocks.query_output.QueryOutput._flatten_list"
    ) as mock_flatten_list:
        res = instance.flatten({"group1": ["obj1", "obj2"]})
    mock_flatten_list.assert_called_once_with(["obj1", "obj2"])
    assert res == {"group1": mock_flatten_list.return_value}


def test_flatten_with_dict_many_groups(instance):
    """
    Tests that flatten() functions works expectedly
    with a non-empty result with many groups - should call flatten list with each group
    """
    with patch(
        "openstack_query.query_blocks.query_output.QueryOutput._flatten_list"
    ) as mock_flatten_list:
        res = instance.flatten({"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]})
    mock_flatten_list.assert_has_calls([call(["obj1", "obj2"]), call(["obj3", "obj4"])])
    assert res == {
        "group1": mock_flatten_list.return_value,
        "group2": mock_flatten_list.return_value,
    }


def test_flatten_list_empty_list(instance):
    """
    Tests that flatten_list() function works expectedly
    with an empty list - should return an empty dictionary
    """
    # pylint:disable=protected-access
    assert instance._flatten_list([]) == {}


def test_flatten_list_one_key_one_item(instance):
    """
    Tests flatten_list() function with one item with one key-value pair
    """
    # pylint:disable=protected-access
    assert instance._flatten_list([{"prop1": "val1"}]) == {"prop1": ["val1"]}


def test_flatten_list_many_keys_one_item(instance):
    """
    Tests flatten_list() function with one item with many key-value pairs
    """
    # pylint:disable=protected-access
    assert instance._flatten_list([{"prop1": "val1", "prop2": "val2"}]) == {
        "prop1": ["val1"],
        "prop2": ["val2"],
    }


def test_flatten_list_many_keys_many_items(instance):
    """
    Tests flatten_list() function with many items with many key-value pairs
    """
    # pylint:disable=protected-access
    assert instance._flatten_list(
        [{"prop1": "val1", "prop2": "val2"}, {"prop1": "val3", "prop2": "val4"}]
    ) == {"prop1": ["val1", "val3"], "prop2": ["val2", "val4"]}


def test_flatten_with_duplicates(instance):
    """
    Tests flatten_list() function with duplicates - should keep duplicates as is
    """
    # pylint:disable=protected-access
    assert instance._flatten_list(
        [{"prop1": "val1", "prop2": "val2"}, {"prop1": "val1", "prop2": "val2"}]
    ) == {"prop1": ["val1", "val1"], "prop2": ["val2", "val2"]}


@patch("builtins.open", new_callable=mock_open)
@patch("csv.DictWriter")
def test_to_csv_with_valid_parameters(mock_dict_writer, mock_file, example_data):
    """With Valid Parameters"""
    to_csv(example_data, "csv_files")

    mock_file.assert_called_once_with(WindowsPath('csv_files/query_out.csv'), 'w', encoding='utf-8')
    mock_dict_writer.assert_called_once_with(
        mock_file.return_value, fieldnames=example_data[0].keys()
    )
    mock_dict_writer.return_value.writeheader.assert_called_once()
    mock_dict_writer.return_value.writerows.assert_called_once_with(example_data)


def test_to_csv_fails():
    with pytest.raises(RuntimeError):
        to_csv([], "invalid path")


@patch("workflows.csv.csv_actions.to_csv")
def test_to_csv_grouped_loop_empty_input(mock_to_csv):
    """loop is given: 0 Items"""
    mock_to_csv.assert_not_called()


@patch("workflows.csv.csv_actions.to_csv_list")
def test_to_csv_grouped_loop_one_input(mock_to_csv):
    """mock to_cs outputs"""

    example_grouped_data = {
        "user_name is user1": [
            {
                "server_id": "server_id1",
                "server_name": "server1",
                "user_id": "user_id1",
                "user_name": "user1",
            },
            {
                "server_id": "server_id2",
                "server_name": "server2",
                "user_id": "user_id1",
                "user_name": "user1",
            },
        ],
    }

    """Run To csv"""
    to_csv_dictionary(example_grouped_data, "csv_files")

    """loop is given: 1 Items"""
    mock_to_csv.assert_called_once_with(
        example_grouped_data["user_name is user1"], Path("csv_files/user_name is user1.csv")

    )


@patch("workflows.csv.csv_actions.to_csv_list")
def test_to_csv_grouped_loop_more_than_one_input(mock_to_csv, example_grouped_data):
    """mock to_cs outputs"""

    """Run To csv"""
    to_csv_dictionary(example_grouped_data, "csv_files")

    """
    loop is given: 1 Items
    This bit need rewriting to check for multiple outputs instead of 1.
    """
    mock_to_csv.assert_called_with(
        example_grouped_data["user_name is user2"], Path("csv_files/user_name is user2.csv")
    )