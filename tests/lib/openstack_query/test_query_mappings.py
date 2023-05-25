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

    @abstractmethod
    def test_preset_to_filter_func_mapping(self, preset):
        """
        Should test that all query presets have a corresponding filter function mapping
        """