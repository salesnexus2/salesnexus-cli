"""``snx opps`` — manage opportunities."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import Format, render_json, render_list, render_message, render_single
from salesnexus_cli.pagination import paginate_all

app = typer.Typer(help="Manage opportunities.")

COLUMNS = ["id", "title", "contactId", "goalId", "currentStageId", "amount", "currency", "createdAt"]


def _parse_custom_fields(raw: list[str]) -> dict:
    out: dict = {}
    for item in raw:
        if "=" not in item:
            raise typer.BadParameter(f"Custom field must be key=value, got: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


@app.command("list")
def list_opportunities(
    page: int = typer.Option(1, "--page"),
    page_size: int = typer.Option(20, "--page-size"),
    goal_id: Optional[int] = typer.Option(None, "--goal-id", "-g", help="Filter by goal."),
    stage_id: Optional[int] = typer.Option(None, "--stage-id", help="Filter by stage."),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", "-c", help="Filter by contact."),
    all_pages: bool = typer.Option(False, "--all", "-a", help="Fetch all pages."),
) -> None:
    """List opportunities."""
    from salesnexus_cli.main import ctx

    params: dict = {}
    if goal_id is not None:
        params["goalId"] = goal_id
    if stage_id is not None:
        params["stageId"] = stage_id
    if contact_id is not None:
        params["contactId"] = contact_id

    with ctx.client() as client:
        if all_pages:
            rows = paginate_all(client.get, "/api/v1/opportunities", extra_params=params)
            render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Opportunities", total=len(rows))
        else:
            params.update(page=page, pageSize=page_size)
            data = client.get("/api/v1/opportunities", params=params)
            render_list(
                data.get("data", []),
                fmt=ctx.fmt,
                columns=COLUMNS,
                title="Opportunities",
                total=data.get("totalItems"),
                page=data.get("page"),
                page_size=data.get("pageSize"),
            )


@app.command("get")
def get_opportunity(
    opp_id: int = typer.Argument(..., help="Opportunity ID."),
) -> None:
    """Get a single opportunity by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/opportunities/{opp_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_opportunity(
    contact_id: int = typer.Option(..., "--contact-id", "-c", help="Primary contact ID (required)."),
    goal_id: int = typer.Option(..., "--goal-id", "-g", help="Goal ID (required)."),
    current_stage_id: Optional[int] = typer.Option(None, "--stage-id", help="Initial stage ID."),
    owner_user_id: Optional[int] = typer.Option(None, "--owner-id", help="Owner user ID."),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Opportunity title."),
    amount: Optional[float] = typer.Option(None, "--amount", help="Deal amount."),
    currency: Optional[str] = typer.Option(None, "--currency", help="Currency code (e.g. USD)."),
    custom_field: Optional[list[str]] = typer.Option(None, "--custom-field", "-F", help="Custom field key=value (repeatable)."),
) -> None:
    """Create a new opportunity."""
    from salesnexus_cli.main import ctx

    body: dict = {"contactId": contact_id, "goalId": goal_id}
    if current_stage_id is not None:
        body["currentStageId"] = current_stage_id
    if owner_user_id is not None:
        body["ownerUserId"] = owner_user_id
    if title:
        body["title"] = title
    if amount is not None:
        body["amount"] = amount
    if currency:
        body["currency"] = currency
    if custom_field:
        body["customFields"] = _parse_custom_fields(custom_field)

    with ctx.client() as client:
        data = client.post("/api/v1/opportunities", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Opportunity {data.get('id')} created.")


@app.command("update")
def update_opportunity(
    opp_id: int = typer.Argument(..., help="Opportunity ID to update."),
    current_stage_id: Optional[int] = typer.Option(None, "--stage-id"),
    owner_user_id: Optional[int] = typer.Option(None, "--owner-id"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    amount: Optional[float] = typer.Option(None, "--amount"),
    currency: Optional[str] = typer.Option(None, "--currency"),
    custom_field: Optional[list[str]] = typer.Option(None, "--custom-field", "-F", help="Custom field key=value (repeatable)."),
) -> None:
    """Update an existing opportunity."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if current_stage_id is not None:
        body["currentStageId"] = current_stage_id
    if owner_user_id is not None:
        body["ownerUserId"] = owner_user_id
    if title is not None:
        body["title"] = title
    if amount is not None:
        body["amount"] = amount
    if currency is not None:
        body["currency"] = currency
    if custom_field:
        body["customFields"] = _parse_custom_fields(custom_field)

    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/opportunities/{opp_id}", json=body)
    render_message(f"Opportunity {opp_id} updated.")


@app.command("delete")
def delete_opportunity(
    opp_id: int = typer.Argument(..., help="Opportunity ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete an opportunity."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete opportunity {opp_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/opportunities/{opp_id}")
    render_message(f"Opportunity {opp_id} deleted.")


@app.command("batch-update")
def batch_update(
    ids: str = typer.Option(..., "--ids", help="Comma-separated opportunity IDs."),
    field: list[str] = typer.Option(..., "--field", "-F", help="Field update as key=value (repeatable)."),
) -> None:
    """Batch update opportunities."""
    from salesnexus_cli.main import ctx

    body = {
        "opportunityIds": [int(i.strip()) for i in ids.split(",")],
        "fieldUpdates": _parse_custom_fields(field),
    }
    with ctx.client() as client:
        data = client.post("/api/v1/opportunities/batch-update", json=body)
    if ctx.fmt == Format.JSON:
        render_json(data)
    else:
        render_message(f"Batch update complete: {data.get('successCount', 0)} succeeded.")


@app.command("batch-delete")
def batch_delete(
    ids: str = typer.Option(..., "--ids", help="Comma-separated opportunity IDs."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Batch delete opportunities."""
    from salesnexus_cli.main import ctx

    id_list = [int(i.strip()) for i in ids.split(",")]
    if not yes:
        typer.confirm(f"Delete {len(id_list)} opportunities?", abort=True)
    with ctx.client() as client:
        data = client.delete("/api/v1/opportunities/batch-delete", json={"opportunityIds": id_list})
    if ctx.fmt == Format.JSON:
        render_json(data)
    else:
        render_message(f"Batch delete complete: {data.get('deletedCount', 0)} deleted.")
