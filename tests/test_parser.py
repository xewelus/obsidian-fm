"""Tests for FrontmatterParser."""

import pytest
from pathlib import Path
from datetime import date
from obsidian_fm.parser import FrontmatterParser


def test_parse_file_with_frontmatter(tmp_path):
    """Test parsing a file with frontmatter."""
    test_file = tmp_path / "test.md"
    content = """---
title: Test Note
tags: [test, example]
created: 2023-01-01
---

# Content here
"""
    test_file.write_text(content)

    parser = FrontmatterParser()
    result = parser.parse_file(test_file)

    assert result is not None
    assert result['title'] == 'Test Note'
    assert result['tags'] == ['test', 'example']
    # PyYAML automatically parses dates as datetime.date objects
    assert result['created'] == date(2023, 1, 1)


def test_parse_file_without_frontmatter(tmp_path):
    """Test parsing a file without frontmatter."""
    test_file = tmp_path / "test.md"
    content = "# Just a regular note\n\nNo frontmatter here."
    test_file.write_text(content)

    parser = FrontmatterParser()
    result = parser.parse_file(test_file)

    assert result == {}


def test_parse_file_invalid_file():
    """Test parsing a non-existent file."""
    parser = FrontmatterParser()
    result = parser.parse_file(Path("/nonexistent/file.md"))

    assert result is None


def test_normalize_value():
    """Test value normalization."""
    # List normalization
    assert FrontmatterParser.normalize_value([1, 2, 3]) == (1, 2, 3)

    # Dict normalization
    normalized = FrontmatterParser.normalize_value({'a': 1, 'b': 2})
    assert isinstance(normalized, tuple)

    # Simple value
    assert FrontmatterParser.normalize_value("test") == "test"


def test_denormalize_value():
    """Test value denormalization."""
    # Tuple to list
    assert FrontmatterParser.denormalize_value((1, 2, 3)) == [1, 2, 3]

    # Simple value
    assert FrontmatterParser.denormalize_value("test") == "test"
