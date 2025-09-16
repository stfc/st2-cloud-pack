from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails


def test_from_dict():
    """tests that AlertMatcherDetails gets created using from_dict() static method"""
    res = AlertMatcherDetails.from_dict({"name": "matcher1", "value": "foo"})
    assert res.name == "matcher1"
    assert res.value == "foo"
    # defaults should be set appropriately
    assert res.is_equal is True
    assert res.is_regex is False


def test_to_dict():
    """tests that AlertMatcherDetails to_dict method works"""

    res = AlertMatcherDetails(name="matcher1", value="foo").to_dict()
    assert res["name"] == "matcher1"
    assert res["value"] == "foo"
    # defaults should be set appropriately
    assert res["isEqual"] is True
    assert res["isRegex"] is False
