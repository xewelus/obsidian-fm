"""Tests for VaultScanner."""

import pytest
from pathlib import Path
from obsidian_fm.scanner import VaultScanner


def test_vault_scanner_init_invalid_path():
    """Test that VaultScanner raises error for invalid path."""
    with pytest.raises(ValueError):
        VaultScanner("/nonexistent/path/to/vault")


def test_vault_scanner_init_file_path(tmp_path):
    """Test that VaultScanner raises error when path is a file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    with pytest.raises(ValueError):
        VaultScanner(str(test_file))


def test_vault_scanner_scan_empty(tmp_path):
    """Test scanning an empty directory."""
    scanner = VaultScanner(str(tmp_path))
    files = list(scanner.scan())
    assert len(files) == 0


def test_vault_scanner_scan_with_files(tmp_path):
    """Test scanning a directory with markdown files."""
    # Create test files
    (tmp_path / "note1.md").write_text("# Note 1")
    (tmp_path / "note2.markdown").write_text("# Note 2")
    (tmp_path / "other.txt").write_text("Not a markdown file")

    scanner = VaultScanner(str(tmp_path))
    files = list(scanner.scan())

    assert len(files) == 2
    assert all(f.suffix.lower() in ['.md', '.markdown'] for f in files)


def test_vault_scanner_skip_dirs(tmp_path):
    """Test that scanner skips configured directories."""
    # Create skip directories
    obsidian_dir = tmp_path / ".obsidian"
    obsidian_dir.mkdir()
    (obsidian_dir / "config.json").write_text("{}")

    # Create regular file
    (tmp_path / "note.md").write_text("# Note")

    scanner = VaultScanner(str(tmp_path))
    files = list(scanner.scan())

    assert len(files) == 1
    assert files[0].name == "note.md"


def test_vault_scanner_recursive(tmp_path):
    """Test recursive scanning of subdirectories."""
    # Create nested structure
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (tmp_path / "note1.md").write_text("# Note 1")
    (subdir / "note2.md").write_text("# Note 2")

    scanner = VaultScanner(str(tmp_path))
    files = list(scanner.scan())

    assert len(files) == 2


def test_vault_scanner_count_files(tmp_path):
    """Test file counting."""
    (tmp_path / "note1.md").write_text("# Note 1")
    (tmp_path / "note2.md").write_text("# Note 2")

    scanner = VaultScanner(str(tmp_path))
    count = scanner.count_files()

    assert count == 2
