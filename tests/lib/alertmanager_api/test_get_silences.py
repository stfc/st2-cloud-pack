from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException
from alertmanager_api.silence import AlertManagerAPI


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_sucess(mock_post):
    """
    use case: the call to get_silences() works fine
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(alertmanager_account)
    class_instance.get_silences()
    mock_post.assert_called_once()


@patch("alertmanager_api.silence.requests.get")
def test_get_silences_exception_is_raised_on_failure(mock_get):
    """
    use case: the call to get all silences
              raised an exception itself
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(alertmanager_account)
    mock_get.side_effect = RequestException("An error occurred")
    try:
        class_instance.get_silences()
    except RequestException as req_ex:
        assert "An error occurred" in str(req_ex)
