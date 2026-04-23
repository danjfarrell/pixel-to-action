"""Controller base classes for the action execution layer.

A Controller receives an Action from a Policy and translates it
into hardware-level input (keypresses, mouse events, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from policy.base import Action


class ControllerBase(ABC):
    """Abstract base for all controllers."""

    @abstractmethod
    def execute(self, action: Action) -> None:
        """Execute an action.

        Args:
            action: Output of a Policy.decide() call.
        """

    def reset(self) -> None:
        """Optional: reset any controller state between episodes."""


class NullController(ControllerBase):
    """Silently discards all actions. Useful as a placeholder."""

    def execute(self, action: Action) -> None:
        pass