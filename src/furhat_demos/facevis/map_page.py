from __future__ import annotations

import plotly.graph_objects as go

from furhat_demos.facevis.air_quality import Station, aqi_category_color, aqi_category_label

_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>FaceVis — Live Air Quality</title>
  <style>
    :root { color-scheme: light; }
    html, body {
      height: 100%;
      margin: 0;
      font-family: system-ui, sans-serif;
      background: #ffffff;
      color: #111111;
    }
    header {
      height: 3rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1rem;
      background: #ffffff;
      color: #111111;
      border-bottom: 1px solid #ddd;
      box-sizing: border-box;
    }
    header h1 { font-size: 1rem; margin: 0; }
    #banner {
      margin: 1rem;
      background: #fff3cd;
      color: #664d03;
      border: 1px solid #ffe69c;
      border-radius: 6px;
      padding: 0.6rem 0.9rem;
      font-size: 0.9rem;
      display: __BANNER_DISPLAY__;
    }
    #status {
      position: fixed;
      bottom: 1rem;
      right: 1rem;
      background: #ffffff;
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 0.5rem 0.8rem;
      font-size: 0.85rem;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
    }
  </style>
</head>
<body>
  <header>
    <h1>FaceVis — Live Air Quality</h1>
    <span>Click a station to show it on Furhat's face</span>
  </header>
  <div id="banner">__BANNER_TEXT__</div>
  __BODY__
  <div id="status"></div>
  <script>
    const mapDiv = document.getElementById('aqi-map');
    const statusEl = document.getElementById('status');

    async function setRobotFace(aqi) {
      statusEl.textContent = 'Setting face…';
      try {
        const res = await fetch('/api/facevis/set_air_quality', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ aqi }),
        });
        const data = await res.json().catch(() => ({}));
        statusEl.textContent = res.ok ? `Done (${data.face_id || 'default face'})` : 'Failed';
      } catch (err) {
        statusEl.textContent = 'Failed';
      }
    }

    if (mapDiv) {
      mapDiv.on('plotly_click', (event) => {
        const point = event.points && event.points[0];
        if (!point || point.customdata === undefined || point.customdata === null) return;
        setRobotFace(point.customdata);
      });
    }
  </script>
</body>
</html>
"""


def render_facevis_page(stations: list[Station] | None, error: str | None = None) -> str:
    """Render the FaceVis air-quality page as a self-contained HTML string.

    Stations are plotted with Plotly's Scattergeo (no OpenStreetMap tiles).
    Clicking a marker posts its AQI to /api/facevis/set_air_quality so the
    robot's face can reflect the selected station.
    """
    plotted = [s for s in (stations or []) if s.aqi is not None]

    fig = go.Figure(
        go.Scattergeo(
            lat=[s.lat for s in plotted],
            lon=[s.lon for s in plotted],
            text=[f"{s.name}<br>AQI: {s.aqi:g}<br>{aqi_category_label(s.aqi)}" for s in plotted],
            customdata=[s.aqi for s in plotted],
            hoverinfo="text",
            mode="markers",
            marker={
                "size": 9,
                "color": [aqi_category_color(s.aqi) for s in plotted],
                "line": {"width": 1, "color": "#333333"},
            },
        )
    )
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="#f2f2f2",
        showocean=True,
        oceancolor="#dceefb",
        showcountries=True,
        countrycolor="#cccccc",
    )
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=700,
    )

    body = fig.to_html(include_plotlyjs="cdn", full_html=False, div_id="aqi-map")

    banner_text = error or ""
    banner_display = "block" if error else "none"

    return (
        _PAGE_TEMPLATE.replace("__BODY__", body)
        .replace("__BANNER_TEXT__", banner_text)
        .replace("__BANNER_DISPLAY__", banner_display)
    )
