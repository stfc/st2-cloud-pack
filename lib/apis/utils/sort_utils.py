from typing import Dict, List


def sort_dictionaries(data: List[Dict], key: str, reverse: bool = False):
    """
    Sort a list of dictionaries by the value of a specified key.
    """
    for item in data:
        if key not in item:
            msg = f"Key '{key}' not found in dictionary: {item}"
            raise KeyError(msg)
    return sorted(data, key=lambda item: item[key], reverse=reverse)
