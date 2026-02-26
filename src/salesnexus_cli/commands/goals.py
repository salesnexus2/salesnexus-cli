"""``snx goals`` — manage goals (pipelines & stages)."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single

app = typer.Typer(help="Manage goals, pipelines, and stages.")

COLUMNS = ["id", "name", "description", "createdBy", "createdAt"]


@app.command("list")
def list_goals(
    page: int = typer.Option(1, "--page"),
    page_size: int = typer.Option(50, "--page-size"),
    sort_by: Optional[str] = typer.Option(None, "--sort-by"),
    sort_desc: bool = typer.Option(False, "--sort-desc"),
) -> None:
    """List all goals."""
    from salesnexus_cli.main import ctx

    params: dict = {"pageNumber": page, "pageSize": page_size}
    if sort_by:
        params["sortBy"] = sort_by
    if sort_desc:
        params["sortDesc"] = True

    with ctx.client() as client:
        data = client.get("/api/v1/goals", params=params)
    rows = data if isinstance(data, list) else data.get("data", [])
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Goals")


@app.command("get")
def get_goal(
    goal_id: int = typer.Argument(..., help="Goal ID."),
) -> None:
    """Get a goal with its pipelines and stages."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/goals/{goal_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_goal(
    name: str = typer.Option(..., "--name", "-n", help="Goal name (required)."),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
) -> None:
    """Create a new goal."""
    from salesnexus_cli.main import ctx

    body: dict = {"name": name}
    if description:
        body["description"] = description

    with ctx.client() as client:
        data = client.post("/api/v1/goals", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Goal {data.get('id')} created.")


@app.command("update")
def update_goal(
    goal_id: int = typer.Argument(..., help="Goal ID."),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
) -> None:
    """Update an existing goal."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/goals/{goal_id}", json=body)
    render_message(f"Goal {goal_id} updated.")


@app.command("delete")
def delete_goal(
    goal_id: int = typer.Argument(..., help="Goal ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a goal."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete goal {goal_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/goals/{goal_id}")
    render_message(f"Goal {goal_id} deleted.")
