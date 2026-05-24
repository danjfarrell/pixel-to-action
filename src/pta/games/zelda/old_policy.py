"""Zelda-specific policy.

Reacts to game state produced by ZeldaStateBuilder.
"""

from __future__ import annotations

import logging

from policy.base import Action, GameState, NULL_ACTION, PolicyBase

logger = logging.getLogger(__name__)

LOW_HEALTH_THRESHOLD = 0.25


class ZeldaPolicy(PolicyBase):
    """Rule-based policy for The Legend of Zelda.

    Current behavior:
        - health_ratio < 0.25 -> log a warning, return NULL_ACTION
        - otherwise           -> return NULL_ACTION
    """

    def decide(self, state: GameState) -> Action:
        health_ratio = state.get("health_ratio", 1.0)

        if health_ratio < LOW_HEALTH_THRESHOLD:
            logger.warning("Low health detected: health_ratio=%.2f", health_ratio)

        return NULL_ACTION