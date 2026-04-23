"""Keyboard controller using pynput.

Translates Action dicts into real keypresses.

Action schema:
    {
        "type": "key",
        "key": "z",           # any pynput-valid key string
        "duration": 0.05      # seconds to hold (optional, default DEFAULT_DURATION)
    }

    {"type": "null"} is silently ignored.
"""

from __future__ import annotations

import logging
import time

from pynput.keyboard import Controller, KeyCode

from control.base import ControllerBase
from policy.base import Action

logger = logging.getLogger(__name__)

DEFAULT_DURATION = 0.05  # seconds


class KeyboardController(ControllerBase):
    """Sends keypresses via pynput.

    Args:
        default_duration: Hold duration (seconds) used when the action
            dict omits the 'duration' key.
    """

    def __init__(self, default_duration: float = DEFAULT_DURATION) -> None:
        self._kb = Controller()
        self._default_duration = default_duration

    def execute(self, action: Action) -> None:
        action_type = action.get("type")

        if action_type == "null":
            return

        if action_type == "key":
            key_str = action.get("key")
            if not key_str:
                logger.warning("KeyboardController: 'key' action missing 'key' field")
                return

            duration = action.get("duration", self._default_duration)
            key = KeyCode.from_char(key_str)

            self._kb.press(key)
            time.sleep(duration)
            self._kb.release(key)
            return

        logger.warning("KeyboardController: unknown action type %r", action_type)