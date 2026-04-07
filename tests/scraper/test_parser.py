"""Tests for src/scraper/parser.py — no network calls."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.scraper.parser import (
    ListingData,
    _extract_estate_data,
    _map_estate_to_listing,
    fetch_listing_detail,
)

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


def _load_detail_fixture() -> dict:
    return json.loads((FIXTURE_DIR / "listing_detail.json").read_text(encoding="utf-8"))


def _wrap_estate_in_html(estate: dict) -> str:
    nd = {
        "props": {
            "pageProps": {
                "dehydratedState": {
                    "queries": [
                        {
                            "queryKey": ["estate", {"id": 1}],
                            "state": {"data": estate},
                        }
                    ]
                }
            }
        }
    }
    payload = json.dumps(nd)
    return f'<html><script id="__NEXT_DATA__" type="application/json">{payload}</script></html>'


# ---------------------------------------------------------------------------
# _extract_estate_data
# ---------------------------------------------------------------------------

def test_extract_estate_data_from_fixture():
    fixture = _load_detail_fixture()
    html = _wrap_estate_in_html(fixture["estate"])
    estate = _extract_estate_data(html)
    assert estate["name"] == fixture["estate"]["name"]


def test_extract_estate_data_raises_when_no_script():
    with pytest.raises(ValueError, match="__NEXT_DATA__"):
        _extract_estate_data("<html>nothing here</html>")


def test_extract_estate_data_raises_when_estate_query_missing():
    nd = {
        "props": {
            "pageProps": {
                "dehydratedState": {
                    "queries": [{"queryKey": ["other"], "state": {"data": {}}}]
                }
            }
        }
    }
    html = f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(nd)}</script></html>'
    with pytest.raises(ValueError, match="estate query not found"):
        _extract_estate_data(html)


def test_extract_estate_data_raises_when_data_none():
    nd = {
        "props": {
            "pageProps": {
                "dehydratedState": {
                    "queries": [{"queryKey": ["estate", {}], "state": {"data": None}}]
                }
            }
        }
    }
    html = f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(nd)}</script></html>'
    with pytest.raises(ValueError, match="delisted"):
        _extract_estate_data(html)


# ---------------------------------------------------------------------------
# _map_estate_to_listing — field mapping
# ---------------------------------------------------------------------------

def test_map_real_fixture_all_fields():
    fixture = _load_detail_fixture()
    result = _map_estate_to_listing(
        fixture["estate"],
        listing_id=str(fixture["listing_id"]),
        final_url=fixture["final_url"],
    )

    assert isinstance(result, ListingData)
    assert result.sreality_id == "1399477068"
    assert result.listing_type == "sale"
    assert result.property_type == "flat"
    assert "Prodej bytu 1+kk" in result.title
    assert "m²" in result.title or "m\xb2" in result.title
    assert result.price_czk == 5_990_000
    assert result.area_m2 == 37
    assert result.floor == 2
    assert result.gps_lat == pytest.approx(50.11664)
    assert result.gps_lon == pytest.approx(14.473991)
    assert "Praha" in result.locality
    assert result.url == fixture["final_url"]
    assert len(result.images) > 0
    assert result.description is not None and len(result.description) > 0
    assert result.raw_data == fixture["estate"]


def test_map_locality_string_format():
    fixture = _load_detail_fixture()
    result = _map_estate_to_listing(fixture["estate"], "123", "http://x")
    # Should be "City, District" format
    assert result.locality == "Praha, Praha 8"


def test_map_unknown_listing_type_returns_none():
    fixture = _load_detail_fixture()
    bad_estate = dict(fixture["estate"])
    bad_estate["categoryTypeCb"] = {"name": "Unknown", "value": 99}
    result = _map_estate_to_listing(bad_estate, "123", "http://x")
    assert result is None


def test_map_missing_title_returns_none():
    fixture = _load_detail_fixture()
    bad_estate = dict(fixture["estate"])
    bad_estate["name"] = ""
    result = _map_estate_to_listing(bad_estate, "123", "http://x")
    assert result is None


def test_map_none_price_is_allowed():
    fixture = _load_detail_fixture()
    estate = dict(fixture["estate"])
    estate["priceCzk"] = None
    result = _map_estate_to_listing(estate, "123", "http://x")
    assert result is not None
    assert result.price_czk is None


def test_map_none_description_is_allowed():
    fixture = _load_detail_fixture()
    estate = dict(fixture["estate"])
    estate["description"] = None
    result = _map_estate_to_listing(estate, "123", "http://x")
    assert result is not None
    assert result.description is None


def test_map_missing_params_area_and_floor_are_none():
    fixture = _load_detail_fixture()
    estate = dict(fixture["estate"])
    estate["params"] = {}
    result = _map_estate_to_listing(estate, "123", "http://x")
    assert result is not None
    assert result.area_m2 is None
    assert result.floor is None


def test_map_rent_listing_type():
    fixture = _load_detail_fixture()
    estate = dict(fixture["estate"])
    estate["categoryTypeCb"] = {"name": "Pronájem", "value": 2}
    result = _map_estate_to_listing(estate, "123", "http://x")
    assert result is not None
    assert result.listing_type == "rent"


# ---------------------------------------------------------------------------
# fetch_listing_detail — integration with mock httpx
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fetch_listing_detail_success():
    fixture = _load_detail_fixture()
    html = _wrap_estate_in_html(fixture["estate"])

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.text = html
    mock_resp.url = "https://www.sreality.cz/detail/prodej/byt/1+kk/x/1399477068"

    with patch("src.scraper.parser.get_with_retry", return_value=mock_resp):
        result = await fetch_listing_detail(AsyncMock(), "1399477068")

    assert isinstance(result, ListingData)
    assert result.sreality_id == "1399477068"
    assert result.listing_type == "sale"


@pytest.mark.asyncio
async def test_fetch_listing_detail_returns_none_on_http_error():
    with patch(
        "src.scraper.parser.get_with_retry",
        side_effect=httpx.HTTPStatusError("404", request=None, response=None),
    ):
        result = await fetch_listing_detail(AsyncMock(), "9999")

    assert result is None


@pytest.mark.asyncio
async def test_fetch_listing_detail_returns_none_on_parse_error():
    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.text = "<html>no next data</html>"
    mock_resp.url = "http://x"

    with patch("src.scraper.parser.get_with_retry", return_value=mock_resp):
        result = await fetch_listing_detail(AsyncMock(), "123")

    assert result is None
