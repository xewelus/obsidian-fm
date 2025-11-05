"""Vault scanner module for traversing Obsidian vault directories."""

from pathlib import Path
from typing import Iterator, Set


class VaultScanner:
    """Scans an Obsidian vault directory for markdown files."""

    # Directories to skip during scanning
    SKIP_DIRS: Set[str] = {'.obsidian', '.trash', '.git', '__pycache__', 'node_modules'}

    def __init__(self, vault_path: str):
        """Initialize the scanner with a vault path.

        Args:
            vault_path: Path to the Obsidian vault directory

        Raises:
            ValueError: If vault_path doesn't exist or is not a directory
        """
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")
        if not self.vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault_path}")

    def scan(self) -> Iterator[Path]:
        """Scan the vault for markdown files.

        Yields:
            Path objects for each markdown file found
        """
        yield from self._scan_directory(self.vault_path)

    def _scan_directory(self, directory: Path) -> Iterator[Path]:
        """Recursively scan a directory for markdown files.

        Args:
            directory: Directory to scan

        Yields:
            Path objects for each markdown file found
        """
        try:
            for item in directory.iterdir():
                # Skip hidden files and configured directories
                if item.name.startswith('.') or item.name in self.SKIP_DIRS:
                    continue

                if item.is_dir():
                    # Recursively scan subdirectories
                    yield from self._scan_directory(item)
                elif item.is_file() and item.suffix.lower() in ['.md', '.markdown']:
                    yield item
        except PermissionError:
            # Skip directories we don't have permission to read
            pass

    def count_files(self) -> int:
        """Count the total number of markdown files in the vault.

        Returns:
            Number of markdown files
        """
        return sum(1 for _ in self.scan())
