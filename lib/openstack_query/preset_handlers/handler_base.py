from enum import Enum
from abc import ABC, abstractmethod
from custom_types.openstack_query.aliases import MappingReturn


class HandlerBase(ABC):
    @abstractmethod
    def _get_mapping(self, key: Enum) -> MappingReturn:
        """
        Method used to return a function mapped to a given enum
        :param key: An Enum for which a mapping may exist for
        """
