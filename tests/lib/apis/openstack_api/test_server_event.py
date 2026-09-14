from apis.openstack_api.enums.server_event import ServerEvent


def test_server_event_values_match_nova_action_names():
    """
    Tests the event names match the values Nova records in the instance
    action table
    """
    assert ServerEvent.START.value == "start"
    assert ServerEvent.STOP.value == "stop"
    assert ServerEvent.SHELVE.value == "shelve"
    assert ServerEvent.UNSHELVE.value == "unshelve"
    assert ServerEvent.SHELVE_OFFLOAD.value == "shelveOffload"


def test_from_str_returns_none_for_untracked_events():
    """
    Tests that from_string maps known names to their members
    (case-insensitively) and every other name to None
    """
    assert ServerEvent.from_string("stop") is ServerEvent.STOP
    assert ServerEvent.from_string("shelveOffload") is ServerEvent.SHELVE_OFFLOAD
    assert ServerEvent.from_string("START") is ServerEvent.START
    assert ServerEvent.from_string("os-reboot:reboot") is None
    assert ServerEvent.from_string("foo") is None
