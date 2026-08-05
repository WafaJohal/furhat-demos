from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class DemoController(Protocol):
    def start_demo(self, demo_id: str, option_id: str) -> None: ...


class LoggingDemoController:
    def start_demo(self, demo_id: str, option_id: str) -> None:
        logger.info("start_demo requested: demo_id=%s option_id=%s", demo_id, option_id)
