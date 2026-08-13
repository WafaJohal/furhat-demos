from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from furhat_demos.config import build_llm_client
from furhat_demos.control import (
    DemoController,
    FurhatDemoController,
    FurhatRealtimeClient,
    LoggingDemoController,
)

logger = logging.getLogger(__name__)

# The Realtime API client's own connect() has no exposed timeout, and nothing
# guarantees the underlying WebSocket handshake is bounded on an unreachable
# host (see ADR-006 for the equivalent finding against the old Remote API).
# This is a hard deadline enforced independently of that.
CONNECT_DEADLINE_SECONDS = 5.0

# A shared, never-shut-down pool: if a connect attempt exceeds the deadline,
# its thread is abandoned (the underlying call can't be cancelled once it's
# blocked on network I/O) rather than blocking connect() until it finishes.
_CONNECT_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="robot-connect")


class RealtimeClientFactory(Protocol):
    def __call__(self, host: str, auth_key: str | None) -> FurhatRealtimeClient: ...


def default_realtime_client_factory(host: str, auth_key: str | None) -> FurhatRealtimeClient:
    from furhat_realtime_api import FurhatClient

    return FurhatClient(host, auth_key=auth_key)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class RobotConnectionState:
    host: str | None = None
    connected: bool = False
    error: str | None = None
    checked_at: str | None = None


class RobotConnection:
    """Holds the currently active DemoController and connection status, and
    lets it be swapped at runtime (e.g. from the web UI's IP entry) rather
    than being fixed once at app startup."""

    def __init__(
        self,
        client_factory: RealtimeClientFactory = default_realtime_client_factory,
        connect_deadline_seconds: float = CONNECT_DEADLINE_SECONDS,
    ) -> None:
        self.controller: DemoController = LoggingDemoController()
        self.state = RobotConnectionState()
        self._client_factory = client_factory
        self._connect_deadline_seconds = connect_deadline_seconds

    def connect(self, host: str, auth_key: str | None = None) -> RobotConnectionState:
        client = self._client_factory(host, auth_key)
        future = _CONNECT_EXECUTOR.submit(client.connect)
        try:
            future.result(timeout=self._connect_deadline_seconds)
        except FutureTimeoutError:
            error = f"Timed out after {self._connect_deadline_seconds:.0f}s trying to reach {host}"
            logger.warning(error)
            self.state = RobotConnectionState(
                host=host, connected=False, error=error, checked_at=_now_iso()
            )
            return self.state
        except Exception as exc:
            logger.warning("Failed to connect to Furhat at host=%s", host, exc_info=True)
            self.state = RobotConnectionState(
                host=host, connected=False, error=str(exc), checked_at=_now_iso()
            )
            return self.state

        self.controller = FurhatDemoController(client, llm_client=build_llm_client())
        self.state = RobotConnectionState(
            host=host, connected=True, error=None, checked_at=_now_iso()
        )
        return self.state
