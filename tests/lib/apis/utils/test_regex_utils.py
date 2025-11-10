from apis.utils.regex_utils import list_to_regex_pattern


def test_list_to_regex_pattern():
    """
    Tests list_to_regex_pattern() function
    Creates regex pattern from list
    """
    mock_list = ["img1", "img2", "img3"]
    res = list_to_regex_pattern(mock_list)
    assert res == "(.*img1|.*img2|.*img3)"
