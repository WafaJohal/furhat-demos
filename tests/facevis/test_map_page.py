from furhat_demos.facevis.air_quality import Station
from furhat_demos.facevis.map_page import render_facevis_page


def test_render_facevis_page_includes_station_names_and_map_div():
    stations = [
        Station(uid=1, name="Melbourne", lat=-37.8, lon=144.9, aqi=42.0),
        Station(uid=2, name="London", lat=51.5, lon=-0.1, aqi=180.0),
    ]

    html = render_facevis_page(stations)

    assert "aqi-map" in html
    assert "Melbourne" in html
    assert "London" in html
    assert "banner" in html


def test_render_facevis_page_omits_stations_with_no_aqi():
    stations = [Station(uid=1, name="Unknown Station", lat=0.0, lon=0.0, aqi=None)]

    html = render_facevis_page(stations)

    assert "Unknown Station" not in html


def test_render_facevis_page_handles_none_stations():
    html = render_facevis_page(None)

    assert "aqi-map" in html


def test_render_facevis_page_shows_error_banner():
    html = render_facevis_page(None, error="WAQI_API_TOKEN is not set")

    assert "WAQI_API_TOKEN is not set" in html
    assert "display: block" in html


def test_render_facevis_page_hides_banner_when_no_error():
    html = render_facevis_page([])

    assert "display: none" in html
