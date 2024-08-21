import pytest

import openstack_query


@pytest.mark.parametrize(
    "test_module_name",
    [
        "ServerQuery",
        "UserQuery",
        "FlavorQuery",
        "ProjectQuery",
        "ImageQuery",
        "HypervisorQuery",
    ],
)
def test_query_server_import(test_module_name):
    """Tests that query object imports can be done at root level"""
    assert getattr(openstack_query, test_module_name)
