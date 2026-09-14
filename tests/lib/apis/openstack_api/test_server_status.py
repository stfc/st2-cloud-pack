from apis.openstack_api.enums.server_status import ServerStatus


def test_server_status_values_match_nova_status_strings():
    """
    Tests the state strings match the values Nova returns in the server
    status field
    """
    assert ServerStatus.ACTIVE.value == "ACTIVE"
    assert ServerStatus.ERROR.value == "ERROR"
    assert ServerStatus.SHELVED.value == "SHELVED"
    assert ServerStatus.SHELVED_OFFLOADED.value == "SHELVED_OFFLOADED"
    assert ServerStatus.SHUTOFF.value == "SHUTOFF"


def test_server_status_from_str_is_case_insensitive():
    """
    Tests that from_string matches tracked states case-insensitively
    and returns None for states that are not tracked
    """
    assert ServerStatus.from_string("shutoff") is ServerStatus.SHUTOFF
    assert ServerStatus.from_string("active") is ServerStatus.ACTIVE
    assert ServerStatus.from_string("shelved") is ServerStatus.SHELVED
    offloaded = ServerStatus.from_string("Shelved_Offloaded")
    assert offloaded is ServerStatus.SHELVED_OFFLOADED
    assert ServerStatus.from_string("ERROR") is ServerStatus.ERROR
    assert ServerStatus.from_string("foo") is None
