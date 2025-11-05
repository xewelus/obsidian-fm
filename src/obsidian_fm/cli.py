"""CLI interface for Obsidian Frontmatter tool."""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml

from .scanner import VaultScanner
from .parser import FrontmatterParser
from .analyzer import DataAnalyzer


# Default vault path
DEFAULT_VAULT_PATH = "~/Documents/Obsidian"

console = Console()


def format_value(value):
    """Format a value for display."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    elif isinstance(value, dict):
        return str(value)
    else:
        return str(value)


def scan_and_analyze(vault_path: str) -> DataAnalyzer:
    """Scan vault and analyze frontmatter.

    Args:
        vault_path: Path to the vault

    Returns:
        Populated DataAnalyzer instance
    """
    try:
        scanner = VaultScanner(vault_path)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    parser = FrontmatterParser()
    analyzer = DataAnalyzer()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning vault...", total=None)

        for file_path in scanner.scan():
            frontmatter = parser.parse_file(file_path)
            analyzer.add_file(file_path, frontmatter)

        progress.update(task, description="Scan complete!")

    return analyzer


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Obsidian Frontmatter CLI - Analyze and manage frontmatter in Obsidian vaults."""
    pass


@main.command()
@click.option(
    '--vault-path',
    default=DEFAULT_VAULT_PATH,
    help='Path to Obsidian vault',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--format',
    type=click.Choice(['yaml', 'table'], case_sensitive=False),
    default='table',
    help='Output format'
)
def stats(vault_path, format):
    """Show statistics for all frontmatter attributes."""
    analyzer = scan_and_analyze(vault_path)

    attr_stats = analyzer.get_attribute_stats()

    if not attr_stats:
        console.print("[yellow]No frontmatter attributes found.[/yellow]")
        return

    # Sort by count (descending)
    sorted_stats = sorted(attr_stats.items(), key=lambda x: x[1], reverse=True)

    if format == 'yaml':
        # Output in pseudo-YAML format
        output = {
            'total_files': analyzer.get_total_files(),
            'files_with_frontmatter': analyzer.get_files_with_frontmatter(),
            'attributes': {attr: count for attr, count in sorted_stats}
        }
        console.print(yaml.dump(output, allow_unicode=True, sort_keys=False))
    else:
        # Output as table
        table = Table(title="Frontmatter Attribute Statistics")
        table.add_column("Attribute", style="cyan")
        table.add_column("Count", style="green", justify="right")

        for attr, count in sorted_stats:
            table.add_row(attr, str(count))

        console.print(f"\nTotal files: {analyzer.get_total_files()}")
        console.print(f"Files with frontmatter: {analyzer.get_files_with_frontmatter()}\n")
        console.print(table)


@main.command()
@click.option(
    '--vault-path',
    default=DEFAULT_VAULT_PATH,
    help='Path to Obsidian vault',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--attribute',
    required=True,
    help='Attribute to query'
)
@click.option(
    '--value',
    default=None,
    help='Filter by specific value (optional)'
)
@click.option(
    '--limit-values',
    type=int,
    default=None,
    help='Max number of attribute values to show'
)
@click.option(
    '--limit-notes',
    type=int,
    default=None,
    help='Max notes to show per attribute value'
)
@click.option(
    '--limit',
    type=int,
    default=None,
    help='Total max notes (when filtering by value)'
)
def list(vault_path, attribute, value, limit_values, limit_notes, limit):
    """List notes and values for a specific attribute."""
    analyzer = scan_and_analyze(vault_path)

    if value is not None:
        # List notes with specific attribute=value
        files = analyzer.get_files_with_attribute(attribute, value, limit)

        if not files:
            console.print(f"[yellow]No notes found with {attribute}={value}[/yellow]")
            return

        console.print(f"\n[bold]Notes with {attribute}={value}[/bold] (Total: {len(files)})\n")
        for file_path in files:
            console.print(f"  - {file_path.relative_to(vault_path)}")

    else:
        # List all values with notes
        value_data = analyzer.get_attribute_values_with_notes(
            attribute, limit_values, limit_notes
        )

        if not value_data:
            console.print(f"[yellow]No values found for attribute '{attribute}'[/yellow]")
            return

        console.print(f"\n[bold]Values for attribute '{attribute}'[/bold]\n")

        for value, (count, notes) in value_data.items():
            console.print(f"\n[cyan]{format_value(value)}[/cyan] ({count} notes):")
            for note_path in notes:
                console.print(f"  - {note_path.relative_to(vault_path)}")
            if limit_notes and count > limit_notes:
                console.print(f"  [dim]... and {count - limit_notes} more[/dim]")


@main.command()
@click.option(
    '--vault-path',
    default=DEFAULT_VAULT_PATH,
    help='Path to Obsidian vault',
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    '--attribute',
    required=True,
    help='Attribute to query'
)
@click.option(
    '--limit',
    type=int,
    default=None,
    help='Max number of values to show'
)
def values(vault_path, attribute, limit):
    """Show possible values for an attribute with count statistics."""
    analyzer = scan_and_analyze(vault_path)

    attr_values = analyzer.get_attribute_values(attribute, limit)

    if not attr_values:
        console.print(f"[yellow]No values found for attribute '{attribute}'[/yellow]")
        return

    table = Table(title=f"Values for '{attribute}'")
    table.add_column("Value", style="cyan")
    table.add_column("Count", style="green", justify="right")

    for value, count in attr_values.items():
        table.add_row(format_value(value), str(count))

    console.print(table)


if __name__ == '__main__':
    main()
