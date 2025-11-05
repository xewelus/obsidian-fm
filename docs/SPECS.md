# Obsidian Frontmatter CLI - Technical Specifications

## Overview

The Obsidian Frontmatter CLI (`obsidian-fm`) is a command-line tool for analyzing and managing YAML frontmatter in Obsidian vaults. It provides efficient scanning, parsing, and statistical analysis of frontmatter attributes across large collections of markdown notes.

## Architecture

### Core Components

#### 1. VaultScanner (`src/obsidian_fm/scanner.py`)

**Purpose**: Traverse Obsidian vault directories to discover markdown files.

**Key Features**:
- Recursive directory traversal
- Automatic skipping of system directories (`.obsidian`, `.trash`, `.git`, etc.)
- Efficient file discovery using `pathlib`
- Graceful handling of permission errors

**Public API**:
- `__init__(vault_path: str)`: Initialize scanner with vault path
- `scan() -> Iterator[Path]`: Yield all markdown files in vault
- `count_files() -> int`: Count total markdown files

**Design Considerations**:
- Generator pattern for memory efficiency (can handle millions of notes)
- Only processes files with `.md` or `.markdown` extensions
- Skips hidden files and configurable system directories

#### 2. FrontmatterParser (`src/obsidian_fm/parser.py`)

**Purpose**: Extract and parse YAML frontmatter from markdown files.

**Key Features**:
- Uses `python-frontmatter` library for robust parsing
- Handles missing or malformed frontmatter gracefully
- Value normalization for hashability and comparison
- Supports complex data types (lists, dicts, dates)

**Public API**:
- `parse_file(file_path: Path) -> Optional[Dict[str, Any]]`: Parse single file
- `parse_files(file_paths: List[Path]) -> Dict[Path, Optional[Dict[str, Any]]]`: Parse multiple files
- `normalize_value(value: Any) -> Any`: Convert values for hashability
- `denormalize_value(value: Any) -> Any`: Convert values back to original form

**Design Considerations**:
- Returns empty dict `{}` for files without frontmatter
- Returns `None` for files that cannot be read or parsed
- Converts lists to tuples for use as dictionary keys
- PyYAML automatically converts date strings to `datetime.date` objects

#### 3. DataAnalyzer (`src/obsidian_fm/analyzer.py`)

**Purpose**: Aggregate and analyze frontmatter data across multiple files.

**Key Features**:
- In-memory data storage and indexing
- Attribute statistics and value counting
- Flexible filtering and limiting
- Support for complex value matching (including list membership)

**Public API**:
- `add_file(file_path: Path, frontmatter: Optional[Dict[str, Any]])`: Add file data
- `get_all_attributes() -> Set[str]`: Get all unique attribute names
- `get_attribute_stats() -> Dict[str, int]`: Get usage counts per attribute
- `get_files_with_attribute(attribute: str, value: Optional[Any], limit: Optional[int]) -> List[Path]`: Find files by attribute/value
- `get_attribute_values(attribute: str, limit: Optional[int]) -> Dict[Any, int]`: Get value distribution
- `get_attribute_values_with_notes(attribute: str, limit_values: Optional[int], limit_notes: Optional[int]) -> Dict[Any, Tuple[int, List[Path]]]`: Get values with file lists
- `get_total_files() -> int`: Count total files
- `get_files_with_frontmatter() -> int`: Count files with frontmatter

**Design Considerations**:
- Stores all data in memory for fast querying
- Sorted results (by count, descending)
- Handles list-valued attributes (e.g., tags)
- Value normalization for accurate counting and grouping

#### 4. CLI Interface (`src/obsidian_fm/cli.py`)

**Purpose**: Provide user-friendly command-line interface.

**Key Features**:
- Built with Click framework
- Rich terminal output with tables and colors
- Progress indicators during scanning
- Multiple output formats (table, YAML)

**Commands**:

##### `stats`
Show statistics for all frontmatter attributes.

**Options**:
- `--vault-path`: Path to Obsidian vault (default: `~/Documents/Obsidian`)
- `--format [yaml|table]`: Output format (default: `table`)

**Output**:
- Total files count
- Files with frontmatter count
- Table/YAML of attributes with usage counts

##### `list`
List notes and values for a specific attribute.

**Options**:
- `--vault-path`: Path to Obsidian vault
- `--attribute` (required): Attribute to query
- `--value`: Filter by specific value
- `--limit-values`: Max number of attribute values to show
- `--limit-notes`: Max notes to show per attribute value
- `--limit`: Total max notes (when filtering by value)

**Behavior**:
- With `--value`: Lists all notes where `attribute=value`
- Without `--value`: Lists all values with their notes grouped

##### `values`
Show possible values for an attribute with count statistics.

**Options**:
- `--vault-path`: Path to Obsidian vault
- `--attribute` (required): Attribute to query
- `--limit`: Max number of values to show

**Output**:
- Table showing each value and its occurrence count
- Sorted by count (descending)

## Data Flow

1. **Scanning Phase**:
   - `VaultScanner` traverses vault directory
   - Yields `Path` objects for each markdown file
   - Skips system directories and non-markdown files

2. **Parsing Phase**:
   - `FrontmatterParser` processes each file
   - Extracts YAML frontmatter into dictionaries
   - Handles errors gracefully (returns `None` or `{}`)

3. **Analysis Phase**:
   - `DataAnalyzer` aggregates all frontmatter data
   - Builds indexes for fast querying
   - Normalizes values for consistent comparison

4. **Output Phase**:
   - CLI formats and displays results
   - Uses Rich library for tables and colors
   - Supports multiple output formats

## Performance Characteristics

### Scalability
- **File Discovery**: O(n) where n = total files in vault
- **Parsing**: O(n × m) where m = average file size
- **Analysis**: O(n × a) where a = average attributes per file
- **Memory**: O(n × a × v) where v = average value size

### Optimizations
- Generator pattern for file scanning (lazy iteration)
- Single-pass processing where possible
- Efficient use of built-in data structures (sets, dicts)
- Optional result limiting to reduce memory usage

### Limitations
- All frontmatter data stored in memory (not suitable for extremely large vaults)
- No persistent caching (rescans on each run)
- Synchronous processing (no parallelization)

## Error Handling

### VaultScanner
- Raises `ValueError` for non-existent or invalid vault paths
- Silently skips directories without read permissions
- Continues on individual file errors

### FrontmatterParser
- Returns `None` for unreadable files
- Returns `{}` for files without frontmatter
- Catches all exceptions to prevent crashes

### DataAnalyzer
- Ignores files with `None` frontmatter
- Handles missing attributes gracefully
- Supports both exact value matching and list membership

### CLI
- Validates vault path before processing
- Provides clear error messages
- Shows progress during scanning
- Exits gracefully on errors

## Configuration

### Default Vault Path
`~/Documents/Obsidian`

Can be overridden with `--vault-path` option on all commands.

### Skipped Directories
- `.obsidian`
- `.trash`
- `.git`
- `__pycache__`
- `node_modules`
- Any directory starting with `.`

### File Extensions
- `.md`
- `.markdown`

## Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Install for production use
pip install .
```

## Usage Examples

```bash
# Show all frontmatter attributes with stats
obsidian-fm stats

# Show stats in YAML format
obsidian-fm stats --format yaml

# List all values for "status" attribute
obsidian-fm values --attribute status

# List notes with status=draft
obsidian-fm list --attribute status --value draft

# Show top 10 values for "tags" attribute
obsidian-fm values --attribute tags --limit 10

# List all tag values with up to 5 notes each
obsidian-fm list --attribute tags --limit-notes 5

# Use custom vault path
obsidian-fm stats --vault-path /path/to/vault
```

## Testing

Test suite located in `tests/` directory.

### Test Coverage
- VaultScanner: 9 tests (initialization, scanning, filtering, counting)
- FrontmatterParser: 5 tests (parsing, normalization, error handling)
- DataAnalyzer: 9 tests (data management, statistics, filtering)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=obsidian_fm

# Run verbose
pytest -v
```

## Dependencies

### Core Dependencies
- `click>=8.1.0`: CLI framework
- `python-frontmatter>=1.0.0`: YAML frontmatter parsing
- `PyYAML>=6.0`: YAML processing
- `rich>=13.0.0`: Terminal formatting and tables

### Development Dependencies
- `pytest>=7.0.0`: Testing framework
- `pytest-cov>=4.0.0`: Coverage reporting

## Future Enhancements

### Potential Features
1. **Caching**: Persistent cache for faster repeated queries
2. **Watch Mode**: Monitor vault for changes and update cache
3. **Export**: Export statistics to JSON/CSV
4. **Filtering**: Advanced query syntax for complex filters
5. **Validation**: Validate frontmatter against schemas
6. **Bulk Updates**: Modify frontmatter across multiple files
7. **Plugins**: Support for custom analyzers and exporters
8. **Performance**: Parallel processing for large vaults
9. **Database**: SQLite backend for very large vaults
10. **Web UI**: Browser-based interface for visualization

### Known Limitations
1. Memory usage grows with vault size
2. No incremental updates (must rescan entire vault)
3. No support for encrypted vaults
4. Limited to YAML frontmatter (no TOML, JSON support)
5. No handling of linked notes or backlinks

## Version History

### v0.1.0 (Initial Release)
- VaultScanner with recursive directory traversal
- FrontmatterParser with robust error handling
- DataAnalyzer with comprehensive statistics
- CLI with `stats`, `list`, and `values` commands
- Full test suite with 21 passing tests
- Rich terminal output with tables and colors
