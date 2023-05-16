import unittest


class OpenstackQueryWrapperTests(unittest.TestCase):
    """
    Runs various tests to ensure that OpenstackQueryWrapper functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        raise NotImplementedError

    def test_select(self):
        """
        Tests that select function accepts all valid property Enums and sets attribute appropriately
        """
        raise NotImplementedError

    def test_select_all(self):
        """
        Tests that select_all function sets attribute to use all valid properties
        """
        raise NotImplementedError

    def test_where_valid_args(self):
        """
        Tests that where function accepts valid enum and args
        """
        raise NotImplementedError

    def test_where_invalid_args(self):
        """
        Tests that where function rejects invalid args appropriately
        """
        raise NotImplementedError

    def test_run_valid(self):
        """
        Tests that run function sets up query and calls _run_query appropriately
        """
        raise NotImplementedError

    def test_run_incomplete_conf(self):
        """
        Tests that run function catches when config is incomplete
        """
        raise NotImplementedError

    def test_group_by(self):
        """
        Tests that group groups results into list of lists appropriately
        """
        raise NotImplementedError

    def test_sort_by(self):
        """
        Tests that sort_by function sorts results list appropriately
        """
        raise NotImplementedError
