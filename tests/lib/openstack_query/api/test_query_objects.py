from unittest.mock import patch, MagicMock
from openstack_query.api.query_objects import UserQuery, ServerQuery, get_common


@patch("openstack_query.api.query_objects.QueryFactory")
@patch("openstack_query.api.query_objects.QueryAPI")
def test_get_common(mock_query_api, mock_query_factory):
    mock_query_mapping = MagicMock()
    res = get_common(mock_query_mapping)
    mock_query_factory.build_query_deps.assert_called_once_with(mock_query_mapping)
    mock_query_api.assert_called_once_with(
        mock_query_factory.build_query_deps.return_value
    )
    assert res == mock_query_api.return_value


@patch("openstack_query.api.query_objects.get_common")
@patch("openstack_query.api.query_objects.ServerMapping")
def test_server_query(mock_server_mapping, mock_get_common):
    res = ServerQuery()
    mock_get_common.assert_called_once_with(mock_server_mapping)
    assert res == mock_get_common.return_value


@patch("openstack_query.api.query_objects.get_common")
@patch("openstack_query.api.query_objects.UserMapping")
def test_user_query(mock_user_mapping, mock_get_common):
    res = UserQuery()
    mock_get_common.assert_called_once_with(mock_user_mapping)
    assert res == mock_get_common.return_value
