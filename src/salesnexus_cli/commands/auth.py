"""``snx auth`` — manage API key profiles."""

from __future__ import annotations

from typing import Optional

import typer
from rich.table import Table

from salesnexus_cli import config
from salesnexus_cli.client import SalesNexusClient
from salesnexus_cli.output import console, render_error, render_message

app = typer.Typer(help="Manage authentication profiles.")


@app.command()
def login(
    api_key: str = typer.Option(..., "--api-key", "-k", help="Your SalesNexus API key (sn_live_...)."),
    base_url: str = typer.Option(config.DEFAULT_BASE_URL, "--base-url", "-u", help="API base URL."),
    profile: str = typer.Option("default", "--profile", "-p", help="Profile name to save."),
) -> None:
    """Save an API key to a named profile."""
    if not api_key.startswith("sn_live_"):
        render_error("API key must start with 'sn_live_'.")
        raise typer.Exit(1)
    config.save_profile(profile, api_key, base_url)
    render_message(f"Profile '{profile}' saved.  Base URL: {base_url}")


@app.command()
def status(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to check (default: active)."),
) -> None:
    """Show the active profile and verify connectivity."""
    cfg = config.resolve(profile=profile)
    if not cfg.api_key:
        render_error("No API key configured. Run `snx auth login --api-key <key>` first.")
        raise typer.Exit(1)

    masked = cfg.api_key[:12] + "..." + cfg.api_key[-4:]
    console.print(f"[bold]Profile:[/bold]  {cfg.profile}")
    console.print(f"[bold]Base URL:[/bold] {cfg.base_url}")
    console.print(f"[bold]API Key:[/bold]  {masked}")

    # Ping the API
    try:
        with SalesNexusClient(cfg) as client:
            data = client.get("/api/v1/ping")
        console.print(f"[green]✓[/green] Connected as [bold]{data.get('user', '?')}[/bold]  (account {data.get('accountId', '?')})")
    except Exception as exc:
        render_error(f"Connection failed: {exc}")
        raise typer.Exit(1)


@app.command("switch")
def switch_profile(
    profile: str = typer.Argument(..., help="Profile name to activate."),
) -> None:
    """Set the active profile."""
    try:
        config.set_active_profile(profile)
        render_message(f"Active profile set to '{profile}'.")
    except KeyError:
        render_error(f"Profile '{profile}' does not exist. Available: {', '.join(config.list_profiles())}")
        raise typer.Exit(1)


@app.command("list")
def list_profiles() -> None:
    """List all saved profiles."""
    profiles = config.list_profiles()
    active = config.get_active_profile_name()
    if not profiles:
        console.print("[dim]No profiles configured. Run `snx auth login` to get started.[/dim]")
        return
    table = Table(title="Profiles")
    table.add_column("Name", style="bold")
    table.add_column("Base URL")
    table.add_column("API Key")
    table.add_column("Active")
    for name, data in profiles.items():
        key = data.get("api_key", "")
        masked = key[:12] + "..." + key[-4:] if len(key) > 16 else "***"
        marker = "✓" if name == active else ""
        table.add_row(name, data.get("base_url", ""), masked, marker)
    console.print(table)


@app.command()
def logout(
    profile: str = typer.Option("default", "--profile", "-p", help="Profile to remove."),
) -> None:
    """Remove a saved profile."""
    if config.delete_profile(profile):
        render_message(f"Profile '{profile}' removed.")
    else:
        render_error(f"Profile '{profile}' not found.")
        raise typer.Exit(1)
