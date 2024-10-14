import json
from unittest.mock import MagicMock, patch

import pytest

from icinga_api.query_objects import query_object
from structs.icinga.object_query import IcingaQuery


@patch("icinga_api.query_objects.requests.post")
@pytest.mark.parametrize("joins", [None, ["host.name", "host.state"]])
def test_query_object_success(mock_post, joins):
    """
    Tests query_object succeeds when providing joins and without joins
    """
    icinga_account = MagicMock()

    mock_icinga_query = IcingaQuery(
        object_type="Host",
        filter="host.team==team",
        filter_vars={"team": "cloud"},
        properties_to_select=["name", "address"],
        joins=joins,
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    query_object(icinga_account, mock_icinga_query)

    mock_post.assert_called_once()

    _, kwargs = mock_post.call_args
    payload = json.loads(kwargs["data"])

    expected_payload = {
        "type": "Host",
        "filter": "host.team==team",
        "filter_vars": {"team": "cloud"},
        "attrs": ["name", "address"],
        "joins": joins,
    }

    assert payload == expected_payload
