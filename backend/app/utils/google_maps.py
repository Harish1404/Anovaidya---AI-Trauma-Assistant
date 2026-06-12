"""
Google Maps Places API — Concentric Fallback Search
====================================================
Searches for nearby hospitals, clinics, and specialist medical
facilities using a 3-phase concentric radius strategy.
"""

import logging
from typing import Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn")

PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# ── Specialization → Google keyword mapping ─────────────────────
SPEC_KEYWORDS: Dict[str, str] = {
    "Orthopedics": "orthopedic hospital clinic",
    "General Surgery": "surgery hospital clinic",
    "Neurology": "neurology hospital clinic",
    "Trauma Surgeon": "trauma hospital emergency",
    "Emergency Medicine": "emergency hospital clinic",
    "General Physician": "hospital clinic doctor",
}


async def _places_search(
    lat: float,
    lng: float,
    radius_m: int,
    keyword: str,
    place_type: str = "hospital",
    max_results: int = 10,
) -> List[Dict]:
    """
    Single call to the Google Places Nearby Search API.
    Returns a list of dicts with name, vicinity, rating, lat/lng, etc.
    """
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "keyword": keyword,
        "type": place_type,
        "key": settings.GOOGLE_MAPS_API_KEY,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(PLACES_NEARBY_URL, params=params)
            data = resp.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            logger.warning(f"[GMAPS] API error: {data.get('status')} — {data.get('error_message', '')}")
            return []

        results = data.get("results", [])[:max_results]
        return [_normalize_place(p, lat, lng) for p in results]

    except Exception as e:
        logger.error(f"[GMAPS] Places request failed: {e}")
        return []


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return round(2 * asin(sqrt(a)) * 6371, 2)


def _normalize_place(place: Dict, user_lat: float, user_lng: float) -> Dict:
    """Map a raw Google Places result to the DoctorInfo-compatible schema."""
    loc = place.get("geometry", {}).get("location", {})
    p_lat = loc.get("lat", 0)
    p_lng = loc.get("lng", 0)

    return {
        "full_name": place.get("name", "Unknown"),
        "hospital_name": place.get("name", "Unknown"),
        "specialization": _extract_specialization(place),
        "clinic_address": place.get("vicinity", ""),
        "is_available": place.get("opening_hours", {}).get("open_now", None),
        "distance_km": _haversine(user_lat, user_lng, p_lat, p_lng),
        "rating": place.get("rating"),
        "user_ratings_total": place.get("user_ratings_total", 0),
        "place_id": place.get("place_id", ""),
    }


def _extract_specialization(place: Dict) -> str:
    """Derive a human-readable specialization from the place types."""
    types = set(place.get("types", []))
    if "hospital" in types:
        return "Hospital"
    if "doctor" in types:
        return "Doctor / Clinic"
    if "health" in types:
        return "Health Center"
    return "Medical Facility"


async def find_nearby_medical_facilities(
    lat: float,
    lng: float,
    specialization: Optional[str] = None,
    min_results: int = 3,
    max_results: int = 10,
) -> List[Dict]:
    """
    3-Phase Concentric Fallback Search
    ===================================
    Phase 1 — Specialist + Hospital search within 5 km
    Phase 2 — Specialist + Hospital search within 15 km
    Phase 3 — General Emergency fallback within 15 km

    Returns a de-duplicated, distance-sorted list of facilities.
    """
    keyword = SPEC_KEYWORDS.get(specialization or "", "hospital clinic doctor")
    seen_ids: set = set()
    all_results: List[Dict] = []

    def _merge(new_places: List[Dict]):
        for p in new_places:
            pid = p.get("place_id", p.get("full_name"))
            if pid not in seen_ids:
                seen_ids.add(pid)
                all_results.append(p)

    # ── Phase 1: Specialist + Hospital, 5 km ────────────────────
    logger.info(f"[GMAPS] Phase 1: Searching '{keyword}' within 5 km")
    phase1 = await _places_search(lat, lng, radius_m=5000, keyword=keyword, max_results=max_results)
    _merge(phase1)

    if len(all_results) >= min_results:
        all_results.sort(key=lambda x: x.get("distance_km", 999))
        return all_results[:max_results]

    # ── Phase 2: Specialist + Hospital, 15 km ───────────────────
    logger.info(f"[GMAPS] Phase 2: Expanding to 15 km for '{keyword}'")
    phase2 = await _places_search(lat, lng, radius_m=15000, keyword=keyword, max_results=max_results)
    _merge(phase2)

    if len(all_results) >= min_results:
        all_results.sort(key=lambda x: x.get("distance_km", 999))
        return all_results[:max_results]

    # ── Phase 3: General emergency fallback, 15 km ──────────────
    logger.info("[GMAPS] Phase 3: General emergency/hospital fallback within 15 km")
    phase3 = await _places_search(lat, lng, radius_m=15000, keyword="hospital emergency", max_results=max_results)
    _merge(phase3)

    all_results.sort(key=lambda x: x.get("distance_km", 999))
    return all_results[:max_results]
