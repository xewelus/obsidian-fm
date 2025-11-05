"""Frontmatter parser module for extracting YAML frontmatter from markdown files."""

from pathlib import Path
from typing import Dict, Any, Optional
import frontmatter


class FrontmatterParser:
    """Parses YAML frontmatter from markdown files."""

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse frontmatter from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary containing frontmatter attributes, or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                # Return metadata as dictionary, or empty dict if no frontmatter
                return dict(post.metadata) if post.metadata else {}
        except (OSError, UnicodeDecodeError):
            # Return None if file can't be read or parsed
            return None
        except Exception:
            # Catch any other exceptions (including parsing errors) to prevent crashes
            return None

    def parse_files(self, file_paths: list[Path]) -> Dict[Path, Optional[Dict[str, Any]]]:
        """Parse frontmatter from multiple markdown files.

        Args:
            file_paths: List of paths to markdown files

        Returns:
            Dictionary mapping file paths to their frontmatter dictionaries
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.parse_file(file_path)
        return results

    @staticmethod
    def normalize_value(value: Any) -> Any:
        """Normalize a frontmatter value for consistent processing.

        Args:
            value: Value to normalize

        Returns:
            Normalized value (converts lists to tuples for hashability, etc.)
        """
        if isinstance(value, list):
            # Convert lists to tuples for hashability
            return tuple(FrontmatterParser.normalize_value(v) for v in value)
        elif isinstance(value, dict):
            # Convert dicts to sorted tuples of key-value pairs
            return tuple(sorted((k, FrontmatterParser.normalize_value(v)) for k, v in value.items()))
        else:
            return value

    @staticmethod
    def denormalize_value(value: Any) -> Any:
        """Denormalize a value back to its original form.

        Args:
            value: Value to denormalize

        Returns:
            Denormalized value (converts tuples back to lists, etc.)
        """
        if isinstance(value, tuple):
            # Check if it's a normalized dict (tuple of tuples with 2 elements)
            if value and all(isinstance(item, tuple) and len(item) == 2 for item in value):
                # Try to reconstruct as dict
                try:
                    return {k: FrontmatterParser.denormalize_value(v) for k, v in value}
                except (TypeError, ValueError):
                    # If that fails, treat as list
                    return [FrontmatterParser.denormalize_value(v) for v in value]
            else:
                # Regular tuple, convert to list
                return [FrontmatterParser.denormalize_value(v) for v in value]
        else:
            return value
