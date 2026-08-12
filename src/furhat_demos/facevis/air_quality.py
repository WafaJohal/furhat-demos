from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

WAQI_BASE_URL = "https://api.waqi.info"

# World-spanning bounding box: south,west,north,east.
WORLD_BOUNDS = "-85,-180,85,180"

# (low, high, charpack base name, frame count). "" means no charpack -- reset
# to the robot's default/neutral face. Categories follow the standard EPA AQI
# bands; Very Unhealthy (201-300) and Hazardous (301-500) are combined onto
# the single AirHazard charpack (5 frames), since no separate charpack exists
# for Very Unhealthy specifically.
_AQI_CATEGORIES: list[tuple[float, float, str, int]] = [
    (0, 50, "", 0),
    (51, 100, "AirModerate", 1),
    (101, 150, "AirSensGroups", 3),
    (151, 200, "AirUnhealthy", 4),
    (201, 500, "AirHazard", 5),
]


def aqi_to_face_id(aqi: float) -> str | None:
    """Map an AQI value to a Furhat face_id (charpack frame), or None for the
    default/neutral face (Good air quality)."""
    # _AQI_CATEGORIES covers [0, 500] with no gaps, and clamping guarantees
    # the value falls in that range, so the loop always returns.
    clamped = max(0.0, min(500.0, aqi))
    for low, high, charpack, frame_count in _AQI_CATEGORIES:
        if low <= clamped <= high:
            if not charpack:
                return None
            span = high - low + 1
            frame = min(frame_count, max(1, math.ceil((clamped - low + 1) / span * frame_count)))
            return f"{charpack}/{charpack}{frame}"
    return None  # pragma: no cover -- unreachable, _AQI_CATEGORIES spans [0, 500] with no gaps


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
