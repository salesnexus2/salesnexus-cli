"""``snx fields`` — manage custom fields (contact & opportunity)."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single

app = typer.Typer(help="Manage custom fields for contacts and opportunities.")

COLUMNS = ["id", "name", "label", "type", "isSystem", "isRequired", "isDropDown", "multiSelect"]

FIELD_TYPES = {
    "character": 0, "currency": 1, "date": 2, "numeric": 3,
    "phone": 4, "time": 5, "checkbox": 6, "percentage": 7, "image": 8,
}


@app.command("list")
def list_fields(
    entity: str = typer.Option("contact", "--entity", "-e", help="Entity type: 'contact' or 'opportunity'."),
) -> None:
    """List all fields for an entity type."""
    from salesnexus_cli.main import ctx

    path = "/api/v1/contact-fields" if entity == "contact" else "/api/v1/opportunity-fields"
    with ctx.client() as client:
        data = client.get(path)
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title=f"{entity.title()} Fields")


@app.command("create")
def create_field(
    entity: str = typer.Option("contact", "--entity", "-e", help="Entity type: 'contact' or 'opportunity'."),
    name: str = typer.Option(..., "--name", "-n", help="Internal field name (required)."),
    label: Optional[str] = typer.Option(None, "--label", "-l", help="Display label."),
    field_type: str = typer.Option("character", "--type", "-t", help="Field type: character, currency, date, numeric, phone, time, checkbox, percentage, image."),
    is_required: bool = typer.Option(False, "--required"),
    is_dropdown: bool = typer.Option(False, "--dropdown"),
    multi_select: bool = typer.Option(False, "--multi-select"),
    default_value: Optional[str] = typer.Option(None, "--default"),
    options: Optional[str] = typer.Option(None, "--options", help="Comma-separated dropdown options."),
) -> None:
    """Create a new custom field."""
    from salesnexus_cli.main import ctx

    type_int = FIELD_TYPES.get(field_type.lower())
    if type_int is None:
        raise typer.BadParameter(f"Unknown field type '{field_type}'. Valid: {', '.join(FIELD_TYPES)}")

    body: dict = {"name": name, "type": type_int}
    if label:
        body["label"] = label
    if is_required:
        body["isRequired"] = True
    if is_dropdown:
        body["isDropDown"] = True
    if multi_select:
        body["multiSelect"] = True
    if default_value:
        body["defaultValue"] = default_value
    if options:
        body["options"] = [o.strip() for o in options.split(",")]

    path = "/api/v1/contact-fields" if entity == "contact" else "/api/v1/opportunity-fields"
    with ctx.client() as client:
        data = client.post(path, json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Field '{name}' created.")
