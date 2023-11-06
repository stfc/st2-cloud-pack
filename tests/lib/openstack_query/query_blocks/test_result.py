from unittest.mock import MagicMock, patch, call
import pytest

from openstack_query.query_blocks.result import Result
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


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


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with mocked prop_enum_cls inject
    """
    return Result(prop_enum_cls=MockProperties, obj_result=MagicMock())


def test_as_object():
    """
    test property getter as_object
    """
    mock_obj = MagicMock()
    assert Result(MockProperties, mock_obj).as_object() == mock_obj


@patch("openstack_query.query_blocks.result.Result.get_prop")
def test_as_props_no_forwarded_props(mock_get_prop, instance):
    """
    test property getter as_props just gets as_props when no forwarded_props given
    """
    mock_props = [MockProperties.PROP_1, MockProperties.PROP_2]
    res = instance.as_props(*mock_props)
    mock_get_prop.assert_has_calls(
        [call(MockProperties.PROP_1), call(MockProperties.PROP_2)]
    )

    assert res == {
        "prop_1": mock_get_prop.return_value,
        "prop_2": mock_get_prop.return_value,
    }


@patch("openstack_query.query_blocks.result.Result.get_prop")
def test_as_props_with_forwarded_props(mock_get_prop, instance):
    """
    test property getter as_props gets as_props result and forwarded_props set,
    concatenates them together
    """
    instance.update_forwarded_properties({"fwd_prop1": "val1", "fwd_prop2": "val2"})

    mock_props = [MockProperties.PROP_1, MockProperties.PROP_2]
    res = instance.as_props(*mock_props)
    mock_get_prop.assert_has_calls(
        [call(MockProperties.PROP_1), call(MockProperties.PROP_2)]
    )

    assert res == {
        "prop_1": mock_get_prop.return_value,
        "prop_2": mock_get_prop.return_value,
        "fwd_prop1": "val1",
        "fwd_prop2": "val2",
    }


def test_get_prop_found(mock_get_prop_func, instance):
    """
    Test get_prop method.
    Method should call prop_enum_cls.get_prop_mapping on given prop and run returned function on stored obj_result
    """
    with patch.object(
        MockProperties, "get_prop_mapping", wraps=mock_get_prop_func
    ) as mock_get_prop_mapping:
        res = instance.get_prop(MockProperties.PROP_1)
    mock_get_prop_mapping.assert_called_once_with(MockProperties.PROP_1)
    assert res == "prop 1 out"


def test_get_prop_not_found(mock_get_prop_func, instance):
    """
    Test get_prop method - when function to get property fails with Attribute error - meaning property does not exist
    method should return the default value attribute
    """
    with patch.object(
        MockProperties, "get_prop_mapping", wraps=mock_get_prop_func
    ) as mock_get_prop_mapping:
        res = instance.get_prop(MockProperties.PROP_2)
    mock_get_prop_mapping.assert_called_once_with(MockProperties.PROP_2)
    assert res == "Not Found"
