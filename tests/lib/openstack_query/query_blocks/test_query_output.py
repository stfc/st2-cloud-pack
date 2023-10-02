from unittest.mock import MagicMock, patch, call
import pytest

from openstack_query.query_blocks.query_output import QueryOutput
from exceptions.parse_query_error import ParseQueryError

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


@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_html_with_list_results(mock_generate_table, instance):
    """
    Tests that to_html function works expectedly - when given list as results and no title
    method should call generate_table with return_html once
    """

    mocked_results = ["obj1", "obj2"]
    mock_generate_table.return_value = "mock out"
    res = instance.to_html(results=mocked_results, title="mock title")
    mock_generate_table.assert_called_once_with(
        mocked_results, return_html=True, title=None
    )
    assert res == "<b> mock title </b><br/> mock out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_html_with_no_title(mock_generate_table, instance):
    """
    Tests that to_html function works expectedly - when given list as results and no title
    method should call generate_table with return_html once
    """

    mocked_results = ["obj1", "obj2"]
    mock_generate_table.return_value = "mock out"
    res = instance.to_html(results=mocked_results, title=None)
    mock_generate_table.assert_called_once_with(
        mocked_results, return_html=True, title=None
    )
    assert res == "mock out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_html_with_grouped_results(mock_generate_table, instance):
    """
    Tests that to_html function works expectedly - when given grouped results
    method should call generate_table with return_html for each group
    """
    mocked_results = {"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]}

    mock_generate_table.side_effect = ["1 out, ", "2 out"]
    res = instance.to_html(results=mocked_results, title="mock title")

    mock_generate_table.assert_has_calls(
        [
            call(["obj1", "obj2"], return_html=True, title="<b> group1: </b><br/> "),
            call(["obj3", "obj4"], return_html=True, title="<b> group2: </b><br/> "),
        ]
    )
    assert res == "<b> mock title </b><br/> 1 out, 2 out"


@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_string_with_list_results(mock_generate_table, instance):
    """
    Tests that to_string function works expectedly - when given list as results
    method should call generate_table with return_html set to false once
    """

    mocked_results = ["obj1", "obj2"]
    mock_generate_table.return_value = "mock out"

    res = instance.to_string(results=mocked_results, title="mock title")
    mock_generate_table.assert_called_once_with(
        mocked_results, return_html=False, title=None
    )
    assert "mock title:\nmock out" == res


@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_string_with_no_title(mock_generate_table, instance):
    """
    Tests that to_string function works expectedly - when given list as results and no title
    method should call generate_table with return_html set to false once
    """

    mocked_results = ["obj1", "obj2"]
    mock_generate_table.return_value = "mock out"

    res = instance.to_string(results=mocked_results, title=None)
    mock_generate_table.assert_called_once_with(
        mocked_results, return_html=False, title=None
    )
    assert "mock out" == res


@patch("openstack_query.query_blocks.query_output.QueryOutput._generate_table")
def test_to_string_with_grouped_results(mock_generate_table, instance):
    """
    Tests that to_string function works expectedly - when given grouped results
    method should call generate_table with return_html set to false for each group
    """
    mocked_results = {"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]}
    mock_generate_table.side_effect = ["1 out, ", "2 out"]

    res = instance.to_string(results=mocked_results, title="mock title")

    mock_generate_table.assert_has_calls(
        [
            call(["obj1", "obj2"], return_html=False, title="group1:\n"),
            call(["obj3", "obj4"], return_html=False, title="group2:\n"),
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
    assert "mock title\nNo results found" == res


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


def test_generate_output_no_items(instance):
    """
    Tests that generate_output method works expectedly - no openstack items
    method should return an empty list
    """
    assert instance.generate_output([]) == []


@patch("openstack_query.query_blocks.query_output.QueryOutput._parse_property")
def test_generate_output_one_item(mock_parse_property, instance):
    """
    Tests that generate_output method works expectedly - 1 item
    method should call parse_property with the singular item
    """
    item_1 = "openstack-resource-1"
    instance.generate_output([item_1])
    mock_parse_property.assert_called_once_with(item_1)


@patch("openstack_query.query_blocks.query_output.QueryOutput._parse_property")
def test_generate_output_multiple_items(mock_parse_property, instance):
    """
    Tests that generate_output method works expectedly - many items
    method should call parse_property multiple times with each item in item list
    """

    item_1 = "openstack-resource-1"
    item_2 = "openstack-resource-2"
    instance.generate_output([item_1, item_2])
    mock_parse_property.assert_has_calls(
        [call("openstack-resource-1"), call("openstack-resource-2")]
    )


@pytest.fixture(name="mock_get_prop_func")
def get_prop_func_fixture():
    """
    Stubs out get_prop_func method to return a
    stub callable based on prop enum
    """
    mock_prop_1_func = MagicMock()
    mock_prop_1_func.return_value = "prop 1 out"

    mock_prop_2_func = MagicMock()
    mock_prop_2_func.side_effect = AttributeError

    def _mock_get_prop_func(prop):
        return {
            MockProperties.PROP_1: mock_prop_1_func,
            MockProperties.PROP_2: mock_prop_2_func,
        }.get(prop, None)

    return _mock_get_prop_func


def test_parse_property_no_props(instance):
    """
    Tests that parse_property function works expectedly with 0 prop_funcs to apply
    method should return an empty dict
    """

    # mock get_prop_mapping to return a func string appropriate for that prop
    instance.selected_props = set()
    # pylint:disable=protected-access
    assert instance._parse_property("openstack-item") == {}


@patch.object(MockProperties, "get_prop_mapping")
def test_parse_property_one_prop(mock_get_prop_func, instance):
    """
    Tests that parse_property function works expectedly with 0 prop_funcs to apply
    method should return a dict with one key value pair (prop-name, prop-value)
    """
    mock_prop_func = MagicMock()
    mock_prop_func.return_value = "prop 1 out"

    mock_get_prop_func.return_value = mock_prop_func

    instance.selected_props = {MockProperties.PROP_1}
    # pylint:disable=protected-access
    res = instance._parse_property("openstack-item")

    mock_get_prop_func.assert_called_once_with(MockProperties.PROP_1)
    mock_prop_func.assert_called_once_with("openstack-item")

    assert res == {"prop_1": "prop 1 out"}


def test_parse_property_many_props(mock_get_prop_func, instance):
    """
    Tests that parse_property function works expectedly with 0 prop_funcs to apply
    method should return a dict with many key value pairs (prop-name, prop-value)
    """

    instance.selected_props = {MockProperties.PROP_1, MockProperties.PROP_2}

    with patch.object(
        MockProperties, "get_prop_mapping", wraps=mock_get_prop_func
    ) as mock_get_prop_mapping:
        # pylint:disable=protected-access
        res = instance._parse_property("openstack-item")

    assert res == {"prop_1": "prop 1 out", "prop_2": "Not Found"}
    mock_get_prop_mapping.assert_has_calls(
        [call(prop) for prop in instance.selected_props]
    )
