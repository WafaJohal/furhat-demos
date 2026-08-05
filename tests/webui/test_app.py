from fastapi.testclient import TestClient

from furhat_demos.webui.app import create_app


class RecordingController:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def start_demo(self, demo_id: str, option_id: str) -> None:
        self.calls.append((demo_id, option_id))


def make_client():
    controller = RecordingController()
    app = create_app(controller=controller)
    return TestClient(app), controller


def test_list_demos_returns_expected_shape():
    client, _ = make_client()
    res = client.get("/api/demos")
    assert res.status_code == 200
    demos = res.json()
    assert {d["id"] for d in demos} == {"opendemo", "facevis"}
    assert all("options" in d and len(d["options"]) > 0 for d in demos)


def test_select_valid_option_calls_controller():
    client, controller = make_client()
    res = client.post("/api/select", json={"demo_id": "opendemo", "option_id": "guide"})
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "demo_id": "opendemo", "option_id": "guide"}
    assert controller.calls == [("opendemo", "guide")]


def test_select_unknown_demo_returns_404():
    client, controller = make_client()
    res = client.post("/api/select", json={"demo_id": "nope", "option_id": "guide"})
    assert res.status_code == 404
    assert controller.calls == []


def test_select_unknown_option_returns_404():
    client, controller = make_client()
    res = client.post("/api/select", json={"demo_id": "opendemo", "option_id": "nope"})
    assert res.status_code == 404
    assert controller.calls == []


def test_index_page_served():
    client, _ = make_client()
    res = client.get("/")
    assert res.status_code == 200
    assert "Furhat Demos" in res.text


def test_default_controller_is_used_when_none_passed():
    app = create_app()
    client = TestClient(app)
    res = client.post("/api/select", json={"demo_id": "facevis", "option_id": "air-quality"})
    assert res.status_code == 200
