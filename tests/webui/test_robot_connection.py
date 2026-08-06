import time
from unittest.mock import MagicMock, patch

from furhat_demos.control import FurhatDemoController, LoggingDemoController
from furhat_demos.webui.robot_connection import RobotConnection, default_remote_api_factory


class FakeRemoteApi:
    def __init__(self):
        self.get_voices_calls: list[dict] = []

    def get_voices(self, **kwargs):
        self.get_voices_calls.append(kwargs)
        return []


def test_connect_success_swaps_controller_and_reports_connected():
    fake_remote_api = FakeRemoteApi()
    connection = RobotConnection(
        remote_api_factory=lambda host: fake_remote_api,
        probe=lambda remote_api: None,
    )

    state = connection.connect("172.20.10.10")

    assert state.connected is True
    assert state.host == "172.20.10.10"
    assert state.error is None
    assert state.checked_at is not None
    assert isinstance(connection.controller, FurhatDemoController)


def test_connect_failure_keeps_previous_controller_and_reports_error():
    connection = RobotConnection(
        remote_api_factory=lambda host: object(),
        probe=lambda remote_api: (_ for _ in ()).throw(ConnectionError("No route to host")),
    )
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


def test_default_probe_calls_get_voices_with_bounded_timeout():
    from furhat_demos.webui.robot_connection import PROBE_TIMEOUT_SECONDS, default_probe

    fake_remote_api = FakeRemoteApi()

    default_probe(fake_remote_api)

    assert fake_remote_api.get_voices_calls == [{"_request_timeout": PROBE_TIMEOUT_SECONDS}]


def test_connect_enforces_a_hard_deadline_even_if_the_probe_hangs():
    def slow_probe(remote_api):
        time.sleep(0.5)

    connection = RobotConnection(
        remote_api_factory=lambda host: object(),
        probe=slow_probe,
        probe_deadline_seconds=0.05,
    )

    start = time.monotonic()
    state = connection.connect("10.255.255.1")
    elapsed = time.monotonic() - start

    assert state.connected is False
    assert "Timed out" in state.error
    assert elapsed < 0.5  # returned well before the slow probe actually finished


def test_default_remote_api_factory_constructs_furhat_remote_api():
    fake_instance = MagicMock()

    with patch("furhat_remote_api.FurhatRemoteAPI", return_value=fake_instance) as mock_cls:
        result = default_remote_api_factory("172.20.10.10")

    mock_cls.assert_called_once_with("172.20.10.10")
    assert result is fake_instance
