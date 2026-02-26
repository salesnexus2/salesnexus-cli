"""``snx docs`` — manage documents."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single
from salesnexus_cli.pagination import paginate_all

app = typer.Typer(help="Manage documents.")

COLUMNS = ["id", "originalFileName", "mime", "size", "contactId", "groupId", "opportunityId", "createdAt"]


@app.command("list")
def list_documents(
    page: int = typer.Option(1, "--page"),
    page_size: int = typer.Option(20, "--page-size"),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", "-c"),
    group_id: Optional[int] = typer.Option(None, "--group-id", "-g"),
    opportunity_id: Optional[int] = typer.Option(None, "--opportunity-id", "-o"),
    scope: str = typer.Option("own", "--scope"),
    all_pages: bool = typer.Option(False, "--all", "-a", help="Fetch all pages."),
) -> None:
    """List documents."""
    from salesnexus_cli.main import ctx

    params: dict = {"scope": scope}
    if contact_id is not None:
        params["contactId"] = contact_id
    if group_id is not None:
        params["groupId"] = group_id
    if opportunity_id is not None:
        params["opportunityId"] = opportunity_id

    with ctx.client() as client:
        if all_pages:
            rows = paginate_all(client.get, "/api/v1/documents", extra_params=params)
            render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Documents", total=len(rows))
        else:
            params.update(page=page, pageSize=page_size)
            data = client.get("/api/v1/documents", params=params)
            render_list(
                data.get("data", []),
                fmt=ctx.fmt,
                columns=COLUMNS,
                title="Documents",
                total=data.get("totalItems"),
                page=data.get("page"),
                page_size=data.get("pageSize"),
            )


@app.command("get")
def get_document(
    doc_id: int = typer.Argument(..., help="Document ID."),
    scope: str = typer.Option("own", "--scope"),
) -> None:
    """Get a single document by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/documents/{doc_id}", params={"scope": scope})
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_document(
    url: str = typer.Option(..., "--url", help="URL of the document to import (required)."),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", "-c"),
    group_id: Optional[int] = typer.Option(None, "--group-id", "-g"),
    opportunity_id: Optional[int] = typer.Option(None, "--opportunity-id", "-o"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags."),
) -> None:
    """Create a document from a URL."""
    from salesnexus_cli.main import ctx

    body: dict = {"sourceUrl": url}
    if description:
        body["description"] = description
    if contact_id is not None:
        body["contactId"] = contact_id
    if group_id is not None:
        body["groupId"] = group_id
    if opportunity_id is not None:
        body["opportunityId"] = opportunity_id
    if tags:
        body["tags"] = tags

    with ctx.client() as client:
        data = client.post("/api/v1/documents/from-url", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Document {data.get('id')} created.")


@app.command("delete")
def delete_document(
    doc_id: int = typer.Argument(..., help="Document ID."),
    scope: str = typer.Option("own", "--scope"),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Delete a document."""
    from salesnexus_cli.main import ctx

    if not yes:
        typer.confirm(f"Delete document {doc_id}?", abort=True)
    with ctx.client() as client:
        client.delete(f"/api/v1/documents/{doc_id}", params={"scope": scope})
    render_message(f"Document {doc_id} deleted.")
