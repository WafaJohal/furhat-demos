from pathlib import Path

from fastapi.testclient import TestClient

from furhat_demos.webui.app import create_app
from furhat_demos.webui.robot_connection import RobotConnection

FIXTURE_PDF = Path(__file__).parent.parent / "opendemo" / "fixtures" / "sample_upload.pdf"


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


class RaisingController:
    def start_demo(self, demo_id: str, option_id: str) -> None:
        raise ConnectionError("No route to host")


def test_select_returns_503_when_controller_raises():
    app = create_app(controller=RaisingController())
    client = TestClient(app, raise_server_exceptions=False)

    res = client.post("/api/select", json={"demo_id": "opendemo", "option_id": "guide"})

    assert res.status_code == 503
    assert "robot" in res.json()["detail"].lower()


def test_robot_status_default_is_disconnected():
    client, _ = make_client()

    res = client.get("/api/robot/status")

    assert res.status_code == 200
    body = res.json()
    assert body["connected"] is False
    assert body["host"] is None


def test_robot_connect_success_updates_status():
    connection = RobotConnection(client_factory=lambda host, auth_key: FakeRealtimeClient())
    app = create_app(connection=connection)
    client = TestClient(app)

    res = client.post("/api/robot/connect", json={"host": "172.20.10.10"})

    assert res.status_code == 200
    assert res.json() == {"host": "172.20.10.10", "connected": True}

    status = client.get("/api/robot/status").json()
    assert status["connected"] is True
    assert status["host"] == "172.20.10.10"


def test_robot_connect_passes_auth_key_through():
    received = {}

    def factory(host, auth_key):
        received["auth_key"] = auth_key
        return FakeRealtimeClient()

    connection = RobotConnection(client_factory=factory)
    app = create_app(connection=connection)
    client = TestClient(app)

    client.post("/api/robot/connect", json={"host": "172.20.10.10", "auth_key": "secret-key"})

    assert received["auth_key"] == "secret-key"


def test_robot_connect_failure_returns_502_and_status_reflects_it():
    class RaisingClient:
        def connect(self):
            raise ConnectionError("No route to host")

    connection = RobotConnection(client_factory=lambda host, auth_key: RaisingClient())
    app = create_app(connection=connection)
    client = TestClient(app, raise_server_exceptions=False)

    res = client.post("/api/robot/connect", json={"host": "10.0.0.5"})

    assert res.status_code == 502
    assert "No route to host" in res.json()["detail"]

    status = client.get("/api/robot/status").json()
    assert status["connected"] is False
    assert status["host"] == "10.0.0.5"
    assert "No route to host" in status["error"]


class FakeRealtimeClient:
    def __init__(self):
        self.say_calls: list[dict] = []

    def connect(self):
        pass

    def request_speak_text(self, text, wait=True):
        self.say_calls.append({"text": text, "wait": wait})

    def request_voice_config(self, **kwargs):
        pass

    def request_attend_user(self):
        pass

    def request_listen_start(self, **kwargs):
        return ""


def test_select_uses_the_currently_connected_controller():
    fake_client = FakeRealtimeClient()
    connection = RobotConnection(client_factory=lambda host, auth_key: fake_client)
    app = create_app(connection=connection)
    client = TestClient(app)

    client.post("/api/robot/connect", json={"host": "172.20.10.10"})
    res = client.post("/api/select", json={"demo_id": "facevis", "option_id": "air-quality"})

    assert res.status_code == 200
    assert len(fake_client.say_calls) == 1


def test_create_app_auto_connects_when_furhat_host_env_var_set(monkeypatch):
    monkeypatch.setenv("FURHAT_HOST", "172.20.10.10")
    fake_client = FakeRealtimeClient()
    connection = RobotConnection(client_factory=lambda host, auth_key: fake_client)

    create_app(connection=connection)

    assert connection.state.connected is True
    assert connection.state.host == "172.20.10.10"


def test_admin_page_served(tmp_path):
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)

    res = client.get("/admin")

    assert res.status_code == 200
    assert "Admin" in res.text


def test_admin_documents_empty_by_default(tmp_path):
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)

    res = client.get("/api/admin/documents")

    assert res.status_code == 200
    assert res.json() == []


def test_admin_upload_pdf_then_lists_and_deletes_it(tmp_path):
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)

    with FIXTURE_PDF.open("rb") as f:
        res = client.post(
            "/api/admin/documents",
            files={"file": ("My Course Guide.pdf", f, "application/pdf")},
        )

    assert res.status_code == 200
    filename = res.json()["filename"]
    assert filename == "uploaded-my-course-guide.md"
    assert (tmp_path / filename).exists()

    list_res = client.get("/api/admin/documents")
    assert list_res.json() == [{"filename": filename}]

    delete_res = client.delete(f"/api/admin/documents/{filename}")
    assert delete_res.status_code == 200
    assert not (tmp_path / filename).exists()


def test_admin_upload_rejects_non_pdf_content_type(tmp_path):
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)

    res = client.post(
        "/api/admin/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert res.status_code == 400
    assert "PDF" in res.json()["detail"]


def test_admin_upload_returns_400_when_no_text_extracted(tmp_path):
    blank_pdf = Path(__file__).parent.parent / "opendemo" / "fixtures" / "blank_page.pdf"
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)

    with blank_pdf.open("rb") as f:
        res = client.post(
            "/api/admin/documents",
            files={"file": ("blank.pdf", f, "application/pdf")},
        )

    assert res.status_code == 400
    assert "No extractable text" in res.json()["detail"]


def test_admin_delete_unknown_document_returns_404(tmp_path):
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)

    res = client.delete("/api/admin/documents/uploaded-nope.md")

    assert res.status_code == 404


def test_admin_delete_rejects_non_uploaded_filename(tmp_path):
    app = create_app(documents_dir=tmp_path)
    client = TestClient(app)
    (tmp_path / "handbook-comp10001.md").write_text("real content")

    res = client.delete("/api/admin/documents/handbook-comp10001.md")

    assert res.status_code == 400
