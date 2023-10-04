import pytest

from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from enums.query.query_presets import QueryPresetsGeneric
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


@pytest.fixture(name="test_corpus")
def corpus_fixture():
    """
    Returns a set of arguments to test against
    """
    return [1, "foo", None, {"a": "b"}]


@pytest.fixture(name="instance")
def instance_fixture():
    """
    Returns an instance with a mocked filter function mappings
    """

    # sets filter function mappings so that PROP_1 is valid for all client_side
    _filter_function_mappings = {
        preset: [MockProperties.PROP_1] for preset in QueryPresetsGeneric
    }
    return ClientSideHandlerGeneric(_filter_function_mappings)


def test_check_supported_all_presets(instance):
    """
    Tests that client_side_handler_generic supports all generic QueryPresets
    """
    assert (
        instance.check_supported(preset, MockProperties.PROP_1)
        for preset in QueryPresetsGeneric
    )


def test_prop_equal_to_valid(instance, test_corpus):
    """
    Tests that method prop_equal_to functions expectedly
    """
    for i in test_corpus:
        assert instance._prop_equal_to(i, i)


def test_prop_equal_to_invalid(instance, test_corpus):
    """
    Tests that method prop_equal_to functions expectedly
    """
    for i in test_corpus:
        assert not instance._prop_equal_to(i, "not equal")


def test_prop_not_equal_to_valid(instance, test_corpus):
    """
    Tests that method not_prop_equal_to functions expectedly
    """
    for i in test_corpus:
        assert instance._prop_not_equal_to(i, "FOO")


def test_prop_not_equal_to_invalid(instance, test_corpus):
    """
    Tests that method not_prop_equal_to functions expectedly
    """
    for i in test_corpus:
        assert not instance._prop_not_equal_to(i, i)


def test_prop_any_in_when_there(instance):
    """
    Tests that method prop_any_in functions expectedly
    Returns True if test_prop matches any values in a given list val_list
    """
    test_prop = "val3"
    val_list = ["val1", "val2", "val3"]
    assert instance._prop_any_in(test_prop, val_list)


def test_prop_any_in_when_not_there(instance):
    """
    Tests that method prop_any_in functions expectedly
    Returns True if test_prop matches any values in a given list val_list
    """
    test_prop = "val3"
    val_list = ["val1", "val2"]
    assert not instance._prop_any_in(test_prop, val_list)


def test_prop_any_in_empty_list(instance):
    """
    Tests that method prop_any_in functions expectedly - when given empty list raise error
    """
    with pytest.raises(MissingMandatoryParamError):
        instance._prop_any_in("some-prop-val", [])


def test_prop_not_any_in_when_there(instance):
    """
    Tests that method prop_any_not_in functions expectedly
    Returns True if test_prop does not match any values in a given list val_list
    """
    val_list = ["val1", "val2", "val3"]
    test_prop = "val3"
    assert not instance._prop_not_any_in(test_prop, val_list)


def test_prop_not_any_in_when_not_there(instance):
    """
    Tests that method prop_any_not_in functions expectedly
    Returns True if test_prop does not match any values in a given list val_list
    """
    val_list = ["val1", "val2"]
    test_prop = "val3"
    assert instance._prop_not_any_in(test_prop, val_list)
