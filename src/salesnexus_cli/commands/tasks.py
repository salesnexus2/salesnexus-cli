"""``snx tasks`` — manage tasks."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single

app = typer.Typer(help="Manage tasks.")

COLUMNS = ["id", "title", "type", "priority", "status", "dateFrom", "dateTo", "assignedToUserId", "contactId"]


@app.command("list")
def list_tasks(
    page: int = typer.Option(1, "--page"),
    page_size: int = typer.Option(20, "--page-size", help="Results per page (max 200)."),
    scope: str = typer.Option("own", "--scope", help="'own' or 'all'."),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Filter start date (YYYY-MM-DD)."),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="Filter end date (YYYY-MM-DD)."),
) -> None:
    """List tasks with optional date filters."""
    from salesnexus_cli.main import ctx

    params: dict = {"pageNumber": page, "pageSize": page_size, "scope": scope}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    with ctx.client() as client:
        resp = client.get("/api/v1/tasks", params=params)

    # Tasks use ApiResponse envelope
    data_items = resp.get("data", [])
    pagination = resp.get("pagination", {})
    render_list(
        data_items,
        fmt=ctx.fmt,
        columns=COLUMNS,
        title="Tasks",
        total=pagination.get("totalCount"),
        page=pagination.get("pageNumber"),
        page_size=pagination.get("pageSize"),
    )


@app.command("get")
def get_task(
    task_id: int = typer.Argument(..., help="Task ID."),
    scope: str = typer.Option("own", "--scope"),
) -> None:
    """Get a single task by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/tasks/{task_id}", params={"scope": scope})
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_task(
    title: str = typer.Option(..., "--title", "-t", help="Task title (required)."),
    details: Optional[str] = typer.Option(None, "--details", "-d", help="Task details / description."),
    date_from: Optional[str] = typer.Option(None, "--date-from", help="Start date (YYYY-MM-DD or ISO)."),
    date_to: Optional[str] = typer.Option(None, "--date-to", help="End date."),
    type: Optional[str] = typer.Option(None, "--type", help="Task type."),
    priority: Optional[str] = typer.Option(None, "--priority", help="Priority."),
    color: Optional[str] = typer.Option(None, "--color", help="Color."),
    assigned_to: Optional[int] = typer.Option(None, "--assigned-to", help="Assigned user ID."),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", "-c", help="Related contact ID."),
    opportunity_id: Optional[int] = typer.Option(None, "--opportunity-id", "-o", help="Related opportunity ID."),
    group_id: Optional[int] = typer.Option(None, "--group-id", "-g", help="Related group ID."),
) -> None:
    """Create a new task."""
    from salesnexus_cli.main import ctx

    body: dict = {"title": title}
    if details:
        body["details"] = details
    if date_from:
        body["dateFrom"] = date_from
    if date_to:
        body["dateTo"] = date_to
    if type:
        body["type"] = type
    if priority:
        body["priority"] = priority
    if color:
        body["color"] = color
    if assigned_to is not None:
        body["assignedToUserId"] = assigned_to
    if contact_id is not None:
        body["contactId"] = contact_id
    if opportunity_id is not None:
        body["opportunityId"] = opportunity_id
    if group_id is not None:
        body["groupId"] = group_id

    with ctx.client() as client:
        data = client.post("/api/v1/tasks", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Task {data.get('id')} created.")


@app.command("update")
def update_task(
    task_id: int = typer.Argument(..., help="Task ID to update."),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    details: Optional[str] = typer.Option(None, "--details", "-d"),
    date_from: Optional[str] = typer.Option(None, "--date-from"),
    date_to: Optional[str] = typer.Option(None, "--date-to"),
    type: Optional[str] = typer.Option(None, "--type"),
    priority: Optional[str] = typer.Option(None, "--priority"),
    color: Optional[str] = typer.Option(None, "--color"),
    status: Optional[str] = typer.Option(None, "--status"),
    assigned_to: Optional[int] = typer.Option(None, "--assigned-to"),
) -> None:
    """Update an existing task."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if title is not None:
        body["title"] = title
    if details is not None:
        body["details"] = details
    if date_from is not None:
        body["dateFrom"] = date_from
    if date_to is not None:
        body["dateTo"] = date_to
    if type is not None:
        body["type"] = type
    if priority is not None:
        body["priority"] = priority
    if color is not None:
        body["color"] = color
    if status is not None:
        body["status"] = status
    if assigned_to is not None:
        body["assignedToUserId"] = assigned_to

    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/tasks/{task_id}", json=body)
    render_message(f"Task {task_id} updated.")


@app.command("delete")
def delete_task(
    task_id: int = typer.Argument(..., help="Task ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a task."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete task {task_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/tasks/{task_id}")
    render_message(f"Task {task_id} deleted.")
