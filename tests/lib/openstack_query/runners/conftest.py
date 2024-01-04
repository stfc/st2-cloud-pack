from unittest.mock import MagicMock
import pytest


@pytest.fixture(scope="function", name="mock_marker_prop_func")
def mock_marker_prop_func_fixture():
    return MagicMock()
