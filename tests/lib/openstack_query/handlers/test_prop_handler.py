import unittest
from unittest.mock import MagicMock, NonCallableMock, patch

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
        """
        Tests that check_supported method works expectedly
        returns True if Prop Enum internal Property Mappings Dict
        """
        self.assertTrue(self.instance.check_supported(MockProperties.PROP_1))

    def test_check_supported_false(self):
        """
        Tests that check_supported method works expectedly
        returns False if Prop Enum not in internal Property Mappings Dict
        """
        self.assertFalse(self.instance.check_supported(MockProperties.PROP_3))

    def test_get_prop_func(self):
        """
        Tests that get_prop_func method works expectedly
        Returns corresponding Prop Func for supported Prop Enum
        """
        self.assertEqual(
            self.instance.get_prop_func(MockProperties.PROP_1), "prop1-func"
        )

    def test_get_prop_func_invalid(self):
        """
        Tests that get_prop_func method works expectedly
        Returns None for unsupported Prop Enum
        """
        self.assertIsNone(self.instance.get_prop_func(MockProperties.PROP_3))

    def test_all_props(self):
        """
        Tests that method all_props works expectedly
        Returns all Prop Enums with internal Property Mappings
        """
        self.assertEqual(
            self.instance.all_props(), {MockProperties.PROP_1, MockProperties.PROP_2}
        )

    @patch("openstack_query.handlers.prop_handler.PropHandler.get_prop_func")
    def test_get_prop_valid(self, mock_get_prop_func):
        """
        Tests that method get_prop works expectedly - with valid Prop Enum and Openstack Resource
        Returns output of prop_func
        """
        mock_openstack_resource = NonCallableMock()
        mock_prop_func = MagicMock()

        mock_get_prop_func.return_value = mock_prop_func
        mock_prop_func.return_value = "prop-val"

        res = self.instance.get_prop(mock_openstack_resource, MockProperties.PROP_1)
        mock_prop_func.assert_called_once_with(mock_openstack_resource)
        self.assertEqual(res, "prop-val")

    @patch("openstack_query.handlers.prop_handler.PropHandler.get_prop_func")
    def test_get_prop_use_default(self, mock_get_prop_func):
        """
        Tests that method get_prop works expectedly
        Returns default value when prop_func returns Attribute error
        """
        item = NonCallableMock()
        default_out = "some-default"
        mock_prop_func = MagicMock()

        mock_get_prop_func.return_value = mock_prop_func
        mock_prop_func.side_effect = AttributeError()

        res = self.instance.get_prop(item, MockProperties.PROP_1, default_out)
        mock_prop_func.assert_called_once_with(item)
        self.assertEqual(res, "some-default")

    def test_get_prop_invalid(self):
        """
        Tests that method get_prop works expectedly
        Returns default value when prop given that is not supported by handler
        """
        item = "some-openstack-resource"
        default_out = "some-default"

        res = self.instance.get_prop(item, MockProperties.PROP_3, default_out)
        self.assertEqual(res, "some-default")
