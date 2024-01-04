from enum import auto
from typing import Dict, Optional

from enums.query.props.prop_enum import PropEnum, PropFunc
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class AggregateProperties(PropEnum):
    """
    An enum class for Host Aggregate Properties
    """

    AGGREGATE_CREATED_AT = auto()
    AGGREGATE_DELETED = auto()
    AGGREGATE_DELETED_AT = auto()
    AGGREGATE_HOST_IPS = auto()
    AGGREGATE_HOSTTYPE = auto()
    AGGREGATE_UPDATED_AT = auto()
    AGGREGATE_ID = auto()

    @staticmethod
    def _get_aliases() -> Dict:
        """
        a method that returns all valid string alias mappings
        """
        return {
            AggregateProperties.AGGREGATE_CREATED_AT: ["created_at"],
            AggregateProperties.AGGREGATE_DELETED: ["deleted"],
            AggregateProperties.AGGREGATE_DELETED_AT: ["deleted_at"],
            AggregateProperties.AGGREGATE_HOST_IPS: ["hosts"],
            AggregateProperties.AGGREGATE_HOSTTYPE: ["metadata_hosttype", "hosttype"],
            AggregateProperties.AGGREGATE_UPDATED_AT: ["updated_at"],
            AggregateProperties.AGGREGATE_ID: ["id", "uuid"],
        }

    @staticmethod
    def get_prop_mapping(prop) -> Optional[PropFunc]:
        """
        Method that returns the property function if function mapping exists for a given AggregateProperty Enum
        how to get specified property from an openstacksdk Aggregate object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/aggregate.html
        :param prop: A Aggregate Enum for which a function may exist for
        """
        mapping = {
            AggregateProperties.AGGREGATE_CREATED_AT: lambda a: a["created_at"],
            AggregateProperties.AGGREGATE_DELETED: lambda a: a["deleted"],
            AggregateProperties.AGGREGATE_DELETED_AT: lambda a: a["deleted_at"],
            AggregateProperties.AGGREGATE_HOST_IPS: lambda a: a["hosts"],
            AggregateProperties.AGGREGATE_HOSTTYPE: lambda a: a["metadata"].get(
                "hosttype", None
            ),
            AggregateProperties.AGGREGATE_ID: lambda a: a["id"],
        }
        try:
            return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                f"Error: failed to get property mapping, property {prop.name} is not supported in AggregateProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return AggregateProperties.get_prop_mapping(AggregateProperties.AGGREGATE_ID)
