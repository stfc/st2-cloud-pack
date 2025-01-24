from unittest.mock import MagicMock, patch
from datetime import datetime
import pytest
from requests import HTTPError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from alertmanager_api.silence_details import SilenceDetails
from alertmanager_api.silence import AlertManagerAPI


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_sucess(mock_post):
    """
    use case: the call to remove_silence() works fine
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
    with pytest.raises(MissingMandatoryParamError, match="Missing silence silence_id"):
        class_instance.remove_silence(silence)


@patch("alertmanager_api.silence.requests.delete")
def test_remove_silence_exception_is_raised_rc_is_not_200(mock_post):
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
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.raise_for_status.side_effect = HTTPError()
    mock_post.return_value = mock_response
    with pytest.raises(HTTPError):
        class_instance.remove_silence(silence)
    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()
