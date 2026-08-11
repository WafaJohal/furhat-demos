from fastapi.testclient import TestClient

from furhat_demos.webui.app import create_app
from furhat_demos.webui.robot_connection import RobotConnection


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
    connection = RobotConnection(remote_api_factory=lambda host: object(), probe=lambda api: None)
    app = create_app(connection=connection)
    client = TestClient(app)

    res = client.post("/api/robot/connect", json={"host": "172.20.10.10"})

    assert res.status_code == 200
    assert res.json() == {"host": "172.20.10.10", "connected": True}

    status = client.get("/api/robot/status").json()
    assert status["connected"] is True
    assert status["host"] == "172.20.10.10"


def test_robot_connect_failure_returns_502_and_status_reflects_it():
    def failing_probe(remote_api):
        raise ConnectionError("No route to host")

    connection = RobotConnection(remote_api_factory=lambda host: object(), probe=failing_probe)
    app = create_app(connection=connection)
    client = TestClient(app, raise_server_exceptions=False)

    res = client.post("/api/robot/connect", json={"host": "10.0.0.5"})

    assert res.status_code == 502
    assert "No route to host" in res.json()["detail"]

    status = client.get("/api/robot/status").json()
    assert status["connected"] is False
    assert status["host"] == "10.0.0.5"
    assert "No route to host" in status["error"]


class FullFakeRemoteApi:
    def __init__(self):
        self.say_calls: list[dict] = []

    def say(self, **kwargs):
        self.say_calls.append(kwargs)

    def get_voices(self, **kwargs):
        return []

    def set_voice(self, name):
        pass

    def listen(self):
        return None


def test_select_uses_the_currently_connected_controller():
    fake_remote_api = FullFakeRemoteApi()
    connection = RobotConnection(
        remote_api_factory=lambda host: fake_remote_api, probe=lambda api: None
    )
    app = create_app(connection=connection)
    client = TestClient(app)

    client.post("/api/robot/connect", json={"host": "172.20.10.10"})
    res = client.post("/api/select", json={"demo_id": "facevis", "option_id": "air-quality"})

    assert res.status_code == 200
    assert len(fake_remote_api.say_calls) == 1


def test_create_app_auto_connects_when_furhat_host_env_var_set(monkeypatch):
    monkeypatch.setenv("FURHAT_HOST", "172.20.10.10")
    fake_remote_api = FullFakeRemoteApi()
    connection = RobotConnection(
        remote_api_factory=lambda host: fake_remote_api, probe=lambda api: None
    )

    create_app(connection=connection)

    assert connection.state.connected is True
    assert connection.state.host == "172.20.10.10"
