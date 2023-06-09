from abc import ABC, abstractmethod


class QueryMappingTests(ABC):
    """
    An abstract base class setup test methods that each Query<Resource> class needs to implement
    to ensure that each corresponding property enum is matched to a preset
    """

    @abstractmethod
    def test_property_to_property_func_mapping(self, prop):
        """
        Should test that all openstack properties have a corresponding property function
        """
