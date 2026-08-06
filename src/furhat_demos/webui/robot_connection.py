from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from furhat_demos.config import build_llm_client
from furhat_demos.control import (
    DemoController,
    FurhatDemoController,
    LoggingDemoController,
    RemoteApi,
)

logger = logging.getLogger(__name__)

PROBE_TIMEOUT_SECONDS = 3.0

# The Furhat Remote API's HTTP client retries a failed connection attempt
# internally (observed: ~3 attempts against an unreachable host), so
# PROBE_TIMEOUT_SECONDS alone does not bound total wall-clock time -- an
# unreachable-but-not-actively-refusing host can hang well past it. This is
# a hard deadline enforced independently of that retry behavior, so
# connect() always returns in bounded time regardless.
PROBE_DEADLINE_SECONDS = 5.0

# A shared, never-shut-down pool: if a probe exceeds the deadline, its thread
# is abandoned (the underlying call can't be cancelled once it's blocked on
# network I/O) rather than blocking connect() until it finishes.
_PROBE_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="robot-probe")


class RemoteApiFactory(Protocol):
    def __call__(self, host: str) -> RemoteApi: ...


def default_remote_api_factory(host: str) -> RemoteApi:
    from furhat_remote_api import FurhatRemoteAPI

    return FurhatRemoteAPI(host)


def default_probe(remote_api: RemoteApi) -> None:
    """Raises if the robot isn't reachable. A cheap, side-effect-free call."""
    remote_api.get_voices(_request_timeout=PROBE_TIMEOUT_SECONDS)


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
        remote_api_factory: RemoteApiFactory = default_remote_api_factory,
        probe: Callable[[RemoteApi], None] = default_probe,
        probe_deadline_seconds: float = PROBE_DEADLINE_SECONDS,
    ) -> None:
        self.controller: DemoController = LoggingDemoController()
        self.state = RobotConnectionState()
        self._remote_api_factory = remote_api_factory
        self._probe = probe
        self._probe_deadline_seconds = probe_deadline_seconds

    def connect(self, host: str) -> RobotConnectionState:
        remote_api = self._remote_api_factory(host)
        future = _PROBE_EXECUTOR.submit(self._probe, remote_api)
        try:
            future.result(timeout=self._probe_deadline_seconds)
        except FutureTimeoutError:
            error = f"Timed out after {self._probe_deadline_seconds:.0f}s trying to reach {host}"
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

        self.controller = FurhatDemoController(remote_api, llm_client=build_llm_client())
        self.state = RobotConnectionState(
            host=host, connected=True, error=None, checked_at=_now_iso()
        )
        return self.state
