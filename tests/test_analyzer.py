"""Tests for DataAnalyzer."""

import pytest
from pathlib import Path
from obsidian_fm.analyzer import DataAnalyzer


def test_add_file():
    """Test adding files to analyzer."""
    analyzer = DataAnalyzer()
    test_path = Path("test.md")
    frontmatter = {'title': 'Test', 'tags': ['test']}

    analyzer.add_file(test_path, frontmatter)

    assert test_path in analyzer.data
    assert analyzer.data[test_path] == frontmatter


def test_add_file_none_frontmatter():
    """Test that None frontmatter is not added."""
    analyzer = DataAnalyzer()
    test_path = Path("test.md")

    analyzer.add_file(test_path, None)

    assert test_path not in analyzer.data


def test_get_all_attributes():
    """Test getting all unique attributes."""
    analyzer = DataAnalyzer()
    analyzer.add_file(Path("note1.md"), {'title': 'Test', 'tags': ['a']})
    analyzer.add_file(Path("note2.md"), {'title': 'Test2', 'author': 'User'})

    attributes = analyzer.get_all_attributes()

    assert attributes == {'title', 'tags', 'author'}


def test_get_attribute_stats():
    """Test getting attribute statistics."""
    analyzer = DataAnalyzer()
    analyzer.add_file(Path("note1.md"), {'title': 'Test', 'tags': ['a']})
    analyzer.add_file(Path("note2.md"), {'title': 'Test2'})
    analyzer.add_file(Path("note3.md"), {'tags': ['b']})

    stats = analyzer.get_attribute_stats()

    assert stats['title'] == 2
    assert stats['tags'] == 2


def test_get_files_with_attribute():
    """Test getting files with specific attribute."""
    analyzer = DataAnalyzer()
    note1 = Path("note1.md")
    note2 = Path("note2.md")
    note3 = Path("note3.md")

    analyzer.add_file(note1, {'title': 'Test', 'tags': ['a']})
    analyzer.add_file(note2, {'title': 'Test2'})
    analyzer.add_file(note3, {'other': 'value'})

    files = analyzer.get_files_with_attribute('title')

    assert len(files) == 2
    assert note1 in files
    assert note2 in files


def test_get_files_with_attribute_and_value():
    """Test getting files with specific attribute and value."""
    analyzer = DataAnalyzer()
    note1 = Path("note1.md")
    note2 = Path("note2.md")

    analyzer.add_file(note1, {'status': 'draft'})
    analyzer.add_file(note2, {'status': 'published'})

    files = analyzer.get_files_with_attribute('status', 'draft')

    assert len(files) == 1
    assert note1 in files


def test_get_attribute_values():
    """Test getting unique values for attribute."""
    analyzer = DataAnalyzer()
    analyzer.add_file(Path("note1.md"), {'status': 'draft'})
    analyzer.add_file(Path("note2.md"), {'status': 'published'})
    analyzer.add_file(Path("note3.md"), {'status': 'draft'})

    values = analyzer.get_attribute_values('status')

    assert values == {'draft': 2, 'published': 1}


def test_get_total_files():
    """Test getting total file count."""
    analyzer = DataAnalyzer()
    analyzer.add_file(Path("note1.md"), {'title': 'Test'})
    analyzer.add_file(Path("note2.md"), {'title': 'Test2'})

    assert analyzer.get_total_files() == 2


def test_values_match_with_list():
    """Test value matching with list values."""
    analyzer = DataAnalyzer()

    # Test list matching
    assert analyzer._values_match(['a', 'b', 'c'], 'b')
    assert not analyzer._values_match(['a', 'b', 'c'], 'd')

    # Test direct matching
    assert analyzer._values_match('test', 'test')
    assert not analyzer._values_match('test', 'other')
