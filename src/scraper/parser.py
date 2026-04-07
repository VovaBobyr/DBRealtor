"""Parser for sreality.cz listing detail pages.

Fetches a detail page by listing ID, extracts __NEXT_DATA__ JSON,
and maps fields to a validated ListingData Pydantic model.
"""

import json
import re
from typing import Any

import httpx
import structlog
from pydantic import BaseModel, Field

from src.scraper.browser import get_with_retry

log = structlog.get_logger()

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)
# sreality uses the numeric ID to locate the listing and ignores the
# path prefix, so we use a fixed "prodej/byt/1+kk" stub that causes a
# redirect to the canonical URL.  "/" + "x" path segments return 404.
_DETAIL_URL_TEMPLATE = "https://www.sreality.cz/detail/prodej/byt/1+kk/x/{listing_id}"

# categoryTypeCb.value → listing_type enum
_LISTING_TYPE_MAP: dict[int, str] = {
    1: "sale",
    2: "rent",
}

# categoryMainCb.value → property_type enum
_PROPERTY_TYPE_MAP: dict[int, str] = {
    1: "flat",
    2: "house",
    3: "land",
    4: "commercial",
}


class ListingData(BaseModel):
    """Validated listing data ready for DB upsert."""

    sreality_id: str
    listing_type: str  # 'sale' | 'rent'
    property_type: str  # 'flat' | 'house' | 'land' | 'commercial'
    title: str
    description: str | None = None
    price_czk: int | None = None
    area_m2: int | None = None
    floor: int | None = None
    locality: str | None = None
    gps_lat: float | None = None
    gps_lon: float | None = None
    url: str
    images: list[dict[str, Any]] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)


def _extract_estate_data(html: str) -> dict[str, Any]:
    """Extract the 'estate' query data from __NEXT_DATA__ in an HTML response."""
    match = _NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("__NEXT_DATA__ script tag not found")
    next_data = json.loads(match.group(1))
    queries = next_data["props"]["pageProps"]["dehydratedState"]["queries"]
    for q in queries:
        key = q.get("queryKey", [])
        if key and key[0] == "estate":
            data = q["state"].get("data")
            if data is None:
                raise ValueError("estate query has no data (listing may be delisted)")
            return data
    raise ValueError("estate query not found in __NEXT_DATA__")


def _map_estate_to_listing(
    estate: dict[str, Any],
    listing_id: str,
    final_url: str,
) -> ListingData | None:
    """Map a raw estate dict to ListingData. Returns None on mapping failure."""
    try:
        type_value = estate["categoryTypeCb"]["value"]
        listing_type = _LISTING_TYPE_MAP.get(type_value)
        if listing_type is None:
            log.warning("unknown_listing_type", value=type_value, listing_id=listing_id)
            return None

        main_value = estate["categoryMainCb"]["value"]
        property_type = _PROPERTY_TYPE_MAP.get(main_value, "flat")

        title = estate.get("name", "").strip()
        if not title:
            log.warning("missing_title", listing_id=listing_id)
            return None

        locality_obj = estate.get("locality") or {}
        city = locality_obj.get("city", "")
        district = locality_obj.get("district", "")
        locality_str = f"{city}, {district}".strip(", ") if (city or district) else None

        params = estate.get("params") or {}

        images = estate.get("images") or []

        return ListingData(
            sreality_id=listing_id,
            listing_type=listing_type,
            property_type=property_type,
            title=title,
            description=estate.get("description") or None,
            price_czk=estate.get("priceCzk"),
            area_m2=params.get("usableArea"),
            floor=params.get("floorNumber"),
            locality=locality_str,
            gps_lat=locality_obj.get("latitude"),
            gps_lon=locality_obj.get("longitude"),
            url=final_url,
            images=images,
            raw_data=estate,
        )

    except (KeyError, TypeError) as exc:
        log.warning("mapping_failed", listing_id=listing_id, error=str(exc))
        return None


async def fetch_listing_detail(
    client: httpx.AsyncClient,
    listing_id: str,
) -> ListingData | None:
    """Fetch a listing detail page and return a validated ListingData.

    Returns None (with a logged warning) if parsing fails or a required
    field is missing. Does not raise on recoverable errors.
    """
    url = _DETAIL_URL_TEMPLATE.format(listing_id=listing_id)
    try:
        resp = await get_with_retry(client, url)
    except Exception as exc:
        log.warning("fetch_failed", listing_id=listing_id, error=str(exc))
        return None

    try:
        estate = _extract_estate_data(resp.text)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        log.warning("parse_failed", listing_id=listing_id, error=str(exc))
        return None

    return _map_estate_to_listing(estate, listing_id, str(resp.url))
