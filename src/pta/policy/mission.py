"""Mission planning layer.

Provides generic Task and MissionPlan dataclasses for hierarchical
goal decomposition. Analogous to a mission plan in an autonomous
aerospace or robotics system — an ordered sequence of objectives,
each with entry and success conditions evaluated against world state.

Game-specific mission definitions live in games/<game>/mission.py.
This module has no knowledge of any particular game.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Optional

from policy.base import GameState

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """A single named objective within a mission plan.

    Attributes:
        name:    Human-readable label (e.g. "get_wooden_sword").
        success: Callable that returns True when the task is complete.
        entry:   Callable that returns True when the task may be started.
                 Defaults to always-ready. Use this to gate tasks on
                 preconditions (e.g. previous task's side-effects).

    Both callables receive the current GameState and return bool.

    Aerospace analogy: a waypoint with arrival criteria and an
    activation condition (e.g. "begin descent only after cruise
    altitude reached").
    """

    name: str
    success: Callable[[GameState], bool]
    entry: Callable[[GameState], bool] = field(
        default_factory=lambda: (lambda state: True)
    )

    def is_complete(self, state: GameState) -> bool:
        """Return True if the success condition is met."""
        try:
            return bool(self.success(state))
        except Exception:
            logger.exception("Task '%s' success check raised an error", self.name)
            return False

    def is_ready(self, state: GameState) -> bool:
        """Return True if the entry condition allows this task to start."""
        try:
            return bool(self.entry(state))
        except Exception:
            logger.exception("Task '%s' entry check raised an error", self.name)
            return False

    def __repr__(self) -> str:
        return f"Task(name={self.name!r})"


@dataclass
class MissionPlan:
    """An ordered sequence of Tasks representing a complete mission.

    The plan maintains a cursor pointing to the currently active task.
    On each call to tick(), it checks whether the active task is complete
    and advances to the next one if so.

    Aerospace analogy: a flight plan with sequential waypoints. The
    autopilot executes the current leg; the mission manager advances
    to the next leg when the arrival criterion is satisfied.

    Attributes:
        name:   Human-readable mission label.
        tasks:  Ordered list of Task objects.
    """

    name: str
    tasks: list[Task]
    _cursor: int = field(default=0, init=False, repr=False)

    def active_task(self) -> Optional[Task]:
        """Return the current Task, or None if the mission is complete."""
        if self._cursor < len(self.tasks):
            return self.tasks[self._cursor]
        return None

    def is_complete(self) -> bool:
        """Return True when all tasks have been completed."""
        return self._cursor >= len(self.tasks)

    def tick(self, state: GameState) -> None:
        """Advance the mission cursor if the active task is complete.

        Call once per policy cycle before querying active_task().

        Args:
            state: Current GameState from the state builder.
        """
        while self._cursor < len(self.tasks):
            task = self.tasks[self._cursor]
            if task.is_complete(state):
                logger.info(
                    "Mission '%s': task '%s' complete — advancing",
                    self.name,
                    task.name,
                )
                self._cursor += 1
            else:
                break

    def reset(self) -> None:
        """Restart the mission from the first task."""
        logger.info("Mission '%s': reset to task 0", self.name)
        self._cursor = 0

    def status(self) -> str:
        """Return a short human-readable status string."""
        if self.is_complete():
            return f"[{self.name}] COMPLETE"
        task = self.active_task()
        return f"[{self.name}] {self._cursor + 1}/{len(self.tasks)}: {task.name}"

    def __repr__(self) -> str:
        return (
            f"MissionPlan(name={self.name!r}, "
            f"tasks={len(self.tasks)}, "
            f"cursor={self._cursor})"
        )
