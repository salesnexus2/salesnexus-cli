"""Configuration management — named profiles stored in ~/.salesnexus/config.toml.

Precedence (highest → lowest):
  1. Explicit --api-key / --base-url CLI flags
  2. Environment variables  SALESNEXUS_API_KEY / SALESNEXUS_BASE_URL
  3. Profile entry in config file (selected via --profile or SALESNEXUS_PROFILE)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]

DEFAULT_BASE_URL = "https://api.salesnex.us"
CONFIG_DIR = Path.home() / ".salesnexus"
CONFIG_FILE = CONFIG_DIR / "config.toml"

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _read_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def _write_config(data: dict) -> None:
    _ensure_config_dir()
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(data, f)


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------

def save_profile(
    profile: str,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
) -> None:
    """Persist a named profile to the config file."""
    cfg = _read_config()
    cfg.setdefault("profiles", {})
    cfg["profiles"][profile] = {
        "api_key": api_key,
        "base_url": base_url,
    }
    # Set as active if it's the only profile or if it's "default"
    if profile == "default" or len(cfg["profiles"]) == 1:
        cfg["active_profile"] = profile
    _write_config(cfg)


def delete_profile(profile: str) -> bool:
    """Remove a profile.  Returns True if it existed."""
    cfg = _read_config()
    profiles = cfg.get("profiles", {})
    if profile not in profiles:
        return False
    del profiles[profile]
    if cfg.get("active_profile") == profile:
        cfg["active_profile"] = next(iter(profiles), "")
    _write_config(cfg)
    return True


def list_profiles() -> dict[str, dict]:
    """Return all profiles as {name: {api_key, base_url}}."""
    return _read_config().get("profiles", {})


def get_active_profile_name() -> str:
    cfg = _read_config()
    return cfg.get("active_profile", "default")


def set_active_profile(profile: str) -> None:
    cfg = _read_config()
    if profile not in cfg.get("profiles", {}):
        raise KeyError(f"Profile '{profile}' does not exist.")
    cfg["active_profile"] = profile
    _write_config(cfg)


# ---------------------------------------------------------------------------
# Resolved credentials (respects precedence)
# ---------------------------------------------------------------------------

class ResolvedConfig:
    """Immutable snapshot of the effective API key + base URL."""

    __slots__ = ("api_key", "base_url", "profile")

    def __init__(self, api_key: str, base_url: str, profile: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.profile = profile

    def __repr__(self) -> str:
        masked = self.api_key[:12] + "..." if len(self.api_key) > 12 else "***"
        return f"ResolvedConfig(profile={self.profile!r}, base_url={self.base_url!r}, api_key={masked!r})"


def resolve(
    *,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    profile: Optional[str] = None,
) -> ResolvedConfig:
    """Build a :class:`ResolvedConfig` by merging flags → env → config file."""

    # --- determine profile name ---
    profile_name = (
        profile
        or os.environ.get("SALESNEXUS_PROFILE")
        or get_active_profile_name()
    )

    # --- load profile from file ---
    file_cfg: dict = {}
    profiles = list_profiles()
    if profile_name in profiles:
        file_cfg = profiles[profile_name]

    # --- merge layers ---
    resolved_key = (
        api_key
        or os.environ.get("SALESNEXUS_API_KEY")
        or file_cfg.get("api_key", "")
    )
    resolved_url = (
        base_url
        or os.environ.get("SALESNEXUS_BASE_URL")
        or file_cfg.get("base_url")
        or DEFAULT_BASE_URL
    )

    return ResolvedConfig(
        api_key=resolved_key,
        base_url=resolved_url,
        profile=profile_name,
    )
