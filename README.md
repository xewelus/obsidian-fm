# Obsidian Frontmatter CLI

A powerful CLI tool for analyzing and managing YAML frontmatter in Obsidian vaults.

## Features

- 📊 **Statistics**: View usage counts for all frontmatter attributes
- 🔍 **Search**: Find notes by attribute and value
- 📈 **Analysis**: Analyze value distributions across your vault
- ⚡ **Fast**: Efficient scanning designed for large vaults
- 🎨 **Beautiful**: Rich terminal output with tables and colors
- 🧪 **Tested**: Comprehensive test suite with 21 passing tests

## Installation

```bash
# Clone the repository
cd obsidian-notes

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start

```bash
# Show statistics for all frontmatter attributes
obsidian-fm stats

# Show stats in YAML format
obsidian-fm stats --format yaml

# List all values for the "status" attribute
obsidian-fm values --attribute status

# Find all notes with status=draft
obsidian-fm list --attribute status --value draft

# Show top 10 tag values
obsidian-fm values --attribute tags --limit 10
```

## Commands

### `stats`
Show statistics for all frontmatter attributes in your vault.

**Options**:
- `--vault-path`: Path to Obsidian vault (default: `~/Documents/Obsidian`)
- `--format [yaml|table]`: Output format (default: `table`)

**Example**:
```bash
obsidian-fm stats --format yaml
```

### `list`
List notes and values for a specific attribute.

**Options**:
- `--vault-path`: Path to Obsidian vault
- `--attribute` (required): Attribute to query
- `--value`: Filter by specific value
- `--limit-values`: Max number of values to show
- `--limit-notes`: Max notes to show per value
- `--limit`: Total max notes (when filtering by value)

**Examples**:
```bash
# List all notes with status=published
obsidian-fm list --attribute status --value published

# Show all tag values with up to 5 notes each
obsidian-fm list --attribute tags --limit-notes 5

# Show top 3 categories with up to 10 notes each
obsidian-fm list --attribute category --limit-values 3 --limit-notes 10
```

### `values`
Show possible values for an attribute with count statistics.

**Options**:
- `--vault-path`: Path to Obsidian vault
- `--attribute` (required): Attribute to query
- `--limit`: Max number of values to show

**Example**:
```bash
# Show top 20 most used tags
obsidian-fm values --attribute tags --limit 20
```

## Configuration

### Default Vault Path
By default, the tool uses: `~/Documents/Obsidian`

Override with `--vault-path` on any command:
```bash
obsidian-fm stats --vault-path /path/to/your/vault
```

### Skipped Directories
The scanner automatically skips:
- `.obsidian`
- `.trash`
- `.git`
- `__pycache__`
- `node_modules`
- Any directory starting with `.`

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=obsidian_fm
```

### Project Structure
```
obsidian-notes/
├── src/obsidian_fm/     # Main package
│   ├── scanner.py       # Vault scanning
│   ├── parser.py        # Frontmatter parsing
│   ├── analyzer.py      # Data analysis
│   └── cli.py           # CLI interface
├── tests/               # Test suite
├── docs/                # Documentation
│   └── SPECS.md        # Technical specifications
└── pyproject.toml      # Package configuration
```

## Documentation

- [Technical Specifications](docs/SPECS.md)
- [Implementation Report](ai/reports/2025-11-05%20frontmatter%20implementation.md)

## Requirements

- Python 3.8+
- Dependencies:
  - click >= 8.1.0
  - python-frontmatter >= 1.0.0
  - PyYAML >= 6.0
  - rich >= 13.0.0

## License

This project is for personal use.

## Version

Current version: 0.1.0
