import re


def list_to_regex_pattern(string_list):
    """
    converts a list of strings into a regex pattern that matches any occurrence of any string in the input list.
    :param string_list: a list of strings
    """
    escaped_strings = [re.escape(s) for s in string_list]
    regex_pattern = "|.*".join(escaped_strings)
    return f"(.*{regex_pattern})"
