from typing import Any, Optional, Set
from custom_types.openstack_query.aliases import (
    PropertyMappings,
    PropFunc,
    OpenstackResourceObj,
)
from enums.query.props.prop_enum import PropEnum


class PropHandler:
    """
    This class stores a dictionary which maps a prop Enum to a function that, when given a valid openstack resource
    object, will return a value for that object which corresponds to the prop Enum. This dictionary is
    called PROPERTY_MAPPINGS
    """

    def __init__(self, property_mappings: PropertyMappings):
        self._PROPERTY_MAPPINGS = property_mappings

    def check_supported(self, prop: PropEnum) -> bool:
        """
        Method that returns True if function mapping exists for a given property Enum
        :param prop: A property Enum for which a function may exist for
        """
        return prop in self._PROPERTY_MAPPINGS.keys()

    def get_prop_func(self, prop: PropEnum) -> Optional[PropFunc]:
        """
        Method that returns the property function if function mapping exists for a given property Enum
        :param prop: A property Enum for which a function may exist for
        """
        return self._PROPERTY_MAPPINGS.get(prop, None)

    def all_props(self) -> Set[PropEnum]:
        """
        Method that returns all valid property Enums that this handler supports
        """
        return set(self._PROPERTY_MAPPINGS.keys())

    def get_prop(
        self, item: OpenstackResourceObj, prop: PropEnum, default_out: str = "Not Found"
    ) -> str:
        """
        Method that returns property value for a given openstack object which corresponds to a prop Enum.
        If the prop doesn't exist for the given openstack object, then the default value will be returned
        :param item: An openstack resource object
        :param prop: A prop Enum which represents the property we want to get
        :param default_out: A default value to return if property does not exist for given openstack resource object
        """
        if not self.check_supported(prop):
            return default_out

        prop_func = self.get_prop_func(prop)
        try:
            return str(prop_func(item))
        except AttributeError:
            return default_out
