from unittest.mock import Mock

from apis.elog_api.elog import add_record_to_elog


def test_add_record_to_elog():
    # Create a fake ELOG account.
    elog_account = Mock()
    elog_account.username = "test_user"
    elog_account.elog_endpoint = "https://elog.example.test"

    # Create a fake authenticated HTTP session.
    session = Mock()
    elog_account.authenticate.return_value = session

    # Create a fake HTTP response.
    response = Mock()
    session.post.return_value = response

    # Call the function under test.
    add_record_to_elog(
        elog_account,
        subject="Test subject",
        body="Test body",
    )

    # Verify authentication was requested.
    elog_account.authenticate.assert_called_once_with()

    # Verify the expected request was sent.
    session.post.assert_called_once_with(
        "https://elog.example.test",
        files={
            "cmd": (None, "Submit"),
            "Category": (None, "Routine"),
            "Subject": (None, "Test subject"),
            "Author": (None, "test_user"),
            "Encoding": (None, "plain"),
            "Text": (None, "Test body"),
        },
    )

    # Verify HTTP errors would be raised.
    response.raise_for_status.assert_called_once_with()
