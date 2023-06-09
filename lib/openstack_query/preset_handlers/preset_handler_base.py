import inspect
from typing import Dict, Callable, Any, Optional

from openstack_query.preset_handlers.handler_base import HandlerBase
from custom_types.openstack_query.aliases import (
    FilterFunc,
    MappingReturn,
    MappingFunc,
    PresetKwargs,
)

from enums.query.query_presets import QueryPresets
from exceptions.query_preset_mapping_error import QueryPresetMappingError


class PresetHandlerBase(HandlerBase):
    def check_preset_supported(self, preset: QueryPresets):
        return preset in self._FILTER_FUNCTIONS.keys()

    def _get_mapping(self, preset: QueryPresets) -> MappingReturn:
        """
        Method that returns whether a property can be used as input for a query
        """
        return self._FILTER_FUNCTIONS.get(preset, None)

    def override_mapping_if_exists(
        self, preset: QueryPresets, override_func_mapping: MappingFunc
    ) -> MappingReturn:
        if self._get_mapping(preset):
            self._FILTER_FUNCTIONS[preset] = override_func_mapping
            return override_func_mapping
        return None

    def get_filter_func(
        self,
        preset: QueryPresets,
        prop_func: Callable[[Any], Any],
        preset_kwargs: PresetKwargs,
    ) -> Optional[FilterFunc]:
        """
        Method that builds and returns a filter function with a given preset, property function and args (if a mapping exists).
        :param preset: A QueryPreset Enum for which a filter function mapping may exist for
        :param prop_func: A function to get a property from a
        :param preset_kwargs: A dictionary of keyword: argument pairs to pass into function
        """

        filter_func = self._get_mapping(preset)
        if not filter_func:
            return None

        try:
            _ = self._check_filter_func(preset, preset_kwargs)
        except TypeError as err:
            raise QueryPresetMappingError(
                f"Preset Argument Error: failed to build filter_function for preset '{preset.name}'"
            ) from err

        return lambda a: filter_func(prop_func(a), **preset_kwargs)

    @staticmethod
    def _check_filter_func(
        func: Callable[[Any], bool], func_kwargs: Dict[str, Any]
    ) -> bool:
        """
        Method that checks a given function can accept a set of kwargs as arguments.
        :param func: function to test
        :param func_kwargs: kwargs to test
        """

        signature = inspect.signature(func)
        all_params = signature.parameters.values()

        # skip first parameter for filter function as it is a positional arg which takes the output
        # of a property function and uses that to compare against
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
