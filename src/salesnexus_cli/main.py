"""``snx`` — SalesNexus CLI entrypoint.

Global options (--json, --csv, --profile, --api-key) are propagated to
sub-commands via a Typer callback and stored in a module-level context
object so every command can access them.
"""

from __future__ import annotations

from typing import Optional

import typer

from salesnexus_cli import __version__
from salesnexus_cli.client import ApiError, SalesNexusClient
from salesnexus_cli.config import resolve as resolve_config
from salesnexus_cli.output import Format, auto_format, render_error

# ---------------------------------------------------------------------------
# Shared state — populated by the root callback, read by commands
# ---------------------------------------------------------------------------

class _Ctx:
    fmt: str = Format.TABLE
    profile: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None

    @classmethod
    def client(cls) -> SalesNexusClient:
        cfg = resolve_config(api_key=cls.api_key, base_url=cls.base_url, profile=cls.profile)
        if not cfg.api_key:
            render_error("No API key configured. Run `snx auth login --api-key <key>` first.")
            raise typer.Exit(1)
        return SalesNexusClient(cfg)


ctx = _Ctx()

# ---------------------------------------------------------------------------
# Root app
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="snx",
    help="SalesNexus CLI — manage your CRM from the command line.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
)


def _version_callback(value: bool) -> None:
    if value:
        print(f"snx {__version__}")
        raise typer.Exit()


@app.callback()
def root(
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON (default when stdout is not a TTY)."),
    csv_output: bool = typer.Option(False, "--csv", help="Output CSV."),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", envvar="SALESNEXUS_PROFILE", help="Config profile name."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="SALESNEXUS_API_KEY", help="API key override.", hidden=True),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="SALESNEXUS_BASE_URL", help="Base URL override.", hidden=True),
    version: bool = typer.Option(False, "--version", "-v", callback=_version_callback, is_eager=True, help="Show version."),
) -> None:
    # Determine effective output format
    explicit = Format.JSON if json_output else (Format.CSV if csv_output else None)
    ctx.fmt = auto_format(explicit)
    ctx.profile = profile
    ctx.api_key = api_key
    ctx.base_url = base_url


# ---------------------------------------------------------------------------
# Register sub-command groups
# ---------------------------------------------------------------------------

from salesnexus_cli.commands import auth  # noqa: E402
from salesnexus_cli.commands import contacts  # noqa: E402
from salesnexus_cli.commands import documents  # noqa: E402
from salesnexus_cli.commands import fields  # noqa: E402
from salesnexus_cli.commands import forms  # noqa: E402
from salesnexus_cli.commands import goals  # noqa: E402
from salesnexus_cli.commands import lookups  # noqa: E402
from salesnexus_cli.commands import notes  # noqa: E402
from salesnexus_cli.commands import opportunities  # noqa: E402
from salesnexus_cli.commands import ping  # noqa: E402
from salesnexus_cli.commands import reports  # noqa: E402
from salesnexus_cli.commands import tasks  # noqa: E402
from salesnexus_cli.commands import templates  # noqa: E402
from salesnexus_cli.commands import users  # noqa: E402

app.add_typer(auth.app, name="auth")
app.add_typer(contacts.app, name="contacts")
app.add_typer(opportunities.app, name="opps")
app.add_typer(tasks.app, name="tasks")
app.add_typer(notes.app, name="notes")
app.add_typer(goals.app, name="goals")
app.add_typer(fields.app, name="fields")
app.add_typer(templates.app, name="templates")
app.add_typer(reports.app, name="reports")
app.add_typer(lookups.app, name="lookups")
app.add_typer(documents.app, name="docs")
app.add_typer(forms.app, name="forms")
app.add_typer(users.app, name="users")
app.command(name="ping")(ping.ping)


# ---------------------------------------------------------------------------
# Global error handler
# ---------------------------------------------------------------------------

_original_main = app.__call__


def _safe_main(*a, **kw):  # type: ignore[no-untyped-def]
    try:
        return _original_main(*a, **kw)
    except ApiError as exc:
        render_error(str(exc))
        raise typer.Exit(1)


app.__call__ = _safe_main  # type: ignore[method-assign]
