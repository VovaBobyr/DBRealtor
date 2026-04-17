"""Tests for src/scraper/paginator.py — no network calls."""

import json
import math
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.scraper.paginator import (
    _extract_next_data,
    _find_search_data,
    _page_url,
    get_all_listing_ids,
)

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_search_next_data(results: list[dict], total: int, limit: int = 22) -> dict:
    """Build a minimal __NEXT_DATA__ structure for a search page."""
    return {
        "props": {
            "pageProps": {
                "dehydratedState": {
                    "queries": [
                        {
                            "queryKey": ["estatesSearch", {}],
                            "state": {
                                "data": {
                                    "pagination": {
                                        "total": total,
                                        "limit": limit,
                                        "offset": 0,
                                        "totalWithPromo": total,
                                    },
                                    "results": results,
                                }
                            },
                        }
                    ]
                }
            }
        }
    }


def _wrap_in_html(next_data: dict) -> str:
    payload = json.dumps(next_data)
    return f'<html><script id="__NEXT_DATA__" type="application/json">{payload}</script></html>'


def _fake_results(ids: list[int]) -> list[dict]:
    return [{"id": i, "name": f"Listing {i}", "priceCzk": 1_000_000} for i in ids]


# ---------------------------------------------------------------------------
# unit tests — pure functions
# ---------------------------------------------------------------------------

def test_extract_next_data_parses_correctly():
    nd = {"props": {"pageProps": {}}}
    html = _wrap_in_html(nd)
    assert _extract_next_data(html) == nd


def test_extract_next_data_raises_when_missing():
    with pytest.raises(ValueError, match="__NEXT_DATA__"):
        _extract_next_data("<html>no script here</html>")


def test_find_search_data_returns_data():
    nd = _make_search_next_data(_fake_results([1, 2, 3]), total=3)
    data = _find_search_data(nd)
    assert data["pagination"]["total"] == 3
    assert len(data["results"]) == 3


def test_find_search_data_raises_when_missing():
    nd = {"props": {"pageProps": {"dehydratedState": {"queries": []}}}}
    with pytest.raises(ValueError, match="estatesSearch"):
        _find_search_data(nd)


def test_page_url_with_no_existing_query():
    assert _page_url("https://example.com/hledani", 3) == \
        "https://example.com/hledani?strana=3"


def test_page_url_with_existing_query():
    assert _page_url("https://example.com/hledani?foo=bar", 2) == \
        "https://example.com/hledani?foo=bar&strana=2"


# ---------------------------------------------------------------------------
# integration-style tests — mock httpx, test get_all_listing_ids
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_single_page_returns_all_ids():
    """When total <= limit, only one page is fetched."""
    ids = [101, 102, 103]
    nd = _make_search_next_data(_fake_results(ids), total=3, limit=22)
    html = _wrap_in_html(nd)

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.text = html

    client = AsyncMock(spec=httpx.AsyncClient)

    with patch("src.scraper.paginator.get_with_retry", return_value=mock_resp) as mock_get:
        result = await get_all_listing_ids(client, "https://example.com/search")

    assert result == ["101", "102", "103"]
    assert mock_get.call_count == 1  # only page 1


@pytest.mark.asyncio
async def test_pagination_fetches_all_pages():
    """With total=44 and limit=22, exactly 2 pages are fetched."""
    page1_ids = list(range(1, 23))   # 22 items
    page2_ids = list(range(23, 45))  # 22 items

    def _make_html(ids, total=44):
        return _wrap_in_html(_make_search_next_data(_fake_results(ids), total=total, limit=22))

    responses = [
        AsyncMock(spec=httpx.Response, text=_make_html(page1_ids)),
        AsyncMock(spec=httpx.Response, text=_make_html(page2_ids)),
    ]

    with patch("src.scraper.paginator.get_with_retry", side_effect=responses):
        result = await get_all_listing_ids(AsyncMock(), "https://example.com/search")

    assert len(result) == 44
    assert result[0] == "1"
    assert result[-1] == "44"


@pytest.mark.asyncio
async def test_stops_early_on_empty_page():
    """If a page returns 0 results, iteration stops."""
    page1_ids = list(range(1, 23))

    def _make_html(ids, total=44):
        return _wrap_in_html(_make_search_next_data(_fake_results(ids), total=total, limit=22))

    responses = [
        AsyncMock(spec=httpx.Response, text=_make_html(page1_ids)),
        AsyncMock(spec=httpx.Response, text=_make_html([])),  # empty page 2
    ]

    with patch("src.scraper.paginator.get_with_retry", side_effect=responses):
        result = await get_all_listing_ids(AsyncMock(), "https://example.com/search")

    assert len(result) == 22  # only page 1


@pytest.mark.asyncio
async def test_real_fixture_parses():
    """Smoke-test the real fixture: check IDs are extracted correctly."""
    fixture = json.loads((FIXTURE_DIR / "search_page.json").read_text(encoding="utf-8"))
    search_data = fixture["search_data"]
    nd = {
        "props": {
            "pageProps": {
                "dehydratedState": {
                    "queries": [
                        {
                            "queryKey": ["estatesSearch", {}],
                            "state": {"data": search_data},
                        }
                    ]
                }
            }
        }
    }
    data = _find_search_data(nd)
    expected_ids = [str(r["id"]) for r in search_data["results"]]
    assert len(expected_ids) == len(data["results"])
    assert expected_ids == [str(i) for i in fixture["listing_ids"]]
