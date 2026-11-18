import re
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# Canonical municipal zones and reference centroids for smart city sectors/wards
# Covers common urban landmarks, sectors, wards, and zones for robust offline grounding
MUNICIPAL_GAZETTEER = {
    "sector 1": {"lat": 28.5355, "lng": 77.3910, "ward": "Ward 1 - Sector 1", "zone": "North Zone"},
    "sector 9": {"lat": 28.5700, "lng": 77.3200, "ward": "Ward 9 - Sector 9", "zone": "North Zone"},
    "sector 14": {"lat": 28.4720, "lng": 77.0520, "ward": "Ward 14 - Sector 14", "zone": "Central Zone"},
    "sector 15": {"lat": 28.4680, "lng": 77.0500, "ward": "Ward 15 - Sector 15", "zone": "Central Zone"},
    "sector 21": {"lat": 28.5050, "lng": 77.0680, "ward": "Ward 21 - Sector 21", "zone": "South Zone"},
    "sector 62": {"lat": 28.6280, "lng": 77.3649, "ward": "Ward 62 - Tech Zone", "zone": "East Zone"},
    "shanti nagar": {"lat": 12.9560, "lng": 77.5970, "ward": "Shanti Nagar", "zone": "Central Zone"},
    "central zone": {"lat": 12.9716, "lng": 77.5946, "ward": "Central Zone", "zone": "Central Zone"},
    "indiranagar": {"lat": 12.9784, "lng": 77.6408, "ward": "Indiranagar Ward 82", "zone": "East Zone"},
    "koramangala": {"lat": 12.9352, "lng": 77.6245, "ward": "Koramangala Ward 151", "zone": "South Zone"},
    "whitefield": {"lat": 12.9698, "lng": 77.7500, "ward": "Whitefield Ward 84", "zone": "East Zone"},
    "jayanagar": {"lat": 12.9308, "lng": 77.5838, "ward": "Jayanagar Ward 153", "zone": "South Zone"},
    "malleshwaram": {"lat": 13.0031, "lng": 77.5643, "ward": "Malleshwaram Ward 65", "zone": "West Zone"},
    "mg road": {"lat": 12.9756, "lng": 77.6066, "ward": "Central Business District", "zone": "Central Zone"},
    "civil lines": {"lat": 28.6814, "lng": 77.2227, "ward": "Civil Lines Ward 12", "zone": "North Zone"},
}

DEFAULT_CIVIC_CENTER = {
    "lat": 12.9716,
    "lng": 77.5946,
    "ward": "Central Ward 1",
    "zone": "Headquarters Zone"
}


class LocationIntelligenceAgent:
    """
    Location Intelligence Agent:
    Perceives unstructured spatial clues (landmarks, addresses, ward hints),
    resolves them to geo-coordinates (lat/lng), and grounds complaints into
    official municipal administrative wards and zones.
    """

    def __init__(self, default_city: str = "Bengaluru"):
        self.default_city = default_city
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {"User-Agent": "CivicConnect-AgenticAI/1.0"}

    async def resolve_location(
        self,
        area_ward_name: Optional[str] = None,
        landmark: Optional[str] = None,
        location_hint: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolves spatial input into a structured Location Intelligence Result:
        - geo_coordinates: { lat, lng }
        - standardized_ward: official ward name for department routing
        - zone: municipal zone
        - confidence_score: 0.0 - 1.0
        - source: 'gazetteer_match' | 'geocoding_tool' | 'heuristic_resolution' | 'civic_center_fallback'
        """
        # Step 1: Synthesize all location clues into a unified query
        candidate_clues = []
        for text in [area_ward_name, landmark, location_hint]:
            if text and str(text).strip() and str(text).lower() not in {"null", "none", "unknown", "n/a"}:
                candidate_clues.append(str(text).strip())

        raw_query = ", ".join(candidate_clues) if candidate_clues else ""

        # If explicit location fields are empty, try extracting spatial references from title/description
        if not raw_query:
            extracted_clue = self._extract_spatial_heuristics(title, description)
            if extracted_clue:
                raw_query = extracted_clue
                candidate_clues.append(extracted_clue)

        # Step 2: Query Municipal Gazetteer (Fast, authoritative offline spatial knowledge)
        gazetteer_result = self._match_gazetteer(raw_query)
        if gazetteer_result:
            logger.info("Location resolved via Municipal Gazetteer: %s", gazetteer_result["ward"])
            return {
                "raw_query": raw_query,
                "geo_coordinates": {
                    "lat": gazetteer_result["lat"],
                    "lng": gazetteer_result["lng"],
                },
                "area_ward_name": gazetteer_result["ward"],
                "zone": gazetteer_result["zone"],
                "confidence_score": 0.95,
                "source": "gazetteer_match",
            }

        # Step 3: Tool Call -> External Geocoding API (OpenStreetMap Nominatim)
        if raw_query:
            nominatim_result = await self._query_nominatim(raw_query)
            if nominatim_result:
                logger.info("Location resolved via Geocoding Tool: %s", nominatim_result["display_name"])
                derived_ward = area_ward_name or nominatim_result.get("suburb") or nominatim_result.get("city_district") or f"Ward - {raw_query[:20]}"
                return {
                    "raw_query": raw_query,
                    "geo_coordinates": {
                        "lat": nominatim_result["lat"],
                        "lng": nominatim_result["lng"],
                    },
                    "area_ward_name": derived_ward,
                    "zone": nominatim_result.get("zone", "Urban Jurisdiction"),
                    "formatted_address": nominatim_result.get("display_name"),
                    "confidence_score": 0.85,
                    "source": "geocoding_tool",
                }

        # Step 4: Sector/Ward heuristic parsing if a number was mentioned
        sector_match = re.search(r"sector\s*(\d+)", raw_query, re.IGNORECASE)
        if sector_match:
            sec_num = sector_match.group(1)
            derived_ward = f"Ward {sec_num} - Sector {sec_num}"
            # Synthesize deterministic coordinates bounded to the city
            lat = round(DEFAULT_CIVIC_CENTER["lat"] + (int(sec_num) % 10) * 0.012, 4)
            lng = round(DEFAULT_CIVIC_CENTER["lng"] + (int(sec_num) % 8) * 0.015, 4)
            return {
                "raw_query": raw_query,
                "geo_coordinates": {"lat": lat, "lng": lng},
                "area_ward_name": derived_ward,
                "zone": "Municipal Ward Grid",
                "confidence_score": 0.70,
                "source": "heuristic_resolution",
            }

        # Step 5: Graceful fallback to City Administrative Center
        fallback_ward = area_ward_name or "General Municipal Area"
        logger.warning("No precise location resolved for '%s'. Defaulting to City Civic Center.", raw_query)
        return {
            "raw_query": raw_query or "Unspecified",
            "geo_coordinates": {
                "lat": DEFAULT_CIVIC_CENTER["lat"],
                "lng": DEFAULT_CIVIC_CENTER["lng"],
            },
            "area_ward_name": fallback_ward,
            "zone": DEFAULT_CIVIC_CENTER["zone"],
            "confidence_score": 0.40,
            "source": "civic_center_fallback",
        }

    def _match_gazetteer(self, text: str) -> Optional[Dict[str, Any]]:
        """Matches input against known municipal landmarks and wards."""
        if not text:
            return None
        lowered = text.lower()
        for key, data in MUNICIPAL_GAZETTEER.items():
            if key in lowered:
                return data
        return None

    def _extract_spatial_heuristics(self, title: Optional[str], description: Optional[str]) -> Optional[str]:
        """Extracts spatial phrases like 'near ...', 'in sector ...', 'at ... road' from text."""
        combined = f"{title or ''} {description or ''}"
        patterns = [
            r"(?:near|at|opposite|behind|beside)\s+([A-Za-z0-9\s]{3,30})(?:,|\.|$)",
            r"(sector\s*\d+)",
            r"(ward\s*\d+)",
            r"([A-Za-z]+(?:\s+nagar|\s+colony|\s+road|\s+street|\s+layout))",
        ]
        for pat in patterns:
            match = re.search(pat, combined, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    async def _query_nominatim(self, query: str) -> Optional[Dict[str, Any]]:
        """Asynchronously calls OpenStreetMap Nominatim for geocoding."""
        try:
            full_query = f"{query}, {self.default_city}"
            params = {
                "q": full_query,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
            }
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(self.nominatim_url, params=params, headers=self.headers)
                if res.status_code == 200:
                    data = res.json()
                    if data and len(data) > 0:
                        first = data[0]
                        address = first.get("address", {})
                        return {
                            "lat": round(float(first["lat"]), 5),
                            "lng": round(float(first["lon"]), 5),
                            "display_name": first.get("display_name"),
                            "suburb": address.get("suburb"),
                            "city_district": address.get("city_district") or address.get("county"),
                            "zone": address.get("state_district") or "Municipal Division",
                        }
        except Exception as e:
            logger.debug("Geocoding tool call failed (offline or timeout): %s", e)
        return None
