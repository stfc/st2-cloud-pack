import unittest
from unittest.mock import MagicMock, patch

from openstack_query.handlers.prop_handler import PropHandler
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


class PropHandlerTests(unittest.TestCase):
    """
    Runs various tests to ensure that PropHandler class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()

        _PROPERTY_MAPPINGS = {
            MockProperties.PROP_1: "prop1-func",
            MockProperties.PROP_2: "prop2-func",
        }
        self.instance = PropHandler(_PROPERTY_MAPPINGS)

    def test_check_supported_true(self):
        self.assertTrue(self.instance.check_supported(MockProperties.PROP_1))

    def test_check_supported_false(self):
        self.assertFalse(self.instance.check_supported(MockProperties.PROP_3))

    def test_get_mapping_valid(self):
        self.assertEqual(
            self.instance._get_mapping(MockProperties.PROP_1), "prop1-func"
        )

    def test_get_mapping_invalid(self):
        self.assertIsNone(self.instance._get_mapping(MockProperties.PROP_3))

    def test_all_props(self):
        self.assertEqual(
            self.instance.all_props(), {MockProperties.PROP_1, MockProperties.PROP_2}
        )

    @patch("openstack_query.handlers.prop_handler.PropHandler._get_mapping")
    def test_get_prop_valid(self, mock_get_mapping):
        item = "some-openstack-resource"
        mock_prop_func = MagicMock()

        mock_get_mapping.return_value = mock_prop_func
        mock_prop_func.return_value = "prop-val"

        res = self.instance.get_prop(item, MockProperties.PROP_1)
        mock_prop_func.assert_called_once_with("some-openstack-resource")
        self.assertEqual(res, "prop-val")

    @patch("openstack_query.handlers.prop_handler.PropHandler._get_mapping")
    def test_get_prop_use_default(self, mock_get_mapping):
        item = "some-openstack-resource"
        default_out = "some-default"
        mock_prop_func = MagicMock()

        mock_get_mapping.return_value = mock_prop_func
        mock_prop_func.side_effect = AttributeError()

        res = self.instance.get_prop(item, MockProperties.PROP_1, default_out)
        mock_prop_func.assert_called_once_with("some-openstack-resource")
        self.assertEqual(res, "some-default")

    def test_get_prop_invalid(self):
        item = "some-openstack-resource"
        default_out = "some-default"

        res = self.instance.get_prop(item, MockProperties.PROP_3, default_out)
        self.assertEqual(res, "some-default")
