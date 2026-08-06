from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from bs4 import BeautifulSoup

BASE_URL = "https://handbook.unimelb.edu.au"

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

_NOISE_LINE_RE = re.compile(r"^\d{4}$")
_NOISE_LINES = {"Or view archived Handbooks"}
_NOISE_PREFIXES = ("Next:", "Last updated:")


class HttpClient(Protocol):
    def get(self, url: str) -> str: ...


class RequestsHttpClient:
    """Real HTTP client, used only by the offline ingestion script (never at
    demo runtime — see scripts/ingest_handbook.py)."""

    def __init__(self, headers: dict[str, str] | None = None, timeout: float = 10.0) -> None:
        import httpx

        self._client = httpx.Client(headers=headers or _DEFAULT_HEADERS, timeout=timeout)

    def get(self, url: str) -> str:
        response = self._client.get(url)
        response.raise_for_status()
        return response.text


@dataclass(frozen=True)
class SearchResult:
    code: str
    name: str
    url: str


def parse_search_results(html: str) -> list[SearchResult]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for anchor in soup.select("a.search-result-item__anchor"):
        name_el = anchor.select_one(".search-result-item__name h3")
        code_el = anchor.select_one(".search-result-item__code")
        href = anchor.get("href")
        if not (name_el and code_el and href):
            continue
        results.append(
            SearchResult(
                code=code_el.get_text(strip=True),
                name=name_el.get_text(strip=True),
                url=BASE_URL + href,
            )
        )
    return results


def parse_detail_page(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find(id="main-content")
    if main is None:
        return ""

    for el in main.select("#sitemap, .layout-sidebar__side, script, style"):
        el.decompose()

    title_el = main.find("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    lines = []
    for raw_line in main.get_text(separator="\n", strip=True).split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if _NOISE_LINE_RE.match(line) or line in _NOISE_LINES:
            continue
        if any(line.startswith(prefix) for prefix in _NOISE_PREFIXES):
            continue
        lines.append(line)

    body = "\n".join(lines)
    return f"{title}\n\n{body}" if title else body


def search(http_client: HttpClient, query: str) -> list[SearchResult]:
    html = http_client.get(f"{BASE_URL}/search?query={query}")
    return parse_search_results(html)


def fetch_detail_text(http_client: HttpClient, url: str) -> str:
    html = http_client.get(url)
    return parse_detail_page(html)
