"""``snx ping`` — verify API connectivity."""

from __future__ import annotations

import typer

from salesnexus_cli.output import Format, render_json, render_message


def ping() -> None:
    """Verify API connectivity and show current user info."""
    from salesnexus_cli.main import ctx

    with ctx.client() as client:
        data = client.get("/api/v1/ping")
    if ctx.fmt == Format.JSON:
        render_json(data)
    else:
        render_message(
            f"Connected as {data.get('user', '?')} (account {data.get('accountId', '?')})"
        )
