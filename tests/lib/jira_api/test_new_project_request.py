from unittest.mock import MagicMock
from munch import DefaultMunch
from jira_api.issue_types.new_project_request import NewProjectRequestIssue

MOCK_ISSUE_DATA_TRUE = [
    DefaultMunch.fromDict(
        {
            "key": "proforma.forms.i1",
            "value": {
                "state": {
                    "visibility": "e",
                    "status": "o",
                    "answers": {
                        "5": {
                            "adf": {
                                "version": 1,
                                "type": "doc",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "This is the project description",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "32": {"text": "20"},
                        "1": {
                            "users": [
                                {"id": "712020:73aa06da-3198-4cae-85f2-601f62052740"}
                            ]
                        },
                        "31": {"text": "", "choices": ["1"]},
                        "42": {"text": "mock_fedid"},
                        "27": {"text": "", "choices": ["1"]},
                        "29": {
                            "adf": {
                                "version": 1,
                                "type": "doc",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "thing 1 and thing 2",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "3": {"text": "test-project-10-03-2025"},
                        "45": {"text": "10"},
                        "34": {"text": "0"},
                        "44": {"text": "0"},
                        "33": {"text": "50"},
                        "24": {"text": "Cloud"},
                        "35": {"text": "0"},
                        "17": {
                            "adf": {
                                "version": 1,
                                "type": "doc",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Big powerful GPUs because they\u2019re fun",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "25": {"text": "mock_user@mock_email"},
                    },
                },
            },
        }
    )
]


def test_create_properties_true():
    """Test the form is serialised correctly."""
    mock_conn = MagicMock()
    mock_conn.issue_properties.return_value = MOCK_ISSUE_DATA_TRUE
    issue = NewProjectRequestIssue(mock_conn, "ABC123")
    res = issue.properties
    mock_conn.issue_properties.assert_called_once_with("ABC123")
    assert res["project_name"] == "test-project-10-03-2025"
    assert res["users"] == "thing 1 and thing 2"
    assert res["cpus"] == 20
    assert res["vms"] == 10
    assert res["memory"] == 50
    assert res["shared_storage"] == 0
    assert res["object_storage"] == 0
    assert res["block_storage"] == 0
    assert res["gpus"] == "Big powerful GPUs because they’re fun"
    assert res["contact_email"] == "mock_user@mock_email"
    assert res["reporting_fed_id"] == "mock_fedid"
    # Assert specifically for "True" here as
    assert res["externally_accessible"] is True
    assert res["tos_agreement"] is True


MOCK_ISSUE_DATA_FALSE = [
    DefaultMunch.fromDict(
        {
            "key": "proforma.forms.i1",
            "value": {
                "state": {
                    "visibility": "e",
                    "status": "o",
                    "answers": {
                        "5": {
                            "adf": {
                                "version": 1,
                                "type": "doc",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "This is the project description",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "32": {"text": "20"},
                        "1": {
                            "users": [
                                {"id": "712020:73aa06da-3198-4cae-85f2-601f62052740"}
                            ]
                        },
                        "31": {"text": "", "choices": ["2"]},
                        "42": {"text": "mock_fedid"},
                        "27": {"text": "", "choices": ["1"]},
                        "29": {
                            "adf": {
                                "version": 1,
                                "type": "doc",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "thing 1 and thing 2",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "3": {"text": "test-project-10-03-2025"},
                        "45": {"text": "10"},
                        "34": {"text": "0"},
                        "44": {"text": "0"},
                        "33": {"text": "50"},
                        "24": {"text": "Cloud"},
                        "35": {"text": "0"},
                        "17": {
                            "adf": {
                                "version": 1,
                                "type": "doc",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Big powerful GPUs because they\u2019re fun",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "25": {"text": "mock_user@mock_email"},
                    },
                },
            },
        }
    )
]


def test_create_properties_false():
    """Test the form is serialised correctly."""
    mock_conn = MagicMock()
    mock_conn.issue_properties.return_value = MOCK_ISSUE_DATA_FALSE
    issue = NewProjectRequestIssue(mock_conn, "ABC123")
    res = issue.properties
    mock_conn.issue_properties.assert_called_once_with("ABC123")
    assert res["project_name"] == "test-project-10-03-2025"
    assert res["users"] == "thing 1 and thing 2"
    assert res["cpus"] == 20
    assert res["vms"] == 10
    assert res["memory"] == 50
    assert res["shared_storage"] == 0
    assert res["object_storage"] == 0
    assert res["block_storage"] == 0
    assert res["gpus"] == "Big powerful GPUs because they’re fun"
    assert res["contact_email"] == "mock_user@mock_email"
    assert res["reporting_fed_id"] == "mock_fedid"
    # Assert specifically for "True" here as
    assert res["externally_accessible"] is False
    assert res["tos_agreement"] is True
