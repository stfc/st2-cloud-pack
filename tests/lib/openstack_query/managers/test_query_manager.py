import unittest
from unittest.mock import MagicMock, patch, NonCallableMock

import pytest
from parameterized import parameterized

from openstack_query.managers.query_manager import QueryManager
from enums.query.query_output_types import QueryOutputTypes
from enums.query.query_presets import (
    QueryPresetsString,
    QueryPresetsGeneric,
    QueryPresetsDateTime,
)

from structs.query.query_preset_details import QueryPresetDetails

from exceptions.enum_mapping_error import EnumMappingError


from tests.lib.openstack_query.mocks.mocked_structs import (
    MOCKED_OUTPUT_DETAILS,
    MOCKED_PRESET_DETAILS,
    MOCKED_OUTPUT_DETAILS_WITH_SORT_BY,
    MOCKED_OUTPUT_DETAILS_WITH_GROUP_BY,
    MOCKED_OUTPUT_DETAILS_WITH_ALL,
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

    def _run_build_and_run_query_case(
        self, output_details, preset_details, runner_params
    ):
        with patch(
            "openstack_query.managers.query_manager.QueryManager._populate_output_params"
        ) as mock_populate_output_params:
            with patch(
                "openstack_query.managers.query_manager.QueryManager._get_query_output"
            ) as mock_get_query_output:
                res = self.instance._build_and_run_query(
                    output_details=output_details,
                    preset_details=preset_details,
                    runner_params=runner_params,
                )
                mock_populate_output_params.assert_called_once_with(
                    output_details=output_details
                )
                mock_get_query_output.assert_called_once_with(
                    output_details.output_type
                )
                self.assertEqual(res, mock_get_query_output.return_value)

    def test_build_and_run_query_with_no_optional_params(self):
        """
        Tests that _build_and_run_query method functions expectedly - with no preset or runner params
        Should setup a QueryResource object and set output details, then call run() with no runner params
        """
        self._run_build_and_run_query_case(
            output_details=MOCKED_OUTPUT_DETAILS,
            preset_details=None,
            runner_params=None,
        )
        self.instance._query.where.assert_not_called()
        self.query.run.assert_called_once_with("test_account")

    def test_build_and_run_query_with_runner_params(self):
        """
        Tests that _build_and_run_query method functions expectedly - with runner params, no preset params
        Should setup a QueryResource object and set output details, then call run() with mock runner params
        """
        mock_runner_params = {"arg1": "val1", "arg2": "val2"}
        self._run_build_and_run_query_case(
            output_details=MOCKED_OUTPUT_DETAILS,
            preset_details=None,
            runner_params=mock_runner_params,
        )
        self.instance._query.where.assert_not_called()
        self.query.run.assert_called_once_with("test_account", **mock_runner_params)

    def test_build_and_run_query_with_preset_details(self):
        """
        Tests that _build_and_run_query method functions expectedly - with preset params
        Should setup a QueryResource object and set output details, then call where() with preset details,
        then finally call run() with no runner params
        """
        self._run_build_and_run_query_case(
            output_details=MOCKED_OUTPUT_DETAILS,
            preset_details=MOCKED_PRESET_DETAILS,
            runner_params=None,
        )
        self.query.where.assert_called_once_with(
            preset=MOCKED_PRESET_DETAILS.preset,
            prop=MOCKED_PRESET_DETAILS.prop,
            **MOCKED_PRESET_DETAILS.args,
        )

    @parameterized.expand(
        [(f"test {outtype.name.lower()}", outtype) for outtype in QueryOutputTypes]
    )
    def test_get_query_output_supports_all_types(self, _, outtype):
        """
        Tests that _get_query_output method works for all OutputType Enums
        """
        self.assertIsNotNone(self.instance._get_query_output(outtype))

    def test_get_query_output_raises_error(self):
        """
        Tests that query output type raises error when given an enum which does not have a mapping
        """
        with pytest.raises(EnumMappingError):
            self.instance._get_query_output(MagicMock())

    def _run_populate_output_params_check(self, mock_output_details):
        self.instance._populate_output_params(output_details=mock_output_details)
        self.query.select.assert_called_once_with(
            *mock_output_details.properties_to_select
        )

    def test_populate_output_params_with_all_provided(self):
        """
        Tests populate_output_params works properly - with group_by and sort_by in output_details
        Should call QueryMethods sort_by and group_by methods appropriately
        """
        mock_output_details = MOCKED_OUTPUT_DETAILS_WITH_ALL
        self._run_populate_output_params_check(mock_output_details)
        self.query.sort_by.assert_called_once_with(*mock_output_details.sort_by)
        self.query.group_by.assert_called_once_with(
            group_by=mock_output_details.group_by,
            group_ranges=mock_output_details.group_ranges,
            include_ungrouped_results=mock_output_details.include_ungrouped_results,
        )

    def test_populate_output_params_with_group_by(self):
        """
        Tests populate_output_params works properly - with group_by in output_details
        Should call QueryMethods group_by method appropriately
        """
        mock_output_details = MOCKED_OUTPUT_DETAILS_WITH_GROUP_BY
        self._run_populate_output_params_check(mock_output_details)
        self.query.sort_by.assert_not_called()
        self.query.group_by.assert_called_once_with(
            group_by=mock_output_details.group_by,
            group_ranges=mock_output_details.group_ranges,
            include_ungrouped_results=mock_output_details.include_ungrouped_results,
        )

    def test_populate_output_params_with_sort_by(self):
        """
        Tests populate_output_params works properly - with sort_by in output_details
        Should call QueryMethods sort_by method appropriately
        """
        mock_output_details = MOCKED_OUTPUT_DETAILS_WITH_SORT_BY
        self._run_populate_output_params_check(mock_output_details)
        self.query.sort_by.assert_called_once_with(*mock_output_details.sort_by)
        self.query.group_by.assert_not_called()

    def test_populate_output_params_with_neither(self):
        """
        Tests populate_output_params works properly - with neither group_by or sort_by in output_details
        Should do nothing
        """
        mock_output_details = MOCKED_OUTPUT_DETAILS
        self._run_populate_output_params_check(mock_output_details)
        self.query.sort_by.assert_not_called()
        self.query.group_by.assert_not_called()

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
            "meta_kwarg1": "val1",
            "meta_kwarg2": "val2",
        }

        res = self.instance.search_all(
            properties_to_select=["generic_name", "generic_id"],
            output_type=QueryOutputTypes.TO_STR,
            **mock_kwargs,
        )
        mock_build_and_run_query.assert_called_once_with(
            preset_details=None,
            output_details=mock_output_details,
            runner_params=mock_kwargs,
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
            "meta_kwarg1": "val1",
            "meta_kwarg2": "val2",
        }

        res = self.instance.search_by_datetime(
            search_mode="older_than",
            property_to_search_by="generic_creation_date",
            days=10,
            hours=10,
            minutes=1,
            properties_to_select=["generic_name", "generic_id"],
            output_type=QueryOutputTypes.TO_STR,
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
            runner_params=mock_kwargs,
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
            "meta_kwarg1": "val1",
            "meta_kwarg2": "val2",
        }

        res = self.instance.search_by_property(
            search_mode="any_in",
            property_to_search_by="image_id",
            values=["image-id1"],
            properties_to_select=["generic_name", "generic_id"],
            output_type=QueryOutputTypes.TO_STR,
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
            runner_params=mock_kwargs,
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
            "meta_kwarg1": "val1",
            "meta_kwarg2": "val2",
        }

        res = self.instance.search_by_property(
            search_mode="any_in",
            property_to_search_by="image_id",
            values=["image-id1", "image-id2"],
            properties_to_select=["generic_name", "generic_id"],
            output_type=QueryOutputTypes.TO_STR,
            **mock_kwargs,
        )

        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.ANY_IN,
                prop=self.prop_cls.from_string.return_value,
                args={"values": ["image-id1", "image-id2"]},
            ),
            output_details=mock_output_details,
            runner_params=mock_kwargs,
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
            "meta_kwarg1": "val1",
            "meta_kwarg2": "val2",
        }

        res = self.instance.search_by_regex(
            property_to_search_by="generic_name",
            pattern="some-regex-pattern",
            properties_to_select=["generic_name", "generic_id"],
            output_type=QueryOutputTypes.TO_STR,
            **mock_kwargs,
        )

        mock_build_and_run_query.assert_called_once_with(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.MATCHES_REGEX,
                prop=self.prop_cls.from_string.return_value,
                args={"regex_string": "some-regex-pattern"},
            ),
            output_details=mock_output_details,
            runner_params=mock_kwargs,
        )

        self.assertEqual(res, mock_query_return)
