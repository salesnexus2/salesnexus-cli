"""``snx templates`` — manage email templates / campaigns."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import Format, render_json, render_list, render_message, render_single

app = typer.Typer(help="Manage email templates.")

COLUMNS = ["id", "name", "status", "mode", "objective", "segmentId", "createdAt"]


@app.command("list")
def list_templates(
    sort_by: Optional[str] = typer.Option(None, "--sort-by"),
    sort_desc: bool = typer.Option(False, "--sort-desc"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Filter by mode: bulk, triggered."),
) -> None:
    """List email templates."""
    from salesnexus_cli.main import ctx

    params: dict = {}
    if sort_by:
        params["sortBy"] = sort_by
    if sort_desc:
        params["sortDesc"] = True
    if mode:
        params["mode"] = mode

    with ctx.client() as client:
        data = client.get("/api/v1/templates", params=params)
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Templates")


@app.command("get")
def get_template(
    template_id: int = typer.Argument(..., help="Template ID."),
) -> None:
    """Get a single template."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/templates/{template_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("stats")
def template_stats(
    template_id: int = typer.Argument(..., help="Template ID."),
) -> None:
    """Get send/open/click statistics for a template."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/templates/{template_id}/statistics")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_template(
    name: str = typer.Option(..., "--name", "-n", help="Template name (required)."),
    objective: Optional[str] = typer.Option(None, "--objective"),
    mode: str = typer.Option("bulk", "--mode", help="bulk or triggered."),
    segment_id: Optional[int] = typer.Option(None, "--segment-id"),
) -> None:
    """Create a new email template."""
    from salesnexus_cli.main import ctx

    body: dict = {"name": name, "mode": mode}
    if objective:
        body["objective"] = objective
    if segment_id is not None:
        body["segmentId"] = segment_id

    with ctx.client() as client:
        data = client.post("/api/v1/templates", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Template {data.get('id')} created.")


@app.command("update")
def update_template(
    template_id: int = typer.Argument(..., help="Template ID."),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    objective: Optional[str] = typer.Option(None, "--objective"),
    status: Optional[str] = typer.Option(None, "--status"),
) -> None:
    """Update a template."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if name is not None:
        body["name"] = name
    if objective is not None:
        body["objective"] = objective
    if status is not None:
        body["status"] = status
    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/templates/{template_id}", json=body)
    render_message(f"Template {template_id} updated.")


@app.command("delete")
def delete_template(
    template_id: int = typer.Argument(..., help="Template ID."),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Delete a template."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete template {template_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/templates/{template_id}")
    render_message(f"Template {template_id} deleted.")
