"""``snx users`` — list users (read-only)."""

from __future__ import annotations

import typer

from salesnexus_cli.output import render_list, render_single

app = typer.Typer(help="List account users (read-only).")

COLUMNS = ["id", "username", "email", "isActive", "securityLevel"]


@app.command("list")
def list_users() -> None:
    """List all users in the account."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/users")
    rows = data if isinstance(data, list) else []
    render_list(rows, fmt=ctx.fmt, columns=COLUMNS, title="Users")


@app.command("get")
def get_user(
    user_id: int = typer.Argument(..., help="User ID."),
) -> None:
    """Get a single user by ID."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get(f"/api/v1/users/{user_id}")
    render_single(data, fmt=ctx.fmt)
