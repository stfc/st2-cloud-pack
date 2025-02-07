from unittest.mock import MagicMock, patch
from datetime import datetime
import json
import pytest
import requests

from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
from structs.alertmanager.silence_details import SilenceDetails
from alertmanager_api.silence import (
    schedule_silence,
    remove_silence,
    remove_silences,
    get_silences,
    get_active_silences,
    get_valid_silences,
    get_hv_silences,
)


@pytest.fixture(name="mock_get_silence_out")
def mock_get_silence_out_fixture():
    return json.dumps(
        [
            # An active silence for hv123
            {
                "id": "foo",
                "status": {"state": "active"},
                "updatedAt": "2025-01-16T07:31:31.257Z",
                "comment": "Testing.",
                "createdBy": "admin",
                "endsAt": "2025-01-16T10:51:00.000Z",
                "matchers": [
                    {"isEqual": True, "isRegex": False, "name": "env", "value": "prod"},
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "alertname",
                        "value": "InstanceDown",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "instance",
                        "value": "hv123.matrix.net",
                    },
                ],
                "startsAt": "2025-01-16T10:50:00.781Z",
            },
            # an expired silence for hv123 - with matcher "name=hostname"
            {
                "id": "boz",
                "status": {"state": "expired"},
                "updatedAt": "2025-01-02T10:00:00.002Z",
                "comment": "old",
                "createdBy": "admin2",
                "endsAt": "2025-01-02T10:00:00.002Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "other",
                        "value": "foo",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "alertname",
                        "value": "OpenStackServiceDown",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "hostname",
                        "value": "hv123.matrix.net",
                    },
                ],
                "startsAt": "2025-01-01T10:00:00.002Z",
            },
            # an expired silence for hv123
            {
                "id": "baz",
                "status": {"state": "expired"},
                "updatedAt": "2025-01-02T10:00:00.002Z",
                "comment": "old",
                "createdBy": "admin2",
                "endsAt": "2025-01-02T10:00:00.002Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "other",
                        "value": "foo",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "alertname",
                        "value": "PrometheusTargetMissing",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "instance",
                        "value": "hv123.matrix.net",
                    },
                ],
                "startsAt": "2025-01-01T10:00:00.002Z",
            },
            # an active silence for hv123 but wrong alertname
            {
                "id": "bil",
                "status": {"state": "active"},
                "updatedAt": "2025-01-02T10:00:00.002Z",
                "comment": "old",
                "createdBy": "admin2",
                "endsAt": "2025-01-02T10:00:00.002Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "other",
                        "value": "foo",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "alertname",
                        "value": "anotheralert",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "instance",
                        "value": "hv123.matrix.net",
                    },
                ],
                "startsAt": "2025-01-01T10:00:00.002Z",
            },
            # an active silence for hv123 but InstanceDown has no accompanying "instance" matcher
            {
                "id": "bol",
                "status": {"state": "active"},
                "updatedAt": "2025-01-02T10:00:00.002Z",
                "comment": "old",
                "createdBy": "admin2",
                "endsAt": "2025-01-02T10:00:00.002Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "other",
                        "value": "foo",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "alertname",
                        "value": "InstanceDown",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "hostname",  # not instance
                        "value": "hv123.matrix.net",
                    },
                ],
                "startsAt": "2025-01-01T10:00:00.002Z",
            },
            # An active silence for hv234
            {
                "id": "bar",
                "status": {"state": "active"},
                "updatedAt": "2025-01-16T07:32:25.792Z",
                "comment": "Testing.",
                "createdBy": "admin",
                "endsAt": "2025-01-16T10:51:00.279Z",
                "matchers": [
                    {"isEqual": True, "isRegex": False, "name": "env", "value": "dev"},
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "instance",
                        "value": "hv234.matrix.net",
                    },
                ],
                "startsAt": "2025-01-16T10:50:00.782Z",
            },
            # A pending silence that doesn't pertain to hvs
            {
                "id": "biz",
                "status": {"state": "pending"},
                "updatedAt": "2025-01-30T10:21:56.632Z",
                "comment": "pending create",
                "createdBy": "admin2",
                "endsAt": "2025-01-30T12:20:52.212Z",
                "matchers": [
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "cluster",
                        "value": "management",
                    },
                    {
                        "isEqual": True,
                        "isRegex": False,
                        "name": "severity",
                        "value": "warning",
                    },
                ],
                "startsAt": "2025-01-30T10:21:56.632Z",
            },
        ]
    )


@pytest.fixture(name="mock_silence_details")
def mock_silence_details_fixture():
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 2, 10, 0, 0)
    return SilenceDetails(
        matchers=[
            AlertMatcherDetails(name="matcher1", value="foo"),
            AlertMatcherDetails(name="matcher2", value="bar"),
        ],
        author="author",
        comment="comment",
        start_time_dt=date_start,
        end_time_dt=date_end,
    )


@patch("alertmanager_api.silence.requests.post")
def test_schedule_silence_success(mock_post, mock_silence_details):
    """
    use case: the call to schedule_silence() works fine
    """
    mock_alertmanager_account = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    schedule_silence(mock_alertmanager_account, mock_silence_details)
    mock_post.assert_called_once()


@patch("alertmanager_api.silence.requests.post")
def test_schedule_silence_exception_is_raised_rc_is_not_200(
    mock_post, mock_silence_details
):
    """
    use case: the call to requests to schedule a silence
              raised an exception itself and logs the correct error message.
    """
    mock_alertmanager_account = MagicMock()

    # Simulate an HTTPError with a specific response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        response=mock_response
    )
    mock_post.return_value = mock_response
    with pytest.raises(requests.HTTPError):
        schedule_silence(mock_alertmanager_account, mock_silence_details)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_success(mock_delete):
    """
    use case: the call to remove_silence() works fine
    """
    mock_alertmanager_account = MagicMock()
    mock_silence_id = "silence_id"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_delete.return_value = mock_response
    remove_silence(mock_alertmanager_account, mock_silence_id)
    mock_delete.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_exception_is_raised_rc_is_not_200(mock_delete):
    """
    use case: the call to requests to remove a silence
              raised an HTTPError and logs the correct error message.
    """
    mock_alertmanager_account = MagicMock()
    mock_silence_id = "silence_id"

    # Simulate an HTTPError with a specific response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        response=mock_response
    )
    mock_delete.return_value = mock_response
    with pytest.raises(requests.HTTPError):
        remove_silence(mock_alertmanager_account, mock_silence_id)

    mock_delete.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.remove_silence")
def test_remove_silences_many(mock_remove_silence):
    """
    use case: remove_silences() successfully removes all silences in the list.
    """
    mock_alertmanager_account = MagicMock()
    mock_silence_list = ["id1", "id2"]

    remove_silences(mock_alertmanager_account, mock_silence_list)

    # Ensure `remove_silence()` was called for both silences
    assert mock_remove_silence.call_count == 2
    mock_remove_silence.assert_any_call(mock_alertmanager_account, "id1")
    mock_remove_silence.assert_any_call(mock_alertmanager_account, "id2")


@patch("alertmanager_api.silence.remove_silence")
def test_remove_silences_empty(mock_remove_silence):
    """
    use case: remove_silences() does nothing for empty list.
    """
    mock_alertmanager_account = MagicMock()
    mock_silence_list = []
    remove_silences(mock_alertmanager_account, mock_silence_list)
    # Ensure `remove_silence()` was not called for empty list
    mock_remove_silence.assert_not_called()


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_success(mock_get, mock_get_silence_out):
    """
    use case: the call to get_silences() works fine
    """
    mock_alertmanager_account = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_get_silence_out
    mock_get.return_value = mock_response

    res = get_silences(mock_alertmanager_account)
    mock_get.assert_called_once()

    # should get 7 outputs for the 7 mock silences set in mock_get_silence_out fixture
    assert len(res) == 7


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_http_error(mock_get):
    """
    use case: an HTTPError occurs while fetching silences, ensuring logging and exception handling.
    """
    mock_alertmanager_account = MagicMock()

    # Simulate an HTTPError with a specific response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        response=mock_response
    )
    mock_get.return_value = mock_response
    with pytest.raises(requests.HTTPError):
        get_silences(mock_alertmanager_account)

    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.requests.get")
def test_get_active_silences(mock_get, mock_get_silence_out):
    """
    use case: test get_active_silences function works properly
    """
    mock_alertmanager_account = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_get_silence_out
    mock_get.return_value = mock_response
    res = get_active_silences(mock_alertmanager_account)

    # should get 4 active silences as set in mock_get_silence_out fixture
    mock_get.assert_called_once()
    assert len(res) == 4


@patch("alertmanager_api.silence.requests.get")
def test_get_valid_silences(mock_get, mock_get_silence_out):
    """
    use case: test get_valid_silence function works properly
    """
    mock_alertmanager_account = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_get_silence_out
    mock_get.return_value = mock_response
    res = get_valid_silences(mock_alertmanager_account)

    # should get 5 (4 active + 1 pending) silences as set in mock_get_silence_out fixture
    mock_get.assert_called_once()
    assert len(res) == 5


@patch("alertmanager_api.silence.requests.get")
def test_get_hv_silences(mock_get, mock_get_silence_out):
    """
    use case: test get_valid_silence function works properly
    """
    mock_alertmanager_account = MagicMock()
    hostname = "hv123.matrix.net"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_get_silence_out
    mock_get.return_value = mock_response
    res = get_hv_silences(mock_alertmanager_account, hostname)

    # should get 2 (1 active + 2 expired) silences as set in mock_get_silence_out fixture
    # should ignore 2 active but misconfigured alerts
    mock_get.assert_called_once()
    assert len(res) == 3
