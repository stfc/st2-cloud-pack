import unittest
from unittest.mock import MagicMock, patch, NonCallableMock
from parameterized import parameterized

from openstack_query.managers.query_manager import QueryManager
from enums.query.query_output_types import QueryOutputTypes

from tests.lib.openstack_query.mocks.mocked_structs import (
    MOCKED_OUTPUT_DETAILS,
    MOCKED_PRESET_DETAILS,
)


class QueryManagerTests(unittest.TestCase):
    """
    Runs various tests to ensure that QueryManager class methods function expectedly
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()

        self.query = MagicMock()
        self.instance = QueryManager(cloud_account="test_account", query=self.query)

    @patch("openstack_query.managers.query_manager.QueryManager._populate_query")
    @patch("openstack_query.managers.query_manager.QueryManager._get_query_output")
    def test_build_and_run_query(self, mock_get_query_output, mock_populate_query):
        """
        Tests that _build_and_run_query method functions expectedly
        Sets up a QueryResource object and runs a given query with appropriate inputs. Returns query result
        """
        mock_query_return = NonCallableMock()
        mock_get_query_output.return_value = mock_query_return

        res = self.instance._build_and_run_query(
            MOCKED_PRESET_DETAILS, MOCKED_OUTPUT_DETAILS
        )
        mock_populate_query.assert_called_once_with(
            preset_details=MOCKED_PRESET_DETAILS,
            properties_to_select=MOCKED_OUTPUT_DETAILS.properties_to_select,
        )
        self.query.run.assert_called_once_with("test_account")
        mock_get_query_output.assert_called_once_with(MOCKED_OUTPUT_DETAILS.output_type)
        self.assertEqual(res, mock_query_return)

    @parameterized.expand(
        [(f"test {outtype.name.lower()}", outtype) for outtype in QueryOutputTypes]
    )
    def test_get_query_output_supports_all_types(self, name, outtype):
        """
        Tests that _get_query_output method works for all OutputType Enums
        """
        self.assertIsNotNone(self.instance._get_query_output(outtype))

    def test_populate_query_with_properties(self):
        """
        Tests that _populate_query method functions expectedly with properties
        method builds the query with appropriate inputs before executing - calls select() with given properties
        """

        self.instance._populate_query(
            MOCKED_PRESET_DETAILS, MOCKED_OUTPUT_DETAILS.properties_to_select
        )
        self.query.select.assert_called_once_with(
            *MOCKED_OUTPUT_DETAILS.properties_to_select
        )
        self.query.where.assert_called_once_with(
            preset=MOCKED_PRESET_DETAILS.preset,
            prop=MOCKED_PRESET_DETAILS.prop,
            **MOCKED_PRESET_DETAILS.args,
        )

    def test_populate_query_with_no_properties(self):
        """
        Tests that _populate_query method functions expectedly with no properties
        method builds the query with appropriate inputs before executing - calls select_all() when given no properties
        """

        self.instance._populate_query(MOCKED_PRESET_DETAILS, None)
        self.query.select_all.assert_called_once()
        self.query.where.assert_called_once_with(
            preset=MOCKED_PRESET_DETAILS.preset,
            prop=MOCKED_PRESET_DETAILS.prop,
            **MOCKED_PRESET_DETAILS.args,
        )
