import unittest
from unittest.mock import MagicMock, patch, NonCallableMock

from openstack_query.managers.server_manager import ServerManager

from enums.query.query_presets import (
    QueryPresetsDateTime,
    QueryPresetsString,
    QueryPresetsGeneric,
)
from enums.query.props.server_properties import ServerProperties
from enums.query.query_output_types import QueryOutputTypes
from structs.query.query_preset_details import QueryPresetDetails


@patch("openstack_query.managers.query_manager.QueryManager._build_and_run_query")
@patch("openstack_query.managers.server_manager.QueryOutputDetails")
class ServerManagerTests(unittest.TestCase):
    """
    Runs various tests to ensure that ServerManager class methods function expectedly
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()

        self.query = MagicMock()
        self.instance = ServerManager(cloud_account="test_account")

        # pylint:disable=protected-access
        self.instance._query = self.query

        # to add future tests
