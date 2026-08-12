from unittest.mock import MagicMock, patch

import pytest

from furhat_demos.facevis.air_quality import (
    WORLD_BOUNDS,
    RequestsHttpClient,
    Station,
    aqi_to_face_id,
    fetch_stations,
)


@pytest.mark.parametrize(
    "aqi,expected",
    [
        (0, None),
        (25, None),
        (50, None),
        (51, "AirModerate/AirModerate1"),
        (75, "AirModerate/AirModerate1"),
        (100, "AirModerate/AirModerate1"),
        (101, "AirSensGroups/AirSensGroups1"),
        (125, "AirSensGroups/AirSensGroups2"),
        (150, "AirSensGroups/AirSensGroups3"),
        (151, "AirUnhealthy/AirUnhealthy1"),
        (175, "AirUnhealthy/AirUnhealthy2"),
        (200, "AirUnhealthy/AirUnhealthy4"),
        (201, "AirHazard/AirHazard1"),
        (350, "AirHazard/AirHazard3"),
        (500, "AirHazard/AirHazard5"),
    ],
)
def test_aqi_to_face_id_maps_known_values(aqi, expected):
    assert aqi_to_face_id(aqi) == expected


def test_aqi_to_face_id_clamps_negative_to_good():
    assert aqi_to_face_id(-10) is None


def test_aqi_to_face_id_clamps_above_500_to_worst_hazard_frame():
    assert aqi_to_face_id(999) == "AirHazard/AirHazard5"


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.requested_urls: list[str] = []

    def get_json(self, url):
        self.requested_urls.append(url)
        return self.response


def test_fetch_stations_parses_valid_response():
    response = {
        "status": "ok",
        "data": [
            {"lat": -37.8, "lon": 144.9, "uid": 1, "aqi": "42", "station": {"name": "Melbourne"}},
            {"lat": 51.5, "lon": -0.1, "uid": 2, "aqi": "-", "station": {"name": "London"}},
        ],
    }
    client = FakeHttpClient(response)

    stations = fetch_stations(client, token="test-token")

    assert stations == [
        Station(uid=1, name="Melbourne", lat=-37.8, lon=144.9, aqi=42.0),
        Station(uid=2, name="London", lat=51.5, lon=-0.1, aqi=None),
    ]
    assert client.requested_urls[0] == (
        f"https://api.waqi.info/map/bounds/?latlng={WORLD_BOUNDS}&token=test-token"
    )


def test_fetch_stations_handles_missing_station_name():
    response = {"status": "ok", "data": [{"lat": 1.0, "lon": 2.0, "uid": 3, "aqi": "10"}]}
    client = FakeHttpClient(response)

    stations = fetch_stations(client, token="test-token")

    assert stations[0].name == "Unknown"


def test_fetch_stations_raises_on_error_status():
    client = FakeHttpClient({"status": "error", "data": "Invalid key"})

    with pytest.raises(RuntimeError, match="Invalid key"):
        fetch_stations(client, token="bad-token")


def test_requests_http_client_get_json_returns_parsed_response():
    fake_response = MagicMock()
    fake_response.json.return_value = {"status": "ok", "data": []}

    fake_httpx_client = MagicMock()
    fake_httpx_client.get.return_value = fake_response

    with patch("httpx.Client", return_value=fake_httpx_client):
        client = RequestsHttpClient()
        result = client.get_json("https://api.waqi.info/map/bounds/?latlng=x&token=y")

    fake_httpx_client.get.assert_called_once_with(
        "https://api.waqi.info/map/bounds/?latlng=x&token=y"
    )
    fake_response.raise_for_status.assert_called_once()
    assert result == {"status": "ok", "data": []}
