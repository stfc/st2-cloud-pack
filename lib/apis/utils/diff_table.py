import deepdiff
from deepdiff import extract


def diff_to_tabulate_table(obj1, obj2, excluded_paths=None):
    """
    Formats the output from DeepDiff into a list of lists suitable for tabulate,
    showing path, before, and after values.
    """
    diff_output = deepdiff.DeepDiff(
        t1=obj1,
        t2=obj2,
        exclude_paths=excluded_paths,
        threshold_to_diff_deeper=0,
        ignore_order=True,
    )

    table_data = []

    # Handle 'values_changed'
    if "values_changed" in diff_output:
        for path, change_info in diff_output["values_changed"].items():
            table_data.append(
                [
                    path,
                    change_info.get("old_value", "Not Present"),
                    change_info.get("new_value", "Not Present"),
                ]
            )

    # Handle 'dictionary_item_added'
    if "dictionary_item_added" in diff_output:
        for path in diff_output["dictionary_item_added"]:
            table_data.append(
                [
                    path,
                    "Not Present",  # No old value for added items
                    extract(obj2, path),
                ]
            )

    # Handle 'dictionary_item_removed'
    if "dictionary_item_removed" in diff_output:
        for path in diff_output["dictionary_item_removed"]:
            table_data.append(
                [
                    path,
                    extract(obj1, path),
                    "Not Present",  # No new value for removed items
                ]
            )

    # Handle 'iterable_item_added'
    if "iterable_item_added" in diff_output:
        for path, value in diff_output["iterable_item_added"].items():
            table_data.append([path, "N/A", value])

    # Handle 'iterable_item_removed'
    if "iterable_item_removed" in diff_output:
        for path, value in diff_output["iterable_item_removed"].items():
            table_data.append([path, value, "N/A"])

    # Handle 'type_changes'
    if "type_changes" in diff_output:
        for path, change_info in diff_output["type_changes"].items():
            table_data.append(
                [
                    path,
                    f"'{change_info.get('old_value')}' (Type: {change_info.get('old_type').__name__})",
                    f"'{change_info.get('new_value')}' (Type: {change_info.get('new_type').__name__})",
                ]
            )

    return table_data
