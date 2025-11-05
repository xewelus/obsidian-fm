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
        limit: Optional[int] = None
    ) -> Dict[Any, int]:
        """Get all unique values for an attribute with counts.

        Args:
            attribute: Attribute name
            limit: Maximum number of values to return

        Returns:
            Dictionary mapping values to count of notes with that value
        """
        value_counts = defaultdict(int)

        for frontmatter in self.data.values():
            if attribute in frontmatter:
                value = frontmatter[attribute]
                # Normalize value for counting (convert lists to tuples for hashability)
                normalized = FrontmatterParser.normalize_value(value)
                value_counts[normalized] += 1

        # Sort by count (descending) and apply limit
        sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        if limit:
            sorted_values = sorted_values[:limit]

        # Denormalize values for output
        return {FrontmatterParser.denormalize_value(k): v for k, v in sorted_values}

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

        # Denormalize and apply note limit
        result = {}
        for normalized_value, notes in sorted_values:
            denormalized_value = FrontmatterParser.denormalize_value(normalized_value)
            if limit_notes:
                notes = notes[:limit_notes]
            result[denormalized_value] = (len(value_notes[normalized_value]), notes)

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
