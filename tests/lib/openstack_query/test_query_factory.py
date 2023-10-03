from unittest.mock import MagicMock, patch
from openstack_query.query_factory import QueryFactory


@patch("openstack_query.query_factory.QueryBuilder")
@patch("openstack_query.query_factory.QueryOutput")
@patch("openstack_query.query_factory.QueryParser")
@patch("openstack_query.query_factory.QueryExecuter")
@patch("openstack_query.query_factory.QueryComponents")
def test_build_query_deps(
    mock_query_components,
    mock_executer,
    mock_parser,
    mock_output,
    mock_builder,
):
    """
    Test that function build_query_deps works
    should build all query blocks and return QueryComponent dataclass using them
    """
    mock_mapping_cls = MagicMock()
    res = QueryFactory.build_query_deps(mock_mapping_cls)

    mock_mapping_cls.get_prop_mapping.assert_called_once()
    mock_prop_mapping = mock_mapping_cls.get_prop_mapping.return_value

    mock_output.assert_called_once_with(mock_prop_mapping)
    mock_parser.assert_called_once_with(mock_prop_mapping)
    mock_builder.assert_called_once_with(
        prop_enum_cls=mock_prop_mapping,
        client_side_handlers=mock_mapping_cls.get_client_side_handlers.return_value.to_list.return_value,
        server_side_handler=mock_mapping_cls.get_server_side_handler.return_value,
    )
    mock_executer.assert_called_once_with(
        prop_enum_cls=mock_prop_mapping,
        runner_cls=mock_mapping_cls.get_runner_mapping.return_value,
    )

    mock_query_components.assert_called_once_with(
        mock_output.return_value,
        mock_parser.return_value,
        mock_builder.return_value,
        mock_executer.return_value,
    )
    assert res == mock_query_components.return_value
