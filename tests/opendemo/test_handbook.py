from pathlib import Path
from unittest.mock import MagicMock, patch

from furhat_demos.opendemo.handbook import (
    RequestsHttpClient,
    fetch_detail_text,
    parse_detail_page,
    parse_search_results,
    search,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


def test_parse_search_results_extracts_code_name_and_url():
    html = _read_fixture("search_computing.html")

    results = parse_search_results(html)

    assert len(results) > 0
    codes = {r.code for r in results}
    assert "COMP90024" in codes
    match = next(r for r in results if r.code == "COMP90024")
    assert match.name == "Cluster and Cloud Computing"
    assert match.url == "https://handbook.unimelb.edu.au/2026/subjects/comp90024"


def test_parse_search_results_handles_no_matches():
    assert parse_search_results("<html><body><div id='main-content'></div></body></html>") == []


def test_parse_search_results_skips_malformed_result_missing_code():
    html = """
    <div id="main-content">
      <a class="search-result-item__anchor" href="/2026/subjects/comp10001">
        <div class="search-result-item__name"><h3>Foundations of Computing</h3></div>
      </a>
      <a class="search-result-item__anchor" href="/2026/subjects/comp20003">
        <div class="search-result-item__name"><h3>Algorithms and Data Structures</h3></div>
        <span class="search-result-item__code">COMP20003</span>
      </a>
    </div>
    """
    results = parse_search_results(html)

    assert len(results) == 1
    assert results[0].code == "COMP20003"


def test_parse_detail_page_extracts_title_and_content():
    html = _read_fixture("subject_comp10001.html")

    text = parse_detail_page(html)

    assert text.startswith("Foundations of Computing (COMP10001)")
    assert "programming" in text.lower()
    assert "AIMS" in text


def test_parse_detail_page_strips_noise_lines():
    html = _read_fixture("subject_comp10001.html")

    text = parse_detail_page(html)
    lines = text.split("\n")

    assert "Or view archived Handbooks" not in lines
    assert not any(line.strip() == "2026" for line in lines)
    assert not any(line.startswith("Last updated:") for line in lines)
    assert not any(line.startswith("Next:") for line in lines)


def test_parse_detail_page_handles_course_page_template():
    html = _read_fixture("course_d-comp.html")

    text = parse_detail_page(html)

    assert text.startswith("Diploma in Computing (D-COMP)")
    assert "credit points" in text.lower()


def test_parse_detail_page_handles_second_subject_fixture():
    html = _read_fixture("subject_comp20003.html")

    text = parse_detail_page(html)

    assert "Algorithms and Data Structures" in text


def test_parse_detail_page_handles_main_content_with_no_text():
    assert parse_detail_page('<html><body><div id="main-content"></div></body></html>') == ""


def test_parse_detail_page_returns_empty_string_when_no_main_content():
    assert parse_detail_page("<html><body>nothing here</body></html>") == ""


class FakeHttpClient:
    def __init__(self, responses: dict[str, str]):
        self.responses = responses
        self.requested_urls: list[str] = []

    def get(self, url: str) -> str:
        self.requested_urls.append(url)
        return self.responses[url]


def test_search_calls_expected_url_and_parses_results():
    html = _read_fixture("search_computing.html")
    client = FakeHttpClient({"https://handbook.unimelb.edu.au/search?query=computing": html})

    results = search(client, "computing")

    assert client.requested_urls == ["https://handbook.unimelb.edu.au/search?query=computing"]
    assert len(results) > 0


def test_fetch_detail_text_calls_get_and_parses():
    html = _read_fixture("subject_comp10001.html")
    client = FakeHttpClient({"https://handbook.unimelb.edu.au/subjects/comp10001": html})

    text = fetch_detail_text(client, "https://handbook.unimelb.edu.au/subjects/comp10001")

    assert text.startswith("Foundations of Computing (COMP10001)")


def test_requests_http_client_get_returns_response_text_and_raises_for_status():
    fake_response = MagicMock()
    fake_response.text = "<html>ok</html>"

    fake_httpx_client = MagicMock()
    fake_httpx_client.get.return_value = fake_response

    with patch("httpx.Client", return_value=fake_httpx_client):
        client = RequestsHttpClient()
        result = client.get("https://handbook.unimelb.edu.au/subjects/comp10001")

    fake_httpx_client.get.assert_called_once_with(
        "https://handbook.unimelb.edu.au/subjects/comp10001"
    )
    fake_response.raise_for_status.assert_called_once()
    assert result == "<html>ok</html>"
