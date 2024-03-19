from unittest.mock import MagicMock
import pytest
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


@pytest.fixture(scope="function", name="mock_results_container")
def results_container_fixture():
    """
    Returns a list of mock results with each as_object return value set to
    given values
    """

    def _setup_results_container(mock_as_objects):
        """
        function which sets up a list of mock Result objects each with
        a different as_object return value - as specified by mock_as_objects input
        :param mock_as_objects: a list of values that is to be assigned as the
         return_value for each mock Result object
        """
        mock_results = [MagicMock() for _ in mock_as_objects]
        for i, mock_result in enumerate(mock_results):
            mock_result.as_object.return_value = mock_as_objects[i]
        return mock_results

    return _setup_results_container


@pytest.fixture(scope="function", name="mock_get_prop_mapping")
def get_prop_mapping_fixture():
    """
    Returns a mocked get_prop_mapping function
    """

    def _mock_get_prop_mapping(mock_prop: MockProperties):
        """
        Stubs the get_prop_mapping method - it now takes a property enum and returns <prop_enum>.name.lower()
        :param mock_prop: property enum passed to get_prop_mapping
        """
        return MagicMock(wraps=lambda obj, prop=mock_prop: obj[prop.name.lower()])

    return _mock_get_prop_mapping
