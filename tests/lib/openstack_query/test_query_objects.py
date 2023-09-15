from openstack_query.api.query_objects import export_query_types


def test_query_objects_get_dynamic():
    cls = export_query_types()[0]
    cls()
