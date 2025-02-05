from unittest.mock import MagicMock, patch
from datetime import datetime
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from requests.exceptions import RequestException
from requests import HTTPError
import pytest
from alertmanager_api.silence_details import SilenceDetails
from alertmanager_api.silence import AlertManagerAPI


@pytest.fixture
def start_time_dt():
    return datetime(2025, 1, 1, 10, 0, 0)


@pytest.fixture
def end_time_dt():
    return datetime(2025, 1, 1, 10, 0, 0)


@pytest.fixture
def class_instance():
    alertmanager_account = MagicMock()
    instance = AlertManagerAPI(alertmanager_account)
    return instance


@pytest.fixture
def silence_details(
    start_time_dt, end_time_dt
):  #  pylint: disable=redefined-outer-name
    """Base fixture for SilenceDetails."""
    return SilenceDetails(
        hostname="name",
        start_time_dt=start_time_dt,
        end_time_dt=end_time_dt,
        comment="comment",
        author="author",
    )


@pytest.mark.parametrize(
    "missing_attr, expected_message",
    [
        ("hostname", "Missing silence hostname"),
        ("start_time_dt", "Missing silence start time"),
        ("end_time_dt", "Missing silence end time"),
        ("author", "Missing silence author"),
        ("comment", "Missing silence comment"),
    ],
)
def test_missing_mandatory_fields(
    class_instance, silence_details, missing_attr, expected_message
):  #  pylint: disable=redefined-outer-name
    """Test missing required attributes in SilenceDetails."""
    setattr(silence_details, missing_attr, None)  # Set missing attribute to None
    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(MissingMandatoryParamError, match=expected_message):
            class_instance.schedule_silence(silence_details)
        mock_critical.assert_called_once_with(expected_message)


@patch("alertmanager_api.silence.requests.post")
def test_schedule_silence_sucess(mock_post):
    """
    use case: the call to schedule_silence() works fine
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    class_instance.schedule_silence(silence)
    mock_post.assert_called_once()


@patch("alertmanager_api.silence.requests.post")
def test_schedule_silence_exception_is_raised_rc_is_not_200(mock_post):
    """
    use case: the call to requests to schedule a silence
              raised an exception itself and logs the correct error message.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")

    # Simulate an HTTPError with a specific response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
    mock_post.return_value = mock_response

    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(HTTPError):
            class_instance.schedule_silence(silence)

        # Verify that the log message was correctly formatted
        expected_message = (
            f"Failed to create silence in Alertmanager: {mock_response.raise_for_status.side_effect} "
            f"Failed to create silence. Response status code: 500 Response text: Internal Server Error"
        )
        mock_critical.assert_called_once_with(expected_message)

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.requests.post")
def test_schedule_silence_exception_is_raised_on_failure(mock_post):
    """
    use case: the call to requests to schedule a silence
              raised an exception itself
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    mock_post.side_effect = RequestException("An error occurred")
    with pytest.raises(RequestException, match="An error occurred"):
        class_instance.schedule_silence(silence)


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_sucess(mock_post):
    """
    use case: the call to remove_silence() works fine
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    silence.silence_id = "silence_id"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    class_instance.remove_silence(silence)
    mock_post.assert_called_once()


def test_remove_silence_missing_attribute():
    """
    use case: the object Silence is missing attribute silenceID
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    with pytest.raises(MissingMandatoryParamError, match="Missing silence silence_id"):
        class_instance.remove_silence(silence)


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_exception_is_raised_rc_is_not_200(mock_delete):
    """
    use case: the call to requests to remove a silence
              raised an HTTPError and logs the correct error message.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    silence.silence_id = "silence_id"

    # Simulate an HTTPError with a response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
    mock_delete.return_value = mock_response

    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(HTTPError):
            class_instance.remove_silence(silence)

        # Verify that the log message was correctly formatted
        expected_message = (
            f"Failed to delete silence in Alertmanager: {mock_response.raise_for_status.side_effect} "
            f"Failed to delete silence with ID {silence.silence_id}. "
            f"Response status code: 500 Response text: Internal Server Error"
        )
        mock_critical.assert_called_once_with(expected_message)

    mock_delete.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_general_exception_is_logged_and_raised(mock_delete):
    """
    use case: an unexpected exception occurs during remove_silence()
              and it is properly logged before being raised.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    silence.silence_id = "silence_id"

    # Simulate a general exception (not an HTTPError)
    mock_delete.side_effect = Exception("Unexpected error")

    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(Exception, match="Unexpected error"):
            class_instance.remove_silence(silence)

        # Verify that the log message was correctly formatted
        expected_message = "Failed to create silence in Alertmanager: Unexpected error "
        mock_critical.assert_called_once_with(expected_message)

    mock_delete.assert_called_once()


@patch.object(AlertManagerAPI, "remove_silence")
def test_remove_silences_success(mock_remove_silence):
    """
    use case: remove_silences() successfully removes all silences in the list.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 11, 0, 0)

    silence_1 = SilenceDetails("host1", date_start, date_end, "author", "comment")
    silence_1.silence_id = "id1"
    silence_2 = SilenceDetails("host2", date_start, date_end, "author", "comment")
    silence_2.silence_id = "id2"

    silence_list = [silence_1, silence_2]

    class_instance.remove_silences(silence_list)

    # Ensure `remove_silence()` was called for both silences
    assert mock_remove_silence.call_count == 2
    mock_remove_silence.assert_any_call(silence_1)
    mock_remove_silence.assert_any_call(silence_2)


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_sucess(mock_post):
    """
    use case: the call to get_silences() works fine
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )
    class_instance.get_silences()
    mock_post.assert_called_once()


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_http_error(mock_get):
    """
    use case: an HTTPError occurs while fetching silences, ensuring logging and exception handling.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    # Simulate an HTTP error with a response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
    mock_get.return_value = mock_response

    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(HTTPError):
            class_instance.get_silences()

        # Verify that the correct error message is logged
        expected_message = (
            f"Failed to get silences from Alertmanager: {mock_response.raise_for_status.side_effect} "
            f"Failed to get silences. Response status code: 500 Response text: Internal Server Error"
        )
        mock_critical.assert_called_once_with(expected_message)

    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_request_exception(mock_get):
    """
    use case: a `RequestException` occurs (e.g., timeout, connection error), ensuring proper logging.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    # Simulate a RequestException with a response
    mock_response = MagicMock()
    mock_response.status_code = 408
    mock_response.text = "Request Timeout"
    request_exception = RequestException("Network error", response=mock_response)
    mock_get.side_effect = request_exception

    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(RequestException):
            class_instance.get_silences()

        # Verify that the correct error message is logged
        expected_message = (
            "Failed to get silences from Alertmanager: Network error "
            "Response status code: 408 Response text: Request Timeout"
        )
        mock_critical.assert_called_once_with(expected_message)

    mock_get.assert_called_once()


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_general_exception(mock_get):
    """
    use case: a general `Exception` occurs (e.g., timeout, connection error), ensuring proper logging.
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )

    # Simulate a general exception (not an HTTPError)
    mock_get.side_effect = Exception("Unexpected error")

    with patch.object(class_instance.log, "critical") as mock_critical:
        with pytest.raises(Exception, match="Unexpected error"):
            class_instance.get_silences()

        # Verify that the log message was correctly formatted
        expected_message = "Failed to get silences from Alertmanager: Unexpected error "
        mock_critical.assert_called_once_with(expected_message)

    mock_get.assert_called_once()
