"""``snx notes`` — manage contact/opportunity notes."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single

app = typer.Typer(help="Manage notes.")

COLUMNS = ["id", "contactId", "opportunityId", "noteText", "createdOn", "createdBy"]


@app.command("list")
def list_notes(
    contact_id: Optional[int] = typer.Option(None, "--contact-id", "-c", help="Filter by contact."),
    opportunity_id: Optional[int] = typer.Option(None, "--opportunity-id", "-o", help="Filter by opportunity."),
    page: int = typer.Option(1, "--page"),
    page_size: int = typer.Option(20, "--page-size"),
) -> None:
    """List notes, optionally filtered by contact or opportunity."""
    from salesnexus_cli.main import ctx

    params: dict = {"page": page, "pageSize": page_size}
    if contact_id is not None:
        params["contactId"] = contact_id
    if opportunity_id is not None:
        params["opportunityId"] = opportunity_id

    with ctx.client() as client:
        data = client.get("/api/v1/notes", params=params)

    # Notes return a flat array
    rows = data if isinstance(data, list) else data.get("data", [])
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Notes")


@app.command("get")
def get_note(
    note_id: int = typer.Argument(..., help="Note ID."),
) -> None:
    """Get a single note by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/notes/{note_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_note(
    contact_id: Optional[int] = typer.Option(None, "--contact-id", "-c", help="Contact ID."),
    opportunity_id: Optional[int] = typer.Option(None, "--opportunity-id", "-o", help="Opportunity ID."),
    text: str = typer.Option(..., "--text", "-t", help="Note text (required)."),
) -> None:
    """Create a new note."""
    from salesnexus_cli.main import ctx

    if contact_id is None and opportunity_id is None:
        raise typer.BadParameter("Provide --contact-id or --opportunity-id.")

    body: dict = {"noteText": text}
    if contact_id is not None:
        body["contactId"] = contact_id
    if opportunity_id is not None:
        body["opportunityId"] = opportunity_id

    with ctx.client() as client:
        data = client.post("/api/v1/notes", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Note {data.get('id')} created.")


@app.command("update")
def update_note(
    note_id: int = typer.Argument(..., help="Note ID to update."),
    text: str = typer.Option(..., "--text", "-t", help="Updated note text."),
) -> None:
    """Update note text."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        client.put(f"/api/v1/notes/{note_id}", json={"noteText": text})
    render_message(f"Note {note_id} updated.")


@app.command("delete")
def delete_note(
    note_id: int = typer.Argument(..., help="Note ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a note."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete note {note_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/notes/{note_id}")
    render_message(f"Note {note_id} deleted.")
