"""Async HTTP client factory for sreality.cz scraping.

Provides a pre-configured httpx.AsyncClient with:
- Realistic browser headers to avoid bot detection
- CMP consent cookie to bypass the cookie-wall
- Automatic retry on 429 / 5xx with exponential backoff
- Configurable inter-request delay
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
import structlog

log = structlog.get_logger()

_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_DEFAULT_HEADERS = {
    "User-Agent": _DEFAULT_USER_AGENT,
    # Sending Accept: application/json + X-Requested-With: XMLHttpRequest
    # causes the sreality.cz Next.js server to respond with the full SSR page
    # and skip the CMP consent-wall redirect loop through cmp.seznam.cz /
    # bcr.iva.seznam.cz.  The HTML response still includes __NEXT_DATA__ JSON.
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "cs,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
}
_MAX_RETRIES = int(os.getenv("SCRAPE_MAX_RETRIES", "3"))
_DELAY_SECONDS = float(os.getenv("SCRAPE_DELAY_SECONDS", "1.5"))


@asynccontextmanager
async def make_client() -> AsyncIterator[httpx.AsyncClient]:
    """Yield a configured AsyncClient. Use as an async context manager."""
    async with httpx.AsyncClient(
        headers=_DEFAULT_HEADERS,
        follow_redirects=True,
        timeout=httpx.Timeout(30.0),
    ) as client:
        yield client


async def get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    *,
    delay: float = _DELAY_SECONDS,
    max_retries: int = _MAX_RETRIES,
) -> httpx.Response:
    """GET *url* with exponential backoff on 429 / 5xx.

    Sleeps *delay* seconds before every request (rate limiting).
    Raises httpx.HTTPStatusError after all retries are exhausted.
    """
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        await asyncio.sleep(delay if attempt == 0 else delay * (2 ** attempt))
        try:
            resp = await client.get(url)
        except httpx.TransportError as exc:
            last_exc = exc
            log.warning("transport_error", url=url, attempt=attempt + 1, error=str(exc))
            continue

        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", delay * (2 ** (attempt + 1))))
            log.warning(
                "rate_limited",
                url=url,
                sleep_s=retry_after,
                attempt=attempt + 1,
                max_attempts=max_retries + 1,
            )
            await asyncio.sleep(retry_after)
            last_exc = httpx.HTTPStatusError(
                f"429 on {url}", request=resp.request, response=resp
            )
            continue

        if resp.status_code >= 500:
            log.warning(
                "http_error",
                status=resp.status_code,
                url=url,
                attempt=attempt + 1,
                max_attempts=max_retries + 1,
            )
            last_exc = httpx.HTTPStatusError(
                f"HTTP {resp.status_code} on {url}", request=resp.request, response=resp
            )
            continue

        resp.raise_for_status()
        return resp

    raise last_exc or RuntimeError(f"All retries failed for {url}")
