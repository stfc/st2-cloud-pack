from enum import Enum
from abc import ABC, abstractmethod
from typing import Callable
from enums.query.query_presets import QueryPresets


class HandlerBase(ABC):
    @abstractmethod
    def _get_mapping(self, preset: QueryPresets, prop: Enum) -> Callable:
        """
        Method used to return a function mapped to a given preset - prop pair
        :param preset: An Enum which represents a preset
        :param prop: An Enum which represents a property for preset to act on
        """

    def _check_supported(self, preset: QueryPresets, prop: Enum) -> bool:
        """
        Method used to return if a preset and prop are supported by the handler
        :param preset: An Enum which represents a preset
        :param prop: An Enum which represents a property for preset to act on
        """
