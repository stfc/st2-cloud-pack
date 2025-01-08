from unittest.mock import patch, NonCallableMock, MagicMock
import pytest

from workflows.search_by_property import search_by_property


@patch("workflows.search_by_property.openstackquery")
@pytest.mark.parametrize(
    "output_type", ["to_html", "to_string", "to_objects", "to_props"]
)
def test_search_by_property_minimal(mock_openstackquery, output_type):
    """
    Runs search_by_property only providing required values
    """

    mock_query = MagicMock()
    mock_cloud_account = NonCallableMock()

    mock_openstackquery.MockQuery.return_value = mock_query
    params = {
        "cloud_account": mock_cloud_account,
        "query_type": "MockQuery",
        "search_mode": NonCallableMock(),
        "property_to_search_by": NonCallableMock(),
        "output_type": output_type,
        "values": ["val1", "val2"],
    }
    res = search_by_property(**params)

    mock_query.select_all.assert_called_once()
    mock_query.where.assert_called_once_with(
        preset=params["search_mode"],
        prop=params["property_to_search_by"],
        values=params["values"],
    )
    mock_query.run.assert_called_once_with(mock_cloud_account)

    assert (
        res
        == {
            "to_html": mock_query.to_html.return_value,
            "to_string": mock_query.to_string.return_value,
            "to_objects": mock_query.to_objects.return_value,
            "to_props": mock_query.to_props.return_value,
        }[output_type]
    )


def test_search_by_property_errors_when_no_values_given():
    """
    test that search_by_property errors when not provided a value to match against
    """
    with pytest.raises(RuntimeError):
        search_by_property(
            cloud_account=NonCallableMock(),
            query_type=NonCallableMock(),
            search_mode=NonCallableMock(),
            property_to_search_by=NonCallableMock(),
            output_type=NonCallableMock(),
            values=[],
        )


@patch("workflows.search_by_property.to_webhook")
@patch("workflows.search_by_property.openstackquery")
@pytest.mark.parametrize(
    "output_type", ["to_html", "to_string", "to_objects", "to_props"]
)
def test_search_by_property_all(mock_openstackquery, mock_to_webhook, output_type):
    """
    Runs search_by_property providing all values
    """

    mock_query = MagicMock()
    mock_cloud_account = NonCallableMock()

    mock_openstackquery.MockQuery.return_value = mock_query
    params = {
        "cloud_account": mock_cloud_account,
        "query_type": "MockQuery",
        "search_mode": NonCallableMock(),
        "property_to_search_by": NonCallableMock(),
        "output_type": output_type,
        "properties_to_select": ["prop1", "prop2"],
        "values": ["val1", "val2"],
        "group_by": NonCallableMock(),
        "sort_by": ["prop1", "prop2"],
        "webhook": "test",
        "arg1": "val1",
        "arg2": "val2",
    }
    res = search_by_property(**params)

    mock_query.select.assert_called_once_with(*params["properties_to_select"])
    mock_query.where.assert_called_once_with(
        preset=params["search_mode"],
        prop=params["property_to_search_by"],
        values=params["values"],
    )
    mock_query.sort_by.assert_called_once_with(
        *[(p, "desc") for p in params["sort_by"]]
    )
    mock_query.group_by.assert_called_once_with(params["group_by"])
    mock_query.run.assert_called_once_with(
        params["cloud_account"], arg1="val1", arg2="val2"
    )
    mock_to_webhook.assert_called_once_with(
        webhook="test", payload=mock_query.select_all().to_props.return_value
    )

    assert (
        res
        == {
            "to_html": mock_query.to_html.return_value,
            "to_string": mock_query.to_string.return_value,
            "to_objects": mock_query.to_objects.return_value,
            "to_props": mock_query.to_props.return_value,
        }[output_type]
    )


@patch("workflows.search_by_property.to_webhook")
@patch("workflows.search_by_property.openstackquery")
def test_search_by_property_migrate_webhook(mock_openstackquery, mock_to_webhook):
    """
    Tests search_by_property with webhook as migrate-server adds params to the query needed for the migrate action
    """

    mock_query = MagicMock()
    mock_cloud_account = NonCallableMock()
    mock_output_type = "to_string"
    mock_openstackquery.MockQuery.return_value = mock_query
    params = {
        "cloud_account": mock_cloud_account,
        "query_type": "MockQuery",
        "search_mode": NonCallableMock(),
        "property_to_search_by": NonCallableMock(),
        "output_type": mock_output_type,
        "properties_to_select": ["prop1", "prop2"],
        "values": ["val1", "val2"],
        "group_by": NonCallableMock(),
        "sort_by": ["prop1", "prop2"],
        "webhook": "migrate-server",
        "arg1": "val1",
        "arg2": "val2",
    }
    search_by_property(**params)

    mock_query.select.assert_called_once_with(*params["properties_to_select"])
    mock_to_webhook.assert_called_once_with(
        webhook="migrate-server", payload=mock_query.select_all().to_props.return_value
    )
