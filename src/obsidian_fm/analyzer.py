"""Data analyzer module for aggregating frontmatter statistics."""

from pathlib import Path
from typing import Dict, Any, List, Tuple, Set, Optional
from collections import defaultdict
from .parser import FrontmatterParser


class DataAnalyzer:
    """Analyzes frontmatter data and generates statistics."""

    def __init__(self):
        """Initialize the analyzer."""
        self.parser = FrontmatterParser()
        # Store all parsed data: {file_path: {attribute: value}}
        self.data: Dict[Path, Dict[str, Any]] = {}

    def add_file(self, file_path: Path, frontmatter: Optional[Dict[str, Any]]) -> None:
        """Add a file's frontmatter to the analyzer.

        Args:
            file_path: Path to the file
            frontmatter: Frontmatter dictionary (or None if no frontmatter)
        """
        if frontmatter is not None:
            self.data[file_path] = frontmatter

    def get_all_attributes(self) -> Set[str]:
        """Get all unique frontmatter attributes across all files.

        Returns:
            Set of attribute names
        """
        attributes = set()
        for frontmatter in self.data.values():
            attributes.update(frontmatter.keys())
        return attributes

    def get_attribute_stats(self) -> Dict[str, int]:
        """Get statistics for each attribute.

        Returns:
            Dictionary mapping attribute names to count of notes using them
        """
        stats = defaultdict(int)
        for frontmatter in self.data.values():
            for attr in frontmatter.keys():
                stats[attr] += 1
        return dict(stats)

    def get_files_with_attribute(
        self,
        attribute: str,
        value: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[Path]:
        """Get files that have a specific attribute, optionally filtered by value.

        Args:
            attribute: Attribute name to search for
            value: Optional value to filter by
            limit: Maximum number of files to return

        Returns:
            List of file paths
        """
        results = []
        for file_path, frontmatter in self.data.items():
            if attribute in frontmatter:
                if value is None:
                    results.append(file_path)
                else:
                    # Check if value matches
                    fm_value = frontmatter[attribute]
                    if self._values_match(fm_value, value):
                        results.append(file_path)

            if limit and len(results) >= limit:
                break

        return results

    def get_attribute_values(
        self,
        attribute: str,
        limit: Optional[int] = None,
        explode_list: bool = False
    ) -> Dict[Any, int]:
        """Get all unique values for an attribute with counts.

        Args:
            attribute: Attribute name
            limit: Maximum number of values to return
            explode_list: If True and the attribute value is a list, count each
                element as a separate value (useful for tags/refs).

        Returns:
            Dictionary mapping values to count of notes with that value
        """
        value_counts = defaultdict(int)

        for frontmatter in self.data.values():
            if attribute not in frontmatter:
                continue

            value = frontmatter[attribute]

            if explode_list and isinstance(value, list):
                for item in value:
                    # Skip empty / non-countable tokens
                    if item is None:
                        continue
                    if item == "":
                        continue
                    if isinstance(item, list) and len(item) == 0:
                        continue
                    if isinstance(item, dict) and len(item) == 0:
                        continue

                    normalized_item = FrontmatterParser.normalize_value(item)

                    # If normalization yields an empty tuple (e.g., []), ignore
                    if normalized_item == ():
                        continue

                    value_counts[normalized_item] += 1
                continue

            # Default behavior: normalize the whole value for counting
            normalized = FrontmatterParser.normalize_value(value)
            value_counts[normalized] += 1

        # Sort by count (descending) and apply limit
        sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        if limit:
            sorted_values = sorted_values[:limit]

        # IMPORTANT: keep normalized (hashable) values as keys.
        # Denormalizing would turn tuples back into lists/dicts, which are unhashable
        # and crash when used as dict keys (e.g., for `tags`/`refs`).
        return {k: v for k, v in sorted_values}

    def get_child_count(
        self,
        hub_value: Any,
        parent_attribute: str = "parent",
        refs_attribute: str = "refs"
    ) -> int:
        """Compute combined child count for a single hub.

        childCount(hub) = parentCount(hub) + refsCount(hub)

        - parentCount(hub): number of notes with `parent: hub_value`
        - refsCount(hub): number of notes where `refs` (YAML list) contains hub_value

        Note: `hub_value` must match the normalized form used by the analyzer.
        In practice this is usually a string like `[[Hub]]`.

        Returns:
            Total child count (int)
        """
        parent_counts = self.get_attribute_values(parent_attribute, limit=None, explode_list=False)
        refs_counts = self.get_attribute_values(refs_attribute, limit=None, explode_list=True)

        pc = int(parent_counts.get(hub_value, 0))
        rc = int(refs_counts.get(hub_value, 0))
        return pc + rc

    def get_child_counts_total(
        self,
        parent_attribute: str = "parent",
        refs_attribute: str = "refs"
    ) -> Dict[Any, int]:
        """Compute combined child counts for all hubs in one pass.

        Returns a dict:
          hub_value -> (parentCount(hub) + refsCount(hub))

        Keys are in the analyzer's normalized form (typically strings like '[[Hub]]').
        """
        breakdown = self.get_child_counts_breakdown(
            parent_attribute=parent_attribute,
            refs_attribute=refs_attribute,
        )

        totals: Dict[Any, int] = {
            hub: int(parts["total"]) for hub, parts in breakdown.items()
        }

        # Sort by total desc for stable CLI output
        totals_sorted = dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))
        return totals_sorted

    def get_child_counts_breakdown(
        self,
        parent_attribute: str = "parent",
        refs_attribute: str = "refs"
    ) -> Dict[Any, Dict[str, int]]:
        """Compute child count breakdown (parent + refs + total) for all hubs.

        Returns a dict:
          hub_value -> {"parent": n, "refs": m, "total": k}

        Keys are in the analyzer's normalized form.
        """
        parent_counts = self.get_attribute_values(parent_attribute, limit=None, explode_list=False)
        refs_counts = self.get_attribute_values(refs_attribute, limit=None, explode_list=True)

        hubs = set(parent_counts.keys()) | set(refs_counts.keys())
        breakdown: Dict[Any, Dict[str, int]] = {}
        for hub in hubs:
            pc = int(parent_counts.get(hub, 0))
            rc = int(refs_counts.get(hub, 0))
            breakdown[hub] = {
                "parent": pc,
                "refs": rc,
                "total": pc + rc,
            }

        breakdown_sorted = dict(
            sorted(breakdown.items(), key=lambda kv: kv[1]["total"], reverse=True)
        )
        return breakdown_sorted

    def get_attribute_values_with_notes(
        self,
        attribute: str,
        limit_values: Optional[int] = None,
        limit_notes: Optional[int] = None
    ) -> Dict[Any, Tuple[int, List[Path]]]:
        """Get all unique values for an attribute with notes using each value.

        Args:
            attribute: Attribute name
            limit_values: Maximum number of values to return
            limit_notes: Maximum number of notes to return per value

        Returns:
            Dictionary mapping values to (count, list of file paths)
        """
        value_notes = defaultdict(list)

        for file_path, frontmatter in self.data.items():
            if attribute in frontmatter:
                value = frontmatter[attribute]
                # Normalize value for grouping
                normalized = FrontmatterParser.normalize_value(value)
                value_notes[normalized].append(file_path)

        # Sort by count (descending) and apply limits
        sorted_values = sorted(value_notes.items(), key=lambda x: len(x[1]), reverse=True)
        if limit_values:
            sorted_values = sorted_values[:limit_values]

        # Keep normalized (hashable) values as keys.
        result = {}
        for normalized_value, notes in sorted_values:
            if limit_notes:
                notes = notes[:limit_notes]
            result[normalized_value] = (len(value_notes[normalized_value]), notes)

        return result

    def _values_match(self, fm_value: Any, search_value: Any) -> bool:
        """Check if two values match.

        Args:
            fm_value: Value from frontmatter
            search_value: Value to search for

        Returns:
            True if values match
        """
        # Handle list values (check if search_value is in the list)
        if isinstance(fm_value, list):
            return search_value in fm_value
        # Direct comparison
        return fm_value == search_value

    def get_total_files(self) -> int:
        """Get total number of files analyzed.

        Returns:
            Number of files
        """
        return len(self.data)

    def get_files_with_frontmatter(self) -> int:
        """Get count of files that have frontmatter.

        Returns:
            Number of files with frontmatter
        """
        return len([fm for fm in self.data.values() if fm])
