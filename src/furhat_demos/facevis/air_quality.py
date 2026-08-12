from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

WAQI_BASE_URL = "https://api.waqi.info"

# World-spanning bounding box: south,west,north,east.
WORLD_BOUNDS = "-85,-180,85,180"


@dataclass(frozen=True)
class AqiCategory:
    low: float
    high: float
    label: str
    color: str
    charpack: str  # "" means no charpack -- reset to the robot's default face
    frame_count: int


# Single source of truth for AQI bands, shared by the robot's face selection
# (aqi_to_face_id) and the map's marker coloring (aqi_category_label/_color).
# Standard EPA AQI bands; Very Unhealthy (201-300) and Hazardous (301-500) are
# combined onto the single AirHazard charpack/color, since no separate
# charpack exists for Very Unhealthy specifically.
_AQI_CATEGORIES: list[AqiCategory] = [
    AqiCategory(0, 50, "Good", "#2a9d3f", "", 0),
    AqiCategory(51, 100, "Moderate", "#f6c000", "AirModerate", 1),
    AqiCategory(101, 150, "Unhealthy for Sensitive Groups", "#ff8c00", "AirSensGroups", 3),
    AqiCategory(151, 200, "Unhealthy", "#e0301e", "AirUnhealthy", 4),
    AqiCategory(201, 500, "Very Unhealthy / Hazardous", "#7e0023", "AirHazard", 5),
]


def _category_for_aqi(aqi: float) -> AqiCategory:
    # _AQI_CATEGORIES covers [0, 500] with no gaps, and clamping guarantees
    # the value falls in that range, so the loop always returns.
    clamped = max(0.0, min(500.0, aqi))
    for category in _AQI_CATEGORIES:
        if category.low <= clamped <= category.high:
            return category
    raise AssertionError(  # pragma: no cover -- unreachable, see above
        "_AQI_CATEGORIES must cover [0, 500] with no gaps"
    )


def aqi_to_face_id(aqi: float) -> str | None:
    """Map an AQI value to a Furhat face_id (charpack frame), or None for the
    default/neutral face (Good air quality)."""
    category = _category_for_aqi(aqi)
    if not category.charpack:
        return None
    clamped = max(0.0, min(500.0, aqi))
    span = category.high - category.low + 1
    frame = min(
        category.frame_count,
        max(1, math.ceil((clamped - category.low + 1) / span * category.frame_count)),
    )
    return f"{category.charpack}/{category.charpack}{frame}"


def aqi_category_label(aqi: float) -> str:
    return _category_for_aqi(aqi).label


def aqi_category_color(aqi: float) -> str:
    return _category_for_aqi(aqi).color


@dataclass(frozen=True)
class Station:
    uid: int
    name: str
    lat: float
    lon: float
    aqi: float | None


class HttpClient(Protocol):
    def get_json(self, url: str) -> dict: ...


class RequestsHttpClient:
    def __init__(self, timeout: float = 10.0) -> None:
        import httpx

        self._client = httpx.Client(timeout=timeout)

    def get_json(self, url: str) -> dict:
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()


def fetch_stations(
    http_client: HttpClient, token: str, bounds: str = WORLD_BOUNDS
) -> list[Station]:
    url = f"{WAQI_BASE_URL}/map/bounds/?latlng={bounds}&token={token}"
    payload = http_client.get_json(url)
    if payload.get("status") != "ok":
        raise RuntimeError(f"WAQI request failed: {payload.get('data')}")

    stations = []
    for item in payload.get("data", []):
        try:
            aqi = float(item["aqi"])
        except (KeyError, TypeError, ValueError):
            aqi = None
        stations.append(
            Station(
                uid=item["uid"],
                name=item.get("station", {}).get("name", "Unknown"),
                lat=float(item["lat"]),
                lon=float(item["lon"]),
                aqi=aqi,
            )
        )
    return stations
