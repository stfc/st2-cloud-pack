from abc import ABC, abstractmethod
from unittest.mock import MagicMock, NonCallableMock


from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_query_base import OpenstackQueryBase


class OpenstackQueryBaseTests(ABC):
    """
    Runs various tests to ensure OpenstackQueryBase works correctly

    self.instance should be assigned in tests that inherit from this during the setUp method
    """

    instance: OpenstackQueryBase

    @abstractmethod
    def test_property_funcs(self):
        """
        Tests calling get_query_property_funcs
        """

    def test_search(self):
        """
        Tests calling search
        """
        query_params = QueryParams(
            query_preset="all_method",
            properties_to_select=NonCallableMock(),
            group_by=NonCallableMock(),
            return_html=NonCallableMock(),
        )

        self.instance.search_all_method = MagicMock()

        self.instance.search(
            cloud_account="test",
            query_params=query_params,
            project_identifier="ProjectID",
            test_param="TestParam",
        )

        self.instance.search_all_method.assert_called_once_with(
            "test", project_identifier="ProjectID", test_param="TestParam"
        )
