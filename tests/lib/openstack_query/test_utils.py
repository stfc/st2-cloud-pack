from parameterized import parameterized
from nose.tools import raises
import openstack_query.utils as utils


@parameterized([
    (lambda a, b, c: None, ['a','b','c']),
    (lambda a, b, c=1: None, ['a','b']),
    (lambda a, b, c=1: None, ['a','b','c']),
    (lambda: None, []),
    (lambda a=1: None, []),
    (lambda a=1: None, ['a']),
])
def test_check_filter_func_valid(func, args):
    assert utils.check_filter_func(func, args)


@parameterized([
    (lambda a, b, c: None, []),
    (lambda a, b, c: None, ['a', 'b']),
    (lambda a=1: None, ['a', 'b']),
    (lambda a, b, c=1: None, ['c']),
    (lambda: None, ['a']),
])
@raises(TypeError)
def test_check_filter_func_mapping_invalid(func, args):
    assert utils.check_filter_func(func, args)
