"""Dual output formatter — rich tables for humans, JSON/CSV for machines.

Auto-detects non-TTY stdout and switches to JSON so that AI agents and
pipes get structured data without needing the ``--json`` flag.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from typing import Any, Optional, Sequence

from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Format enum
# ---------------------------------------------------------------------------

class Format:
    JSON = "json"
    TABLE = "table"
    CSV = "csv"


def auto_format(explicit: Optional[str]) -> str:
    """Return the effective output format.

    - If the caller passed ``--json`` or ``--csv``, honour that.
    - Otherwise, if stdout is not a TTY (piped / subprocess), default to JSON.
    - Otherwise, use a rich table.
    """
    if explicit:
        return explicit
    if not sys.stdout.isatty():
        return Format.JSON
    return Format.TABLE


# ---------------------------------------------------------------------------
# Render functions
# ---------------------------------------------------------------------------

def render_json(data: Any) -> None:
    """Print compact JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def render_table(
    rows: Sequence[dict],
    *,
    columns: Optional[list[str]] = None,
    title: Optional[str] = None,
    caption: Optional[str] = None,
) -> None:
    """Render a list of dicts as a rich table."""
    if not rows:
        console.print("[dim]No results.[/dim]")
        return
    cols = columns or list(rows[0].keys())
    table = Table(title=title, caption=caption, show_lines=False)
    for c in cols:
        table.add_column(c, overflow="fold")
    for row in rows:
        table.add_row(*(str(row.get(c, "")) for c in cols))
    console.print(table)


def render_csv(rows: Sequence[dict], *, columns: Optional[list[str]] = None) -> None:
    """Render a list of dicts as CSV to stdout."""
    if not rows:
        return
    cols = columns or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    print(buf.getvalue(), end="")


def render_single(data: dict, *, fmt: str) -> None:
    """Render a single record."""
    if fmt == Format.JSON:
        render_json(data)
    elif fmt == Format.CSV:
        render_csv([data])
    else:
        # Key-value table for a single item
        table = Table(show_header=False, show_lines=False)
        table.add_column("Field", style="bold cyan")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(str(k), str(v) if v is not None else "")
        console.print(table)


def render_list(
    rows: Sequence[dict],
    *,
    fmt: str,
    columns: Optional[list[str]] = None,
    title: Optional[str] = None,
    total: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> None:
    """Render a list of records in the chosen format."""
    if fmt == Format.JSON:
        payload: dict[str, Any] = {"data": rows}
        if total is not None:
            payload["totalItems"] = total
        if page is not None:
            payload["page"] = page
        if page_size is not None:
            payload["pageSize"] = page_size
        render_json(payload)
    elif fmt == Format.CSV:
        render_csv(rows, columns=columns)
    else:
        caption = None
        if total is not None:
            caption = f"Page {page or 1} — {len(rows)} of {total} total"
        render_table(rows, columns=columns, title=title, caption=caption)


def render_message(msg: str, *, style: str = "green") -> None:
    """Print a styled status message to stderr (so it doesn't pollute JSON stdout)."""
    err_console.print(f"[{style}]{msg}[/{style}]")


def render_error(msg: str) -> None:
    """Print an error message to stderr."""
    err_console.print(f"[bold red]Error:[/bold red] {msg}")
