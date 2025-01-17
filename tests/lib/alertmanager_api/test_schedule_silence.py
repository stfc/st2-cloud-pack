from unittest.mock import MagicMock, patch
from datetime import datetime
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from requests.exceptions import RequestException
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
def missing_instance_name(
    start_time_dt, end_time_dt
):  #  pylint: disable=redefined-outer-name
    silence_details = SilenceDetails(
        start_time_dt=start_time_dt,
        end_time_dt=end_time_dt,
        comment="comment",
        author="author",
    )
    return silence_details


@pytest.fixture
def missing_start_time(end_time_dt):  #  pylint: disable=redefined-outer-name
    silence_details = SilenceDetails(
        instance_name="name",
        end_time_dt=end_time_dt,
        comment="comment",
        author="author",
    )
    return silence_details


@pytest.fixture
def missing_end_time(start_time_dt):  #  pylint: disable=redefined-outer-name
    silence_details = SilenceDetails(
        instance_name="name",
        start_time_dt=start_time_dt,
        comment="comment",
        author="author",
    )
    return silence_details


@pytest.fixture
def missing_author(start_time_dt, end_time_dt):  #  pylint: disable=redefined-outer-name
    silence_details = SilenceDetails(
        instance_name="name",
        start_time_dt=start_time_dt,
        end_time_dt=end_time_dt,
        comment="comment",
    )
    return silence_details


@pytest.fixture
def missing_comment(
    start_time_dt, end_time_dt
):  #  pylint: disable=redefined-outer-name
    silence_details = SilenceDetails(
        instance_name="name",
        start_time_dt=start_time_dt,
        end_time_dt=end_time_dt,
        author="author",
    )
    return silence_details


def test_missing_instance_name(
    class_instance, missing_instance_name
):  #  pylint: disable=redefined-outer-name
    with pytest.raises(
        MissingMandatoryParamError, match="Missing silence instance name"
    ):
        class_instance.schedule_silence(missing_instance_name)


def test_missing_start_time(
    class_instance, missing_start_time
):  #  pylint: disable=redefined-outer-name
    with pytest.raises(MissingMandatoryParamError, match="Missing silence start time"):
        class_instance.schedule_silence(missing_start_time)


def test_missing_end_time(
    class_instance, missing_end_time
):  #  pylint: disable=redefined-outer-name
    with pytest.raises(MissingMandatoryParamError, match="Missing silence end time"):
        class_instance.schedule_silence(missing_end_time)


def test_missing_attribute_author(
    class_instance, missing_author
):  #  pylint: disable=redefined-outer-name
    with pytest.raises(MissingMandatoryParamError, match="Missing silence author"):
        class_instance.schedule_silence(missing_author)


def test_missing_attribute_comment(
    class_instance, missing_comment
):  #  pylint: disable=redefined-outer-name
    with pytest.raises(MissingMandatoryParamError, match="Missing silence comment"):
        class_instance.schedule_silence(missing_comment)


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
def test_schedule_silence_exception_is_raised_status_code_not_200(mock_post):
    """
    use case: the call to requests to schedule a silence
              returned a RC different than 200
    """
    alertmanager_account = MagicMock()
    class_instance = AlertManagerAPI(  #  pylint: disable=redefined-outer-name
        alertmanager_account
    )
    date_start = datetime(2025, 1, 1, 10, 0, 0)
    date_end = datetime(2025, 1, 1, 10, 0, 0)
    silence = SilenceDetails("hostname", date_start, date_end, "author", "comment")
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.text = "rc is 201"
    mock_post.return_value = mock_response
    try:
        class_instance.schedule_silence(silence)
    except RequestException as req_ex:
        assert "Failed to create silence. " in str(req_ex)
        assert "Response status code: 201" in str(req_ex)
        assert "Response text: rc is 201" in str(req_ex)


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
    try:
        class_instance.schedule_silence(silence)
    except RequestException as req_ex:
        assert "An error occurred" in str(req_ex)
