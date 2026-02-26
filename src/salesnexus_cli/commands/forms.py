"""``snx forms`` — manage web forms."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import Format, render_json, render_list, render_message, render_single

app = typer.Typer(help="Manage web forms.")

COLUMNS = ["id", "name", "slug", "status", "isWiretap", "createdAt"]


@app.command("list")
def list_forms() -> None:
    """List all forms."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/forms")
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Forms")


@app.command("get")
def get_form(
    form_id: int = typer.Argument(..., help="Form ID."),
) -> None:
    """Get a single form."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/forms/{form_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_form(
    name: str = typer.Option(..., "--name", "-n", help="Form name (required)."),
    slug: Optional[str] = typer.Option(None, "--slug"),
    redirect_url: Optional[str] = typer.Option(None, "--redirect-url"),
    settings_json: Optional[str] = typer.Option(None, "--settings", help="Settings as JSON string."),
) -> None:
    """Create a new form."""
    from salesnexus_cli.main import ctx

    body: dict = {"name": name}
    if slug:
        body["slug"] = slug
    if redirect_url:
        body["redirectURL"] = redirect_url
    if settings_json:
        body["settingsJson"] = settings_json

    with ctx.client() as client:
        data = client.post("/api/v1/forms", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Form {data.get('id')} created.")


@app.command("update")
def update_form(
    form_id: int = typer.Argument(..., help="Form ID."),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    slug: Optional[str] = typer.Option(None, "--slug"),
    redirect_url: Optional[str] = typer.Option(None, "--redirect-url"),
    settings_json: Optional[str] = typer.Option(None, "--settings"),
) -> None:
    """Update a form."""
    from salesnexus_cli.main import ctx

    body: dict = {}
    if name is not None:
        body["name"] = name
    if slug is not None:
        body["slug"] = slug
    if redirect_url is not None:
        body["redirectURL"] = redirect_url
    if settings_json is not None:
        body["settingsJson"] = settings_json
    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/forms/{form_id}", json=body)
    render_message(f"Form {form_id} updated.")


@app.command("delete")
def delete_form(
    form_id: int = typer.Argument(..., help="Form ID."),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Delete a form."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete form {form_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/forms/{form_id}")
    render_message(f"Form {form_id} deleted.")


@app.command("embed")
def embed_code(
    form_id: int = typer.Argument(..., help="Form ID."),
) -> None:
    """Get the embed code snippet for a form."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/forms/{form_id}/embed-code")
    if ctx.fmt == Format.JSON:
        render_json(data)
    else:
        render_single(data, fmt=ctx.fmt)


@app.command("unpublish")
def unpublish_form(
    form_id: int = typer.Argument(..., help="Form ID."),
) -> None:
    """Unpublish a form."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        client.post(f"/api/v1/forms/{form_id}/unpublish")
    render_message(f"Form {form_id} unpublished.")
