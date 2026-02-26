"""Auto-pagination helper.

When ``--all`` is passed, iterates through every page automatically.
"""

from __future__ import annotations

from typing import Any, Callable


def paginate_all(
    fetch: Callable[..., Any],
    path: str,
    *,
    page_param: str = "page",
    size_param: str = "pageSize",
    page_size: int = 100,
    extra_params: dict | None = None,
    data_key: str = "data",
    total_key: str = "totalItems",
) -> list[dict]:
    """Fetch every page and return the merged list of records.

    ``fetch`` should be a bound :pymethod:`SalesNexusClient.get`.
    """
    all_items: list[dict] = []
    page = 1
    while True:
        params: dict[str, Any] = {page_param: page, size_param: page_size}
        if extra_params:
            params.update(extra_params)
        resp = fetch(path, params=params)

        # Handle both envelope styles:
        #   { data: [], totalItems }   or   plain array
        if isinstance(resp, list):
            items = resp
            all_items.extend(items)
            break  # no pagination metadata → single page
        else:
            items = resp.get(data_key, [])
            all_items.extend(items)
            total = resp.get(total_key, 0)
            if len(all_items) >= total or not items:
                break
        page += 1
    return all_items
