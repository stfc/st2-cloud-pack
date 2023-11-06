from typing import Dict
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue
from enums.query.props.prop_enum import PropEnum


class Result:
    """Class that holds a single result item"""

    def __init__(self, prop_enum_cls, obj_result: OpenstackResourceObj):
        self._prop_enum_cls = prop_enum_cls
        self._obj_result = obj_result
        self._forwarded_props = {}

    def as_object(self) -> OpenstackResourceObj:
        return self._obj_result

    def as_props(self, *props: PropEnum) -> Dict[str, PropValue]:
        """
        return stored result, only outputting the properties given
        :props: A set of prop enums to select
        """
        selected_props = {}
        for prop in props:
            key = prop.name.lower()
            selected_props[key] = self.get_prop(prop)

        return {**selected_props, **self._forwarded_props}

    def get_prop(self, prop: PropEnum) -> PropValue:
        """
        return value of prop enum for stored result
        :prop: a prop enum to select
        """
        return self._prop_enum_cls.get_prop_mapping(prop)(self._obj_result)

    def update_forwarded_properties(self, forwarded_props: Dict[str, PropValue]):
        """
        updates the set of forwarded properties to be associated with query result
        :param forwarded_props: a dictionary containing property name: property value of
        props to be associated with this result forwarded from previous queries
        """
        self._forwarded_props.update(forwarded_props)
