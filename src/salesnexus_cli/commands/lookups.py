"""``snx lookups`` — manage lookups, segments, and layouts."""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli.output import render_list, render_message, render_single

app = typer.Typer(help="Manage lookups, segments, and layouts.")

# ── Lookups ──────────────────────────────────────────────────────────────

LOOKUP_COLUMNS = ["id", "name", "segmentId", "layoutId"]


@app.command("list")
def list_lookups() -> None:
    """List all lookups."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/lookups")
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=LOOKUP_COLUMNS, title="Lookups")


@app.command("get")
def get_lookup(
    lookup_id: int = typer.Argument(..., help="Lookup ID."),
) -> None:
    """Get a single lookup."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/lookups/{lookup_id}")
    render_single(data, fmt=ctx.fmt)


@app.command("create")
def create_lookup(
    name: str = typer.Option(..., "--name", "-n", help="Lookup name (required)."),
    segment_id: Optional[int] = typer.Option(None, "--segment-id"),
    layout_id: Optional[int] = typer.Option(None, "--layout-id"),
) -> None:
    """Create a new lookup."""
    from salesnexus_cli.main import ctx

    body: dict = {"name": name}
    if segment_id is not None:
        body["segmentId"] = segment_id
    if layout_id is not None:
        body["layoutId"] = layout_id

    with ctx.client() as client:
        data = client.post("/api/v1/lookups", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Lookup {data.get('id')} created.")


# ── Segments ─────────────────────────────────────────────────────────────

segments_app = typer.Typer(help="Manage segments within lookups.")
app.add_typer(segments_app, name="segments")

SEGMENT_COLUMNS = ["id", "name"]


@segments_app.command("list")
def list_segments() -> None:
    """List all segments."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/lookups/segments")
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=SEGMENT_COLUMNS, title="Segments")


@segments_app.command("get")
def get_segment(
    segment_id: int = typer.Argument(..., help="Segment ID."),
) -> None:
    """Get a single segment."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/lookups/segments/{segment_id}")
    render_single(data, fmt=ctx.fmt)


@segments_app.command("create")
def create_segment(
    name: str = typer.Option(..., "--name", "-n"),
    spec: Optional[str] = typer.Option(None, "--spec", help="Segment spec as JSON string."),
) -> None:
    """Create a new segment."""
    from salesnexus_cli.main import ctx
    import json as _json

    body: dict = {"name": name}
    if spec:
        body.update(_json.loads(spec))

    with ctx.client() as client:
        data = client.post("/api/v1/lookups/segments", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Segment {data.get('id')} created.")


@segments_app.command("update")
def update_segment(
    segment_id: int = typer.Argument(..., help="Segment ID."),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    spec: Optional[str] = typer.Option(None, "--spec", help="Full segment spec as JSON string."),
) -> None:
    """Update a segment."""
    from salesnexus_cli.main import ctx
    import json as _json

    body: dict = {}
    if name is not None:
        body["name"] = name
    if spec:
        body.update(_json.loads(spec))
    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/lookups/segments/{segment_id}", json=body)
    render_message(f"Segment {segment_id} updated.")


# ── Layouts ──────────────────────────────────────────────────────────────

layouts_app = typer.Typer(help="Manage layouts within lookups.")
app.add_typer(layouts_app, name="layouts")

LAYOUT_COLUMNS = ["id", "name"]


@layouts_app.command("list")
def list_layouts() -> None:
    """List all layouts."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/lookups/layouts")
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=LAYOUT_COLUMNS, title="Layouts")


@layouts_app.command("get")
def get_layout(
    layout_id: int = typer.Argument(..., help="Layout ID."),
) -> None:
    """Get a single layout."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/lookups/layouts/{layout_id}")
    render_single(data, fmt=ctx.fmt)


@layouts_app.command("create")
def create_layout(
    name: str = typer.Option(..., "--name", "-n"),
    spec: Optional[str] = typer.Option(None, "--spec", help="Layout spec as JSON string."),
) -> None:
    """Create a new layout."""
    from salesnexus_cli.main import ctx
    import json as _json

    body: dict = {"name": name}
    if spec:
        body.update(_json.loads(spec))

    with ctx.client() as client:
        data = client.post("/api/v1/lookups/layouts", json=body)
    render_single(data, fmt=ctx.fmt)
    render_message(f"Layout {data.get('id')} created.")


@layouts_app.command("update")
def update_layout(
    layout_id: int = typer.Argument(..., help="Layout ID."),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    spec: Optional[str] = typer.Option(None, "--spec", help="Layout spec as JSON string."),
) -> None:
    """Update a layout."""
    from salesnexus_cli.main import ctx
    import json as _json

    body: dict = {}
    if name is not None:
        body["name"] = name
    if spec:
        body.update(_json.loads(spec))
    if not body:
        render_message("Nothing to update.", style="yellow")
        return

    with ctx.client() as client:
        client.put(f"/api/v1/lookups/layouts/{layout_id}", json=body)
    render_message(f"Layout {layout_id} updated.")
