"""HTTP client wrapper for the SalesNexus public API.

Handles authentication, retries, error messaging, and response parsing.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Optional

import httpx
from rich.console import Console

from salesnexus_cli.config import ResolvedConfig

err_console = Console(stderr=True)

# Retryable status codes
_RETRYABLE = {429, 502, 503, 504}
_MAX_RETRIES = 3
_BASE_BACKOFF = 1.0  # seconds


class ApiError(Exception):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class SalesNexusClient:
    """Thin synchronous wrapper around *httpx* for the SalesNexus REST API."""

    def __init__(self, cfg: ResolvedConfig, *, timeout: float = 30.0):
        self._cfg = cfg
        self._http = httpx.Client(
            base_url=cfg.base_url,
            headers={
                "X-Api-Key": cfg.api_key,
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Generic request with retries
    # ------------------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[Any] = None,
    ) -> httpx.Response:
        """Send a request, retrying on transient failures."""
        last_exc: Optional[Exception] = None
        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._http.request(method, path, params=params, json=json)
            except httpx.TransportError as exc:
                last_exc = exc
                time.sleep(_BASE_BACKOFF * (2**attempt))
                continue

            if resp.status_code not in _RETRYABLE:
                self._raise_for_status(resp)
                return resp

            # Retryable status — back off
            retry_after = resp.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else _BASE_BACKOFF * (2**attempt)
            time.sleep(delay)
            last_exc = ApiError(resp.status_code, resp.text)

        # Exhausted retries
        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected retry loop exit")

    # ------------------------------------------------------------------
    # Convenience verbs
    # ------------------------------------------------------------------

    def get_response(self, path: str, *, params: Optional[dict] = None) -> httpx.Response:
        """Return the raw GET response after retry/error handling.

        Useful for endpoints that return pagination metadata in headers instead
        of inside the JSON body.
        """
        return self.request("GET", path, params=params)

    def get(self, path: str, *, params: Optional[dict] = None) -> Any:
        return self.request("GET", path, params=params).json()

    def post(self, path: str, *, json: Optional[Any] = None, params: Optional[dict] = None) -> Any:
        resp = self.request("POST", path, json=json, params=params)
        if resp.status_code == 204:
            return None
        return resp.json()

    def put(self, path: str, *, json: Optional[Any] = None) -> None:
        self.request("PUT", path, json=json)

    def delete(self, path: str, *, params: Optional[dict] = None, json: Optional[Any] = None) -> Any:
        resp = self.request("DELETE", path, params=params, json=json)
        if resp.status_code == 204:
            return None
        return resp.json()

    # ------------------------------------------------------------------
    # Error translation
    # ------------------------------------------------------------------

    @staticmethod
    def _raise_for_status(resp: httpx.Response) -> None:
        if resp.is_success:
            return
        code = resp.status_code
        body = resp.text.strip()
        match code:
            case 401:
                detail = "Invalid or expired API key. Run `snx auth login` to configure."
            case 403:
                detail = "Permission denied."
            case 404:
                detail = "Resource not found."
            case 409:
                detail = body or "Conflict."
            case 422:
                detail = body or "Validation error."
            case 429:
                detail = "Rate limit exceeded. Try again later."
            case _:
                detail = body or f"Unexpected error (HTTP {code})."
        raise ApiError(code, detail)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SalesNexusClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
