import time
from unittest.mock import MagicMock, patch

from furhat_demos.control import FurhatDemoController, LoggingDemoController
from furhat_demos.webui.robot_connection import RobotConnection, default_realtime_client_factory


class FakeRealtimeClient:
    def __init__(self):
        self.connect_calls = 0

    def connect(self):
        self.connect_calls += 1


def test_connect_success_swaps_controller_and_reports_connected():
    fake_client = FakeRealtimeClient()
    connection = RobotConnection(client_factory=lambda host, auth_key: fake_client)

    state = connection.connect("172.20.10.10")

    assert state.connected is True
    assert state.host == "172.20.10.10"
    assert state.error is None
    assert state.checked_at is not None
    assert isinstance(connection.controller, FurhatDemoController)
    assert fake_client.connect_calls == 1


def test_connect_passes_auth_key_to_factory():
    received = {}

    def factory(host, auth_key):
        received["host"] = host
        received["auth_key"] = auth_key
        return FakeRealtimeClient()

    connection = RobotConnection(client_factory=factory)

    connection.connect("172.20.10.10", "secret-key")

    assert received == {"host": "172.20.10.10", "auth_key": "secret-key"}


def test_connect_failure_keeps_previous_controller_and_reports_error():
    class RaisingClient:
        def connect(self):
            raise ConnectionError("No route to host")

    connection = RobotConnection(client_factory=lambda host, auth_key: RaisingClient())
    previous_controller = connection.controller

    state = connection.connect("10.0.0.5")

    assert state.connected is False
    assert state.host == "10.0.0.5"
    assert "No route to host" in state.error
    assert connection.controller is previous_controller
    assert isinstance(connection.controller, LoggingDemoController)


def test_default_state_is_disconnected_before_any_connect_attempt():
    connection = RobotConnection()

    assert connection.state.connected is False
    assert connection.state.host is None


def test_connect_enforces_a_hard_deadline_even_if_connect_hangs():
    class SlowClient:
        def connect(self):
            time.sleep(0.5)

    connection = RobotConnection(
        client_factory=lambda host, auth_key: SlowClient(),
        connect_deadline_seconds=0.05,
    )

    start = time.monotonic()
    state = connection.connect("10.255.255.1")
    elapsed = time.monotonic() - start

    assert state.connected is False
    assert "Timed out" in state.error
    assert elapsed < 0.5  # returned well before the slow connect actually finishes


def test_default_realtime_client_factory_constructs_furhat_client():
    fake_instance = MagicMock()

    with patch("furhat_realtime_api.FurhatClient", return_value=fake_instance) as mock_cls:
        result = default_realtime_client_factory("172.20.10.10", "secret-key")

    mock_cls.assert_called_once_with("172.20.10.10", auth_key="secret-key")
    assert result is fake_instance
