import unittest
from unittest.mock import MagicMock, patch, NonCallableMock
from parameterized import parameterized

from nose.tools import raises
from openstack_query.managers.query_manager import QueryManager
from enums.query.query_output_types import QueryOutputTypes
from enums.query.query_presets import (
    QueryPresetsString,
    QueryPresetsGeneric,
    QueryPresetsDateTime,
)

from structs.query.query_preset_details import QueryPresetDetails

from lib.exceptions.parse_query_error import ParseQueryError
from tests.lib.openstack_query.mocks.mocked_structs import (
    MOCKED_OUTPUT_DETAILS,
    MOCKED_PRESET_DETAILS,
)

# pylint:disable=protected-access,


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
        self.prop_cls = MagicMock()
        self.instance = QueryManager(
            cloud_account="test_account", query=self.query, prop_cls=self.prop_cls
        )

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
    def test_get_query_output_supports_all_types(self, _, outtype):
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

    @patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
    @patch("openstack_query.managers.query_manager.QueryOutputDetails")
    def test_search_all(self, mock_query_output_details, mock_build_and_run_query):
        """
        Tests that search_all method functions expectedly
        Runs a query to get all generic resources, returns query results
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        mock_output_details = MagicMock()
        mock_query_output_details.from_kwargs.return_value = mock_output_details

        mock_kwargs = {
            "properties_to_select": ["generic_name", "generic_id"],
            "output_type": QueryOutputTypes.TO_STR,
        }

        res = self.instance.search_all(**mock_kwargs)
        mock_build_and_run_query.assert_called_once_with(
            preset_details=None, output_details=mock_output_details
        )

        self.assertEqual(res, mock_query_return)

    @patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
    @patch("openstack_query.managers.query_manager.QueryOutputDetails")
    def test_search_by_datetime(
        self, mock_query_output_details, mock_build_and_run_query
    ):
        """
        Tests that search_by_datetime method functions expectedly
        Run a datetime query - in this case get all older than generic resources a relative time
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        mock_output_details = MagicMock()
        mock_query_output_details.from_kwargs.return_value = mock_output_details

        mock_kwargs = {
            "properties_to_select": ["generic_name", "generic_id"],
            "output_type": QueryOutputTypes.TO_STR,
        }

        res = self.instance.search_by_datetime(
            search_mode="older_than",
            property_to_search_by="generic_creation_date",
            days=10,
            hours=10,
            minutes=1,
            **mock_kwargs,
        )

        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsDateTime.OLDER_THAN,
                prop=self.prop_cls.from_string.return_value,
                args={
                    "days": 10,
                    "hours": 10,
                    "minutes": 1,
                    "seconds": 0,
                },
            ),
            output_details=mock_output_details,
        )
        self.assertEqual(res, mock_query_return)

    @patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
    @patch("openstack_query.managers.query_manager.QueryOutputDetails")
    def test_search_by_property_with_single_value(
        self, mock_query_output_details, mock_build_and_run_query
    ):
        """
        Tests that search_by_property method functions expectedly - with single value list
        Runs a property query - in this case get servers with matching image_id
        Should build and run a query using EQUAL_TO preset
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        mock_output_details = MagicMock()
        mock_query_output_details.from_kwargs.return_value = mock_output_details

        mock_kwargs = {
            "properties_to_select": ["generic_name", "generic_id"],
            "output_type": QueryOutputTypes.TO_STR,
        }

        res = self.instance.search_by_property(
            search_mode="any_in",
            property_to_search_by="image_id",
            values=["image-id1"],
            **mock_kwargs,
        )

        # should call build with EQUAL_TO and args with keyword value instead
        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsGeneric.EQUAL_TO,
                prop=self.prop_cls.from_string.return_value,
                args={"value": "image-id1"},
            ),
            output_details=mock_output_details,
        )
        self.assertEqual(res, mock_query_return)

    @patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
    @patch("openstack_query.managers.query_manager.QueryOutputDetails")
    def test_search_by_property_with_multiple_values(
        self, mock_query_output_details, mock_build_and_run_query
    ):
        """
        Tests that search_by_property method functions expectedly - with single value list
        Runs a property query - in this case get servers with matching image_id
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        mock_output_details = MagicMock()
        mock_query_output_details.from_kwargs.return_value = mock_output_details

        mock_kwargs = {
            "properties_to_select": ["generic_name", "generic_id"],
            "output_type": QueryOutputTypes.TO_STR,
        }

        res = self.instance.search_by_property(
            search_mode="any_in",
            property_to_search_by="image_id",
            values=["image-id1", "image-id2"],
            **mock_kwargs,
        )

        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.ANY_IN,
                prop=self.prop_cls.from_string.return_value,
                args={"values": ["image-id1", "image-id2"]},
            ),
            output_details=mock_output_details,
        )
        self.assertEqual(res, mock_query_return)

    @patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
    @patch("openstack_query.managers.query_manager.QueryOutputDetails")
    @patch("openstack_query.managers.query_manager.re")
    def test_search_by_regex_valid(
        self, mock_re, mock_query_output_details, mock_build_and_run_query
    ):
        """
        Tests that search_by_regex method functions expectedly - with single regex pattern
        Runs a regex pattern query - in this case gets servers with matching pattern on name
        """
        mock_query_return = NonCallableMock()
        mock_build_and_run_query.return_value = mock_query_return

        mock_re_return = NonCallableMock()
        mock_re.compile.return_value = mock_re_return

        mock_output_details = MagicMock()
        mock_query_output_details.from_kwargs.return_value = mock_output_details

        mock_kwargs = {
            "properties_to_select": ["generic_name", "generic_id"],
            "output_type": QueryOutputTypes.TO_STR,
        }

        res = self.instance.search_by_regex(
            property_to_search_by="generic_name",
            pattern="some-regex-pattern",
            **mock_kwargs,
        )

        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.MATCHES_REGEX,
                prop=self.prop_cls.from_string.return_value,
                args={"regex_string": "some-regex-pattern"},
            ),
            output_details=mock_output_details,
        )

        self.assertEqual(res, mock_query_return)

    @raises(ParseQueryError)
    def test_search_datetime_raise_error(self):
        """
        Test that ParseQueryError is raised when someone tries to query
        using datetime
        """
        mock_kwargs = {
            "search_mode": "mock_mode",
            "property_to_search_by": "mock_prop",
            "date 1": "2023-08-01",
        }
        self.instance.search_by_datetime(**mock_kwargs)
