from datetime import timedelta, datetime
from inspect import getfullargspec
import re

from typing import Any, Callable, List, Union, Pattern, Dict
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


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


def check_kwarg_mapping(
        kwarg_mapping: Callable[[Any], Dict[str, Any]],
        args: Dict[str, Any]
):
    try:
        _ = kwarg_mapping(**args)
    except KeyError as e:
        raise TypeError(f"expected arg '{e.args[0]}' but not found")

    return True


def prop_equal_to(prop: Any, value: Any) -> bool:
    if isinstance(prop, type(value)):
        if isinstance(prop, object) and hasattr(prop, '__eq__'):
            return prop.__eq__(value)
    else:
        return False
    return prop == value


def prop_not_equal_to(prop: Any, value: Any) -> bool:
    return not prop_equal_to(prop, value)


def prop_less_than(prop: Union[int, float], value: Union[int, float]) -> bool:
    return prop < value


def prop_greater_than(prop: Union[int, float], value: Union[int, float]) -> bool:
    return prop > value


def convert_to_timestamp(
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ"
):
    delta = get_timestamp_in_seconds(
        days, hours, minutes, seconds
    )
    return (datetime(1970, 1, 1) + timedelta(seconds=delta)).strftime(timestamp_fmt)


def get_current_time():
    return datetime.now()


def get_timestamp_in_seconds(
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0
):
    if all(arg == 0 for arg in [days, hours, minutes, seconds]):
        raise MissingMandatoryParamError("requires at least 1 argument for function to be non-zero")

    current_time = get_current_time().timestamp()
    prop_time_in_seconds = timedelta(
        days=days, hours=hours, minutes=minutes, seconds=seconds,
    ).total_seconds()

    return current_time - prop_time_in_seconds


def prop_older_than(
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ"
):
    prop_timestamp = datetime.strptime(prop, prop_timestamp_fmt).timestamp()
    given_timestamp = get_timestamp_in_seconds(days, hours, minutes, seconds)

    return prop_timestamp > given_timestamp


def prop_younger_than_or_equal_to(
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ"
):
    return not prop_older_than(
        prop,
        days,
        hours,
        minutes,
        seconds,
        prop_timestamp_fmt
    )


def prop_younger_than(
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0, seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ"
):
    prop_datetime = datetime.strptime(prop, prop_timestamp_fmt).timestamp()

    return prop_datetime < get_timestamp_in_seconds(
        days,
        hours,
        minutes,
        seconds,
    )


def prop_older_than_or_equal_to(
        prop: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
        prop_timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ"
):
    return not prop_younger_than(
        prop,
        days,
        hours,
        minutes,
        seconds,
        prop_timestamp_fmt
    )


def prop_matches_regex(prop: Any, regex_string: Pattern[str]) -> bool:
    return True if re.match(regex_string, prop) else False


def prop_any_in(prop: Any, values: str) -> bool:
    if len(values) == 0:
        raise MissingMandatoryParamError("values list must contain at least one item to match against")
    return any(prop == val for val in values)


def prop_not_any_in(prop: Any, values: str) -> bool:
    return not prop_any_in(prop, values)
