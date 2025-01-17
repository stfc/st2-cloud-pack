from unittest.mock import MagicMock, patch
from datetime import datetime
from requests.exceptions import RequestException
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from alertmanager_api.silence_details import SilenceDetails
from alertmanager_api.silence import AlertManagerAPI


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_sucess(mock_post):
    """
    use case: the call to schedule_silence() works fine
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(alertmanager_account)
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
    class_instance = AlertManagerAPI(alertmanager_account)
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    try:
        class_instance.remove_silence(silence)
    except MissingMandatoryParamError as miss_ex:
        assert "Missing silence silence_id" in str(miss_ex)


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_exception_is_raised_status_code_not_200(mock_post):
    """
    use case: the call to requests to schedule a silence
              returned a RC different than 200
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(alertmanager_account)
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    silence.silence_id = "silence_id"
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.text = "rc is 201"
    mock_post.return_value = mock_response
    try:
        class_instance.remove_silence(silence)
    except RequestException as req_ex:
        assert f"Failed to delete silence with ID {silence.silence_id}" in str(req_ex)
        assert "Response status code: 201" in str(req_ex)
        assert "Response text: rc is 201" in str(req_ex)


@patch("alertmanager_api.silence.requests.delete")
def test_schedule_silence_exception_is_raised_on_failure(mock_post):
    """
    use case: the call to requests to schedule a silence
              raised an exception itself
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(alertmanager_account)
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    silence.silence_id = "silence_id"
    mock_post.side_effect = RequestException("An error occurred")
    try:
        class_instance.remove_silence(silence)
    except RequestException as req_ex:
        assert "An error occurred" in str(req_ex)
