from inspect import getfullargspec
from typing import Callable, Any, List


def check_filter_func(func: Callable[[Any], bool], arg_names: List[str]) -> bool:
    func_spec = getfullargspec(func)
    func_all_args = func_spec.args
    defaults = func_spec.defaults

    # required arguments would be positional arguments at the start minus number of configured defaults if any
    func_required_args = func_all_args
    if defaults:
        func_required_args = func_all_args[0:-len(defaults)]

    # check that preset args contains required arguments
    for arg in func_required_args:
        if arg not in arg_names:
            raise TypeError(
                "missing argument '%s'" % arg
            )

    # check that all preset args will be accepted from
    for arg in arg_names:
        if arg not in func_all_args:
            raise TypeError(
                "unexpected argument '%s" % arg
            )
    return True
