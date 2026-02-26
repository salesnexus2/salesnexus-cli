"""``snx contacts`` — manage contacts."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import Format, render_list, render_message, render_single
from salesnexus_cli.pagination import paginate_all

app = typer.Typer(help="Manage contacts.")

COLUMNS = ["id", "firstName", "lastName", "email", "phone", "company", "title", "city", "state"]


def _parse_custom_fields(raw: list[str]) -> dict:
    out: dict = {}
    for item in raw:
        if "=" not in item:
            raise typer.BadParameter(f"Custom field must be key=value, got: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


@app.command("list")
def list_contacts(
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(20, "--page-size", help="Results per page (max 100)."),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search contacts by name, email, etc."),
    all_pages: bool = typer.Option(False, "--all", "-a", help="Fetch all pages."),
) -> None:
    """List contacts with optional search and pagination."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        params: dict = {}
        if search:
            params["search"] = search
        if all_pages:
            rows = paginate_all(client.get, "/api/v1/contacts", extra_params=params)
            render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Contacts", total=len(rows))
        else:
            params.update(page=page, pageSize=page_size)
            data = client.get("/api/v1/contacts", params=params)
            render_list(
                data.get("data", []),
                fmt=ctx.fmt,
                columns=COLUMNS,
                title="Contacts",
                total=data.get("totalItems"),
                page=data.get("page"),
                page_size=data.get("pageSize"),
            )


@app.command("get")
def get_contact(
    contact_id: int = typer.Argument(..., help="Contact ID."),
) -> None:
    """Get a single contact by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/contacts/{contact_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_contact(
    first_name: str = typer.Option(..., "--first-name", "-f", help="First name (required)."),
    last_name: Optional[str] = typer.Option(None, "--last-name", "-l", help="Last name."),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address."),
    phone: Optional[str] = typer.Option(None, "--phone", help="Phone number."),
    company: Optional[str] = typer.Option(None, "--company", "-c", help="Company name."),
    title: Optional[str] = typer.Option(None, "--title", help="Job title."),
    address: Optional[str] = typer.Option(None, "--address", help="Street address."),
    city: Optional[str] = typer.Option(None, "--city", help="City."),
    state: Optional[str] = typer.Option(None, "--state", help="State."),
    zip_code: Optional[str] = typer.Option(None, "--zip", help="ZIP / postal code."),
    country: Optional[str] = typer.Option(None, "--country", help="Country."),
    manager_user_id: Optional[int] = typer.Option(None, "--manager-id", help="Assigned manager user ID."),
    custom_field: Optional[list[str]] = typer.Option(None, "--custom-field", "-F", help="Custom field as key=value (repeatable)."),
) -> None:
    """Create a new contact."""
    from salesnexus_cli.main import ctx

    body: dict = {"firstName": first_name}
    if last_name:
        body["lastName"] = last_name
    if email:
        body["email"] = email
    if phone:
        body["phone"] = phone
    if company:
        body["company"] = company
    if title:
        body["title"] = title
    if address:
        body["address"] = address
    if city:
        body["city"] = city
    if state:
        body["state"] = state
    if zip_code:
        body["zip"] = zip_code
    if country:
        body["country"] = country
    if manager_user_id is not None:
        body["managerUserId"] = manager_user_id
    if custom_field:
        body["customFields"] = _parse_custom_fields(custom_field)

    with ctx.client() as client:
        data = client.post("/api/v1/contacts", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Contact {data.get('id')} created.")


@app.command("update")
def update_contact(
    contact_id: int = typer.Argument(..., help="Contact ID to update."),
    first_name: Optional[str] = typer.Option(None, "--first-name", "-f"),
    last_name: Optional[str] = typer.Option(None, "--last-name", "-l"),
    email: Optional[str] = typer.Option(None, "--email", "-e"),
    phone: Optional[str] = typer.Option(None, "--phone"),
    company: Optional[str] = typer.Option(None, "--company", "-c"),
    title: Optional[str] = typer.Option(None, "--title"),
    address: Optional[str] = typer.Option(None, "--address"),
    city: Optional[str] = typer.Option(None, "--city"),
    state: Optional[str] = typer.Option(None, "--state"),
    zip_code: Optional[str] = typer.Option(None, "--zip"),
    country: Optional[str] = typer.Option(None, "--country"),
    manager_user_id: Optional[int] = typer.Option(None, "--manager-id"),
    custom_field: Optional[list[str]] = typer.Option(None, "--custom-field", "-F", help="Custom field as key=value (repeatable)."),
) -> None:
    """Update an existing contact."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if first_name is not None:
        body["firstName"] = first_name
    if last_name is not None:
        body["lastName"] = last_name
    if email is not None:
        body["email"] = email
    if phone is not None:
        body["phone"] = phone
    if company is not None:
        body["company"] = company
    if title is not None:
        body["title"] = title
    if address is not None:
        body["address"] = address
    if city is not None:
        body["city"] = city
    if state is not None:
        body["state"] = state
    if zip_code is not None:
        body["zip"] = zip_code
    if country is not None:
        body["country"] = country
    if manager_user_id is not None:
        body["managerUserId"] = manager_user_id
    if custom_field:
        body["customFields"] = _parse_custom_fields(custom_field)

    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/contacts/{contact_id}", json=body)
    render_message(f"Contact {contact_id} updated.")


@app.command("delete")
def delete_contact(
    contact_id: int = typer.Argument(..., help="Contact ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a contact (soft delete)."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete contact {contact_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/contacts/{contact_id}")
    render_message(f"Contact {contact_id} deleted.")


@app.command("batch-update")
def batch_update(
    ids: Optional[str] = typer.Option(None, "--ids", help="Comma-separated contact IDs."),
    lookup_id: Optional[int] = typer.Option(None, "--lookup-id", help="Lookup ID for selection."),
    field: list[str] = typer.Option(..., "--field", "-F", help="Field update as key=value (repeatable)."),
) -> None:
    """Batch update contacts by IDs or lookup."""
    from salesnexus_cli.main import ctx

    body: dict = {"fieldUpdates": _parse_custom_fields(field)}
    if ids:
        body["selectionMode"] = "ids"
        body["contactIds"] = [int(i.strip()) for i in ids.split(",")]
    elif lookup_id is not None:
        body["selectionMode"] = "lookup"
        body["lookupId"] = lookup_id
    else:
        raise typer.BadParameter("Provide --ids or --lookup-id.")

    with ctx.client() as client:
        data = client.post("/api/v1/contacts/batch-update", json=body)
    if ctx.fmt == Format.JSON:
        from salesnexus_cli.output import render_json
        render_json(data)
    else:
        render_message(f"Batch update complete: {data.get('successCount', 0)} succeeded.")


@app.command("batch-delete")
def batch_delete(
    ids: Optional[str] = typer.Option(None, "--ids", help="Comma-separated contact IDs."),
    lookup_id: Optional[int] = typer.Option(None, "--lookup-id", help="Lookup ID for selection."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Batch delete contacts by IDs or lookup."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if ids:
        body["selectionMode"] = "ids"
        body["contactIds"] = [int(i.strip()) for i in ids.split(",")]
    elif lookup_id is not None:
        body["selectionMode"] = "lookup"
        body["lookupId"] = lookup_id
    else:
        raise typer.BadParameter("Provide --ids or --lookup-id.")

    if not yes:
        typer.confirm("Delete these contacts? This cannot be undone.", abort=True)

    with ctx.client() as client:
        data = client.delete("/api/v1/contacts/batch-delete", json=body)
    if ctx.fmt == Format.JSON:
        from salesnexus_cli.output import render_json
        render_json(data)
    else:
        render_message(f"Batch delete complete: {data.get('deletedCount', 0)} deleted.")
