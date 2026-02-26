"""``snx reports`` — manage reports."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single

app = typer.Typer(help="Manage reports.")

COLUMNS = ["id", "title", "isPublic", "createdAt", "lastRunAt"]


@app.command("list")
def list_reports() -> None:
    """List all reports."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/reports")
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Reports")


@app.command("get")
def get_report(
    report_id: int = typer.Argument(..., help="Report ID."),
) -> None:
    """Get a single report."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/reports/{report_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_report(
    title: str = typer.Option(..., "--title", "-t", help="Report title (required)."),
    spec_json: Optional[str] = typer.Option(None, "--spec", help="Report spec as JSON string."),
    is_public: bool = typer.Option(False, "--public"),
) -> None:
    """Create a new report."""
    from salesnexus_cli.main import ctx
    import json as _json

    body: dict = {"title": title, "isPublic": is_public}
    if spec_json:
        body["specJson"] = spec_json

    with ctx.client() as client:
        data = client.post("/api/v1/reports", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Report {data.get('id')} created.")


@app.command("update")
def update_report(
    report_id: int = typer.Argument(..., help="Report ID."),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    spec_json: Optional[str] = typer.Option(None, "--spec"),
    is_public: Optional[bool] = typer.Option(None, "--public/--private"),
) -> None:
    """Update a report."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if title is not None:
        body["title"] = title
    if spec_json is not None:
        body["specJson"] = spec_json
    if is_public is not None:
        body["isPublic"] = is_public
    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/reports/{report_id}", json=body)
    render_message(f"Report {report_id} updated.")


@app.command("delete")
def delete_report(
    report_id: int = typer.Argument(..., help="Report ID."),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Delete a report."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete report {report_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/reports/{report_id}")
    render_message(f"Report {report_id} deleted.")
