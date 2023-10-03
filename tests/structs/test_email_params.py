from structs.email.email_params import EmailParams
from structs.email.email_template_details import EmailTemplateDetails


def test_from_dict():
    """
    Tests that from_dict() static method works properly
    this method should build a EmailParams dataclass from a valid dictionary
    """
    mock_valid_kwargs = {
        "subject": "subject1",
        "email_from": "from@example.com",
        "email_to": "test@example.com",
        "email_cc": ["cc1@example.com", "cc2@example.com"],
        "attachment_filepaths": ["path/to/file1", "path/to/file2"],
        "email_templates": EmailTemplateDetails(
            template_name="template1",
            template_params={"arg1": "val1", "arg2": "val2"},
        ),
    }
    mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

    res = EmailParams.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
    for key, val in mock_valid_kwargs.items():
        assert val == getattr(res, key)
