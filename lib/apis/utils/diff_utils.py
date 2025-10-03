import fnmatch
import re
from collections import Counter, deque
from typing import Any, Deque, Dict, List, Set, Tuple, Union


def _format_value(value: Any) -> str:
    """
    Format a value for display in the difference report.

    :param value: The value to format.
    :return: A string representation of the value, truncated if necessary.
    """
    if value is None:
        return "None"
    if isinstance(value, (str, int, float, bool)):
        return repr(value)
    # Truncate representation of complex objects for readability
    return f"{type(value).__name__}: {str(value)[:50]}..."


def _normalize_path(path: str) -> str:
    """
    Convert a path string (e.g., root['a'][0]) to a simplified, slash-separated
    format (e.g., root/a/0) for use with fnmatch glob matching.

    :param path: The path string in bracket notation.
    :return: The normalized, slash-separated path string.
    """
    parts = re.findall(r"\[(.*?)\]", path)
    cleaned_parts = [part.strip("'\"") for part in parts]
    return "root/" + "/".join(cleaned_parts)


# pylint: disable=too-few-public-methods
class DiffUtils:
    """
    Encapsulates the state and configuration for the diff process.

    This class manages:
      - configuration (excluded paths, ignore_order flag),
      - current state (changes, queue, visited pairs),
      - and dispatch logic for comparing dicts, lists, sets, and primitives.
    """

    def __init__(
        self,
        exclude_paths: Union[List[str], Set[str]] = None,
        ignore_order: bool = True,
    ):
        """
        Initialize a DiffUtils instance with optional configuration.

        :param exclude_paths: Set of glob-like path patterns to ignore.
        :param ignore_order: If True, lists are compared as unordered collections.
        :return: None
        """
        self.exclude_paths: Set[str] = set(exclude_paths or [])
        self.ignore_order: bool = ignore_order

        # State tracking
        self.changes: List[List[str]] = []
        self.queue: Deque[Tuple[Any, Any, str]] = deque()
        # Track object ID pairs to prevent infinite recursion on circular references
        self.visited_pairs: Set[Tuple[int, int]] = set()

    def _is_excluded(self, path: str) -> bool:
        """
        Check if a path matches any excluded pattern using glob matching.

        :param path: The current path string in bracket notation.
        :return: True if the path is excluded, False otherwise.
        """
        norm_path = _normalize_path(path)
        for pattern in self.exclude_paths:
            if fnmatch.fnmatch(norm_path, _normalize_path(pattern)):
                return True
        return False

    def _get_diff_dict(self, source: Dict, target: Dict, path: str) -> None:
        """
        Compare two dictionaries and queue items for further processing.

        :param source: Dictionary from the source object.
        :param target: Dictionary from the target object.
        :param path: The current path string.
        :return: None
        """
        all_keys = set(source.keys()) | set(target.keys())
        for key in all_keys:
            key_path = f"{path}['{key}']"
            if self._is_excluded(key_path):
                continue
            if key not in source:
                self.changes.append(
                    [key_path, "Not Present", _format_value(target[key])]
                )
            elif key not in target:
                self.changes.append(
                    [key_path, _format_value(source[key]), "Not Present"]
                )
            else:
                # Add to queue for deeper comparison
                self.queue.append((source[key], target[key], key_path))

    def _get_diff_list_hashable(
        self, src: List[Any], tgt: List[Any], path: str
    ) -> None:
        """
        Compare hashable items in unordered lists using Counter.

        :param src: List of hashable items from source.
        :param tgt: List of hashable items from target.
        :param path: The current path string.
        :return: None
        """
        src_counts, tgt_counts = Counter(src), Counter(tgt)

        # Report items unique to source
        for item, count in (src_counts - tgt_counts).items():
            for _ in range(count):
                self.changes.append([f"{path}[?]", _format_value(item), "Not Present"])

        # Report items unique to target
        for item, count in (tgt_counts - src_counts).items():
            for _ in range(count):
                self.changes.append([f"{path}[?]", "Not Present", _format_value(item)])

    def _get_diff_list_unhashable(
        self, src: List[Any], tgt: List[Any], path: str
    ) -> None:
        """
        Compare unhashable items (e.g., dicts, lists) in unordered lists using pairwise comparison.

        Attempts to find a "match" first, then reports closest diffs if no perfect match.

        :param src: List of unhashable items from source.
        :param tgt: List of unhashable items from target.
        :param path: The current path string.
        :return: None
        """
        matched_in_tgt = [False] * len(tgt)

        # Pass 1: look for perfect matches
        for item in src:
            found_match = False
            for j, tgt_item in enumerate(tgt):
                if not matched_in_tgt[j]:
                    sub_changes = DiffUtils(self.exclude_paths, True).diff(
                        item, tgt_item
                    )
                    if not sub_changes:
                        matched_in_tgt[j] = True
                        found_match = True
                        break
            if found_match:
                continue

            # Pass 2: look for best available match (nested diffs)
            for j, tgt_item in enumerate(tgt):
                if not matched_in_tgt[j]:
                    sub_changes = DiffUtils(self.exclude_paths, False).diff(
                        item, tgt_item
                    )
                    for sub_path, val1, val2 in sub_changes:
                        nested_path = sub_path.replace("root", f"{path}[?]")
                        self.changes.append([nested_path, val1, val2])
                    matched_in_tgt[j] = True
                    break
            else:
                # No match found: item missing in target
                self.changes.append([f"{path}[?]", _format_value(item), "Not Present"])

        # Pass 3: items in target missing from source
        for j, tgt_item in enumerate(tgt):
            if not matched_in_tgt[j]:
                self.changes.append(
                    [f"{path}[?]", "Not Present", _format_value(tgt_item)]
                )

    def _get_diff_list_unordered(self, src: List, tgt: List, path: str) -> None:
        """
        Compare two lists, ignoring order.

        :param src: Source list.
        :param tgt: Target list.
        :param path: The current path string.
        :return: None
        """

        def is_simple_hashable(x: Any) -> bool:
            return isinstance(x, (int, str, bool, float, tuple, type(None)))

        src_hash, tgt_hash = [i for i in src if is_simple_hashable(i)], [
            i for i in tgt if is_simple_hashable(i)
        ]
        src_unhash, tgt_unhash = [i for i in src if not is_simple_hashable(i)], [
            i for i in tgt if not is_simple_hashable(i)
        ]

        # 1. Fast diff for hashable items
        self._get_diff_list_hashable(src_hash, tgt_hash, path)

        # 2. Slower pair-wise comparison for unhashable items
        self._get_diff_list_unhashable(src_unhash, tgt_unhash, path)

    def _get_diff_list_ordered(self, src: List, tgt: List, path: str) -> None:
        """
        Compare two lists, considering the order of elements.

        :param src: Source list.
        :param tgt: Target list.
        :param path: The current path string.
        :return: None
        """
        for i in range(max(len(src), len(tgt))):
            item_path = f"{path}[{i}]"
            if i >= len(src):
                self.changes.append([item_path, "Not Present", _format_value(tgt[i])])
            elif i >= len(tgt):
                self.changes.append([item_path, _format_value(src[i]), "Not Present"])
            else:
                # Add matching elements to queue for deeper comparison
                self.queue.append((src[i], tgt[i], item_path))

    def _get_diff_set(self, src: Set, tgt: Set, path: str) -> None:
        """
        Compare two sets and report unique elements in each.

        :param src: Source set.
        :param tgt: Target set.
        :param path: The current path string.
        :return: None
        """
        for item in src - tgt:
            self.changes.append([path, _format_value(item), "Not Present in Set"])
        for item in tgt - src:
            self.changes.append([path, "Not Present in Set", _format_value(item)])

    def diff(self, obj1: Any, obj2: Any) -> List[List[str]]:
        """
        Recursively compare two arbitrary objects (dict, list, set, or primitive).

        :param obj1: Source object.
        :param obj2: Target object.
        :return: List of differences [Path, SourceValue, TargetValue].
        """
        self.changes.clear()
        self.queue.clear()
        self.visited_pairs.clear()

        # Seed the queue with the root objects
        self.queue.append((obj1, obj2, "root"))

        while self.queue:
            src, tgt, path = self.queue.popleft()

            # Circular reference protection
            pair = (id(src), id(tgt))
            if pair in self.visited_pairs:
                continue
            self.visited_pairs.add(pair)

            # Skip comparison for excluded fields
            if self._is_excluded(path):
                continue

            # Type mismatch
            if not isinstance(src, type(tgt)):
                self.changes.append([path, _format_value(src), _format_value(tgt)])
                continue

            # Dispatch based on type
            if isinstance(src, dict):
                self._get_diff_dict(src, tgt, path)
            elif isinstance(src, list):
                if self.ignore_order:
                    self._get_diff_list_unordered(src, tgt, path)
                else:
                    self._get_diff_list_ordered(src, tgt, path)
            elif isinstance(src, set):
                self._get_diff_set(src, tgt, path)
            elif src != tgt:
                # Base case: primitive inequality
                self.changes.append([path, _format_value(src), _format_value(tgt)])

        return self.changes


def get_diff(
    obj1: Union[Dict, List, Set, Any],
    obj2: Union[Dict, List, Set, Any],
    exclude_paths: Union[List[str], Set[str]] = None,
    ignore_order: bool = True,
) -> List[List[str]]:
    """
    Convenience wrapper to run DiffUtils without instantiating directly.

    :param obj1: First object to compare (source).
    :param obj2: Second object to compare (target).
    :param exclude_paths: Optional set of paths to exclude.
    :param ignore_order: If True, lists are compared as unordered collections.
    :return: List of differences [Path, SourceValue, TargetValue].
    """
    return DiffUtils(exclude_paths, ignore_order).diff(obj1, obj2)
