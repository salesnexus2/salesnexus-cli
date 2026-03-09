"""``snx transcripts`` — read call transcripts."""

from __future__ import annotations

from typing import Any, Optional

import typer

from salesnexus_cli.output import render_list, render_single

app = typer.Typer(help="Read call transcripts.")

COLUMNS = ["id", "contactId", "userId", "provider", "status", "durationSeconds", "createdAt"]


def _extract_page(payload: Any, *, headers: dict[str, str], page: int, page_size: int) -> tuple[list[dict], int, int, int]:
    """Normalize transcript list responses from either body or headers."""
    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            pagination = payload.get("pagination") or {}
            total = (
                pagination.get("totalCount")
                or pagination.get("totalItems")
                or payload.get("totalItems")
                or len(payload["data"])
            )
            current_page = pagination.get("pageNumber") or payload.get("page") or page
            current_size = pagination.get("pageSize") or payload.get("pageSize") or page_size
            return payload["data"], int(total), int(current_page), int(current_size)

    items = payload if isinstance(payload, list) else []
    total = int(headers.get("X-Total-Count", len(items)))
    current_page = int(headers.get("X-Page", page))
    current_size = int(headers.get("X-Page-Size", page_size))
    return items, total, current_page, current_size


def _fetch_page(client: Any, *, params: dict[str, Any]) -> tuple[list[dict], int, int, int]:
    response = client.get_response("/api/v1/calltranscripts", params=params)
    payload = response.json()
    return _extract_page(
        payload,
        headers=dict(response.headers),
        page=int(params.get("page", 1)),
        page_size=int(params.get("pageSize", 20)),
    )


@app.command("list")
def list_transcripts(
    page: int = typer.Option(1, "--page", help="Page number."),
    page_size: int = typer.Option(20, "--page-size", help="Results per page (max 100)."),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", help="Filter by contact ID."),
    user_id: Optional[int] = typer.Option(None, "--user-id", help="Filter by user / agent ID."),
    provider: Optional[str] = typer.Option(None, "--provider", help="Filter by provider (e.g. RingCentral, zoom_phone)."),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (processing, completed, failed)."),
    from_value: Optional[str] = typer.Option(None, "--from", help="Created-at lower bound (ISO 8601)."),
    to_value: Optional[str] = typer.Option(None, "--to", help="Created-at upper bound (ISO 8601)."),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search transcript text."),
    all_pages: bool = typer.Option(False, "--all", "-a", help="Fetch all pages."),
) -> None:
    """List call transcripts with optional filters."""
    from salesnexus_cli.main import ctx

    params: dict[str, Any] = {"page": page, "pageSize": page_size}
    if contact_id is not None:
        params["contactId"] = contact_id
    if user_id is not None:
        params["userId"] = user_id
    if provider:
        params["provider"] = provider
    if status:
        params["status"] = status
    if from_value:
        params["from"] = from_value
    if to_value:
        params["to"] = to_value
    if search:
        params["search"] = search

    with ctx.client() as client:
        if all_pages:
            items: list[dict] = []
            current_page = page
            total = 0
            while True:
                params["page"] = current_page
                page_items, total, _, resolved_size = _fetch_page(client, params=params)
                if not page_items:
                    break
                items.extend(page_items)
                if len(items) >= total or len(page_items) < resolved_size:
                    break
                current_page += 1
            render_list(items, fmt=ctx.fmt, columns=COLUMNS, title="Call Transcripts", total=total or len(items))
        else:
            items, total, resolved_page, resolved_size = _fetch_page(client, params=params)
            render_list(
                items,
                fmt=ctx.fmt,
                columns=COLUMNS,
                title="Call Transcripts",
                total=total,
                page=resolved_page,
                page_size=resolved_size,
            )


@app.command("get")
def get_transcript(
    transcript_id: int = typer.Argument(..., help="Call transcript ID."),
) -> None:
    """Get a single call transcript by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/calltranscripts/{transcript_id}")
    render_single(data, fmt=ctx.fmt)