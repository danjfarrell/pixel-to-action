"""Zelda-specific policy.

Reacts to game state produced by ZeldaStateBuilder, consulting the
active MissionPlan task to determine current objective context.

Policy structure
----------------
Each decide() call:
  1. Ticks the mission plan (advances cursor if active task is complete).
  2. Reads the active task name to determine behavioral mode.
  3. Applies task-appropriate rules and returns an Action.

This is a single flat policy for now. As task behaviors grow in
complexity each task will delegate to its own sub-policy or behavior
tree node. The mission plan layer is already in place for that.

Aerospace analogy: the mission manager selects the active flight phase
(taxi, takeoff, cruise, approach); the autopilot executes the
phase-specific control law.
"""

from __future__ import annotations

import logging

from policy.base import Action, GameState, NULL_ACTION, PolicyBase
from policy.mission import MissionPlan
from games.zelda.mission import build_zelda_mission

logger = logging.getLogger(__name__)

LOW_HEALTH_THRESHOLD = 0.25


class ZeldaPolicy(PolicyBase):
    """Rule-based policy for The Legend of Zelda.

    Args:
        mission: MissionPlan to follow. Defaults to the standard
                 opening mission built by build_zelda_mission().
                 Pass a custom plan for testing or alternative routes.

    Current behavior per task
    -------------------------
    get_wooden_sword:
        - Low health warning still fires (can die before getting sword).
        - Returns NULL_ACTION (movement not yet implemented).

    reach_dungeon_1, find_boomerang, defeat_aquamentus:
        - Stubs — return NULL_ACTION until navigation/combat implemented.

    All tasks:
        - health_ratio < LOW_HEALTH_THRESHOLD logs a warning.
        - Mission status is logged at INFO on every task transition.
    """

    def __init__(self, mission: MissionPlan | None = None) -> None:
        self._mission = mission or build_zelda_mission()
        logger.info("ZeldaPolicy initialized | %s", self._mission.status())

    def decide(self, state: GameState) -> Action:
        # Advance mission cursor if the active task just completed.
        self._mission.tick(state)

        # Cross-cutting concern: low health check applies regardless of task.
        health_ratio = state.get("health_ratio", 1.0)
        if health_ratio < LOW_HEALTH_THRESHOLD:
            logger.warning(
                "Low health | health_ratio=%.2f | task=%s",
                health_ratio,
                self._mission.active_task(),
            )

        # Mission complete — nothing left to do.
        if self._mission.is_complete():
            logger.info("Mission complete.")
            return NULL_ACTION

        task = self._mission.active_task()

        # Dispatch to task-specific behavior.
        handler = self._TASK_HANDLERS.get(task.name, self._handle_unknown)
        return handler(self, state)

    # ------------------------------------------------------------------
    # Task handlers
    # ------------------------------------------------------------------

    def _handle_get_wooden_sword(self, state: GameState) -> Action:
        """Navigate to and enter the starting cave to collect the sword."""
        # Stub: navigation not yet implemented.
        return NULL_ACTION

    def _handle_reach_dungeon_1(self, state: GameState) -> Action:
        """Navigate the overworld to Dungeon 1 entrance."""
        # Stub: grid navigation not yet implemented.
        return NULL_ACTION

    def _handle_find_boomerang(self, state: GameState) -> Action:
        """Explore Dungeon 1 and pick up the boomerang."""
        # Stub: dungeon navigation not yet implemented.
        return NULL_ACTION

    def _handle_defeat_aquamentus(self, state: GameState) -> Action:
        """Execute combat behavior against the Dungeon 1 boss."""
        # Stub: combat not yet implemented.
        return NULL_ACTION

    def _handle_unknown(self, state: GameState) -> Action:
        active = self._mission.active_task()
        logger.warning("No handler for task '%s' — returning NULL_ACTION", active)
        return NULL_ACTION

    # Map task names to handler methods.
    _TASK_HANDLERS: dict = {
        "get_wooden_sword":  _handle_get_wooden_sword,
        "reach_dungeon_1":   _handle_reach_dungeon_1,
        "find_boomerang":    _handle_find_boomerang,
        "defeat_aquamentus": _handle_defeat_aquamentus,
    }

    def reset(self) -> None:
        """Reset mission and any internal state between episodes."""
        self._mission.reset()
