import inspect
from typing import Any, Dict, Optional
from enum import Enum

from openstack_query.handlers.handler_base import HandlerBase
from custom_types.openstack_query.aliases import (
    FilterFunc,
    PresetToValidPropsMap,
    ParsedFilterFunc,
    PropFunc,
    PresetKwargs,
)

from enums.query.query_presets import QueryPresets
from exceptions.query_preset_mapping_error import QueryPresetMappingError


class PresetHandlerBase(HandlerBase):
    def __init__(self, filter_func_mappings: PresetToValidPropsMap):
        self._FILTER_FUNCTION_MAPPINGS = filter_func_mappings

    def check_supported(self, preset: QueryPresets, prop: Enum):
        if preset not in self._FILTER_FUNCTIONS.keys():
            return False

        props_valid_for_preset = self._FILTER_FUNCTION_MAPPINGS.get(preset, None)
        if props_valid_for_preset:
            if prop in props_valid_for_preset:
                return True

            # '*' represents that all props are valid for preset
            elif ["*"] == self._FILTER_FUNCTION_MAPPINGS[preset]:
                return True
        return False

    def _get_mapping(self, preset: QueryPresets, prop: Enum) -> Optional[FilterFunc]:
        """
        Method that returns whether a filter function mapping exists in this handler
        :param preset: A QueryPreset Enum for which a filter function mapping may exist for
        :param prop: A property Enum for which a filter function mapping may exist for
        """
        if self.check_supported(preset, prop):
            return self._FILTER_FUNCTIONS.get(preset, None)
        return None

    def get_filter_func(
        self,
        preset: QueryPresets,
        prop: Enum,
        prop_func: PropFunc,
        filter_func_kwargs: Optional[PresetKwargs] = None,
    ) -> Optional[ParsedFilterFunc]:
        """
        Method that checks and returns a parsed filter function (if a mapping exists in this handler).
        the parsed filter function will take as input a single openstack resource and return
        True if resources passes check, False if not.

        :param preset: A QueryPreset Enum for which a filter function mapping may exist for
        :param prop: A property Enum for which a filter function mapping may exist for
        :param prop_func: A function to get a property of an openstack resource when given it as input
        :param filter_func_kwargs: A dictionary of keyword: argument pairs to pass into filter function
        """

        filter_func = self._get_mapping(preset, prop)
        if not filter_func:
            raise QueryPresetMappingError(
                "Preset Not Found: failed to find filter_function mapping for preset "
                f"'{preset.name}' and property '{prop.name}'"
                "does the preset work with property specified?"
            )

        try:
            _ = self._check_filter_func(filter_func, filter_func_kwargs)
        except TypeError as err:
            raise QueryPresetMappingError(
                f"Preset Argument Error: failed to build filter_function for preset '{preset.name}'"
            ) from err

        return lambda a: self._filter_func_wrapper(
            a, filter_func, prop_func, filter_func_kwargs
        )

    @staticmethod
    def _filter_func_wrapper(
        item: Any,
        filter_func: FilterFunc,
        prop_func: PropFunc,
        filter_func_kwargs: Optional[PresetKwargs] = None,
    ):
        """
        Method that acts as a wrapper to the filter function, if the property cannot be found for the resource
        we return False before calling the filter function - since there's no property to compare.
        :param item: An openstack resource item
        :param filter_func: A filter function to run if property given can be retrieved from openstack resource
        :param **filter_func_kwargs: A dictionary of keyword args to pass to filter function
        """
        try:
            item_prop = prop_func(item)
        except AttributeError:
            return False
        if filter_func_kwargs:
            return filter_func(item_prop, **filter_func_kwargs)
        return filter_func(item_prop)

    @staticmethod
    def _check_filter_func(
        func: FilterFunc, func_kwargs: Optional[PresetKwargs] = None
    ) -> bool:
        """
        Method that checks a given function can accept a set of kwargs as arguments.
        :param func: function to test
        :param func_kwargs: kwargs to test
        """

        signature = inspect.signature(func)

        # skip first parameter for filter function as it is a positional arg which takes the output
        # of a property function and use that to compare against
        parameters = list(signature.parameters.values())[1:]

        has_varargs = any(param.kind == param.VAR_POSITIONAL for param in parameters)
        has_varkwargs = any(param.kind == param.VAR_KEYWORD for param in parameters)

        for param in parameters:
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                param_name = param.name
                if param_name in func_kwargs:
                    kwargs_value = func_kwargs[param_name]
                    param_type = param.annotation
                    if not isinstance(kwargs_value, param_type):
                        return False
                elif param.default is inspect.Parameter.empty:
                    return False

        if not has_varargs and not has_varkwargs:
            # Check for extra items in kwargs not present in the function signature
            if set(func_kwargs.keys()) - set(p.name for p in parameters):
                return False

        return True
