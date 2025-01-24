from datetime import datetime
import json
import pytest
from alertmanager_api.silence_details import SilenceDetails, SilenceDetailsHandler


@pytest.mark.parametrize(
    "attr, value, expected_message",
    [
        ("start_time_dt", "not_dt", "start_time_dt must be of type datetime."),
        ("end_time_dt", "not_dt", "end_time_dt must be of type datetime."),
    ],
)
def test_invalid_datetime_fields(attr, value, expected_message):
    """Test that SilenceDetails raises a TypeError for invalid datetime fields."""
    kwargs = {
        "instance_name": "name",
        "start_time_dt": datetime(2025, 1, 1, 10, 0, 0),
        "end_time_dt": datetime(2025, 1, 1, 10, 0, 0),
        "author": "author",
        "comment": "comment",
    }
    kwargs[attr] = value  # Set the invalid attribute

    with pytest.raises(TypeError, match=expected_message):
        SilenceDetails(**kwargs)


@pytest.mark.parametrize(
    "status, expected_active, expected_pending, expected_expired, expected_valid",
    [
        ("active", True, False, False, True),  # "active" should be valid
        ("pending", False, True, False, True),  # "pending" should be valid
        ("expired", False, False, True, False),  # "expired" is not valid
    ],
)
def test_status_properties(
    status, expected_active, expected_pending, expected_expired, expected_valid
):
    """Test that is_active, is_pending, is_expired, and is_valid return correct values for each status."""
    instance = SilenceDetails(status=status)

    assert instance.is_active == expected_active
    assert instance.is_pending == expected_pending
    assert instance.has_expired == expected_expired
    assert instance.is_valid == expected_valid


# ==============================================================================
#   test class SilenceDetailsHandler
# ==============================================================================


def test_add_from_json_with_string():
    """Test that add_from_json correctly parses a JSON string into a list of dictionaries."""

    json_input = '[{"id": "123",\
"startsAt": "2025-01-16T10:50:00.000Z",\
"endsAt": "2025-01-16T10:51:00.000Z",\
"createdBy": "admin",\
"comment": "Testing.",\
"status": {"state": "active"},\
"matchers": [{"name": "instance", "value": "hv123.matrix.net"}]}]'
    expected_output = json.loads(json_input)  # Expected parsed list

    handler = SilenceDetailsHandler()
    handler.add_from_json(json_input)  # Should parse the string

    assert isinstance(
        handler, SilenceDetailsHandler
    )  # Ensure handler is still a valid instance
    assert len(handler) == len(
        expected_output
    )  # Ensure same number of items were added
    for silence_obj, expected_silence in zip(handler, expected_output):
        assert silence_obj.silence_id == expected_silence["id"]
        assert silence_obj.start_time_dt == datetime.fromisoformat(
            expected_silence["startsAt"].replace("Z", "+00:00")
        )
        assert silence_obj.end_time_dt == datetime.fromisoformat(
            expected_silence["endsAt"].replace("Z", "+00:00")
        )
        assert silence_obj.author == expected_silence["createdBy"]
        assert silence_obj.comment == expected_silence["comment"]
        assert silence_obj.status == expected_silence["status"]["state"]
        assert silence_obj.instance_name == expected_silence["matchers"][0]["value"]


def test_add_from_json_with_list():
    """Test that add_from_json correctly accepts a list input without parsing."""

    json_list = [
        {
            "id": "456",
            "startsAt": "2025-01-16T10:50:00.000Z",
            "endsAt": "2025-01-16T10:51:00.000Z",
            "createdBy": "admin",
            "comment": "Testing.",
            "status": {"state": "pending"},
            "matchers": [{"name": "instance", "value": "hv123.matrix.net"}],
        }
    ]

    handler = SilenceDetailsHandler()
    handler.add_from_json(json_list)  # Should not parse, just accept the list

    assert isinstance(handler, SilenceDetailsHandler)
    assert len(handler) == 1
    assert handler[0].silence_id == "456"


def test_add_from_json_with_invalid_json():
    """Test that a malformed JSON string raises a JSONDecodeError."""

    invalid_json_input = '{"id": "789",\
"startsAt": "2025-01-16T10:50:00.000Z",\
"endsAt": "2025-01-16T10:51:00.000Z",\
"createdBy": "admin" '  # Missing closing brace

    handler = SilenceDetailsHandler()

    with pytest.raises(json.JSONDecodeError):
        handler.add_from_json(invalid_json_input)


@pytest.mark.parametrize(
    "property_name, active_ids",
    [
        ("active_silences", ["id1"]),  # Only "active" should be included
        (
            "valid_silences",
            ["id1", "id2"],
        ),  # "active" and "pending" are considered valid
    ],
)
def test_filtered_silences(property_name, active_ids):
    """Test that active_silences and valid_silences return expected results."""
    # Create SilenceDetails instances with different statuses
    silence_active = SilenceDetails(
        "instance1", None, None, "admin", "Active silence", "id1", "active"
    )
    silence_pending = SilenceDetails(
        "instance2", None, None, "admin", "Pending silence", "id2", "pending"
    )
    silence_expired = SilenceDetails(
        "instance3", None, None, "admin", "Expired silence", "id3", "expired"
    )

    # Set their statuses
    silence_active.status = "active"
    silence_pending.status = "pending"
    silence_expired.status = "expired"

    # Create handler and add silences
    handler = SilenceDetailsHandler()
    handler.extend([silence_active, silence_pending, silence_expired])

    # Dynamically call the property method
    filtered_handler = getattr(handler, property_name)

    assert isinstance(
        filtered_handler, SilenceDetailsHandler
    )  # Must return the same class type
    assert {silence.silence_id for silence in filtered_handler} == set(
        active_ids
    )  # Compare expected IDs


@pytest.mark.parametrize(
    "search_name, expected_ids",
    [
        ("hv123.matrix.net", ["id1", "id2"]),  # Match two instances
        ("hv456.matrix.net", ["id3"]),  # Match one instance
        ("nonexistent.net", []),  # No matches
    ],
)
def test_get_by_name(search_name, expected_ids):
    """Test that get_by_name correctly filters silences based on instance_name."""

    # Create SilenceDetails instances with different instance names
    silence1 = SilenceDetails(
        "hv123.matrix.net", None, None, "admin", "Testing 1", "id1", "active"
    )
    silence2 = SilenceDetails(
        "hv123.matrix.net", None, None, "admin", "Testing 2", "id2", "pending"
    )
    silence3 = SilenceDetails(
        "hv456.matrix.net", None, None, "admin", "Testing 3", "id3", "expired"
    )

    # Create handler and add silences
    handler = SilenceDetailsHandler()
    handler.extend([silence1, silence2, silence3])

    # Call get_by_name
    filtered_handler = handler.get_by_name(search_name)

    assert isinstance(
        filtered_handler, SilenceDetailsHandler
    )  # Must return the same class type
    assert {silence.silence_id for silence in filtered_handler} == set(
        expected_ids
    )  # Compare expected IDs


def test_get_by_name_empty_handler():
    """Test that get_by_name returns an empty SilenceDetailsHandler when no silences exist."""

    handler = SilenceDetailsHandler()
    filtered_handler = handler.get_by_name("hv123.matrix.net")

    assert isinstance(filtered_handler, SilenceDetailsHandler)
    assert len(filtered_handler) == 0  # Expecting an empty result
