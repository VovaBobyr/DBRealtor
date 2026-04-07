"""Paginator for sreality.cz search result pages.

Iterates over paginated search results and collects all listing IDs,
extracting them from the __NEXT_DATA__ JSON embedded in each page.
"""

import json
import math
import re
from typing import Any

import httpx
import structlog

from src.scraper.browser import get_with_retry

log = structlog.get_logger()

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)
_BASE_URL = "https://www.sreality.cz"


def _extract_next_data(html: str) -> dict[str, Any]:
    """Parse __NEXT_DATA__ JSON from an HTML response body."""
    match = _NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("__NEXT_DATA__ script tag not found in page")
    return json.loads(match.group(1))


def _find_search_data(next_data: dict[str, Any]) -> dict[str, Any]:
    """Return the estatesSearch query payload from __NEXT_DATA__."""
    queries = next_data["props"]["pageProps"]["dehydratedState"]["queries"]
    for q in queries:
        key = q.get("queryKey", [])
        if key and key[0] == "estatesSearch":
            data = q["state"]["data"]
            if data is None:
                raise ValueError("estatesSearch query has no data")
            return data
    raise ValueError("estatesSearch query not found in __NEXT_DATA__")


def _page_url(search_url: str, page: int) -> str:
    """Return the search URL for a given page number."""
    sep = "&" if "?" in search_url else "?"
    return f"{search_url}{sep}strana={page}"


async def get_all_listing_ids(
    client: httpx.AsyncClient,
    search_url: str,
    max_ids: int | None = None,
) -> list[str]:
    """Fetch listing IDs across paginated search results.

    Fetches page 1 to determine total count, then iterates remaining pages.
    Returns IDs as strings (sreality integer IDs cast to str).
    Stops early if a page returns 0 results or max_ids is reached.

    Args:
        max_ids: If set, stop collecting once this many IDs are gathered.
    """
    # --- page 1: discover total ---
    resp = await get_with_retry(client, _page_url(search_url, 1))
    next_data = _extract_next_data(resp.text)
    search_data = _find_search_data(next_data)

    pagination = search_data["pagination"]
    total = pagination["total"]
    limit = pagination["limit"] or 22
    total_pages = math.ceil(total / limit)

    ids: list[str] = [str(r["id"]) for r in search_data.get("results", [])]
    log.info("page_fetched", page=1, total_pages=total_pages, found=len(ids), total=total)

    if not ids:
        return ids

    if max_ids is not None and len(ids) >= max_ids:
        return ids[:max_ids]

    # --- remaining pages ---
    for page in range(2, total_pages + 1):
        url = _page_url(search_url, page)
        resp = await get_with_retry(client, url)
        next_data = _extract_next_data(resp.text)
        try:
            search_data = _find_search_data(next_data)
        except ValueError as exc:
            log.warning("pagination_stopped", page=page, error=str(exc))
            break

        page_ids = [str(r["id"]) for r in search_data.get("results", [])]
        if not page_ids:
            log.info("pagination_empty_page", page=page, total_pages=total_pages)
            break

        ids.extend(page_ids)
        log.info(
            "page_fetched",
            page=page,
            total_pages=total_pages,
            found=len(page_ids),
            running_total=len(ids),
        )

        if max_ids is not None and len(ids) >= max_ids:
            log.info("pagination_max_ids", max_ids=max_ids)
            break

    return ids if max_ids is None else ids[:max_ids]
