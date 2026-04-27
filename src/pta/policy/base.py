"""Policy base classes for the decision-making layer.

A Policy consumes a GameState and returns an Action - a structured
description of what the controller should do next.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

# GameState is whatever the StateBuilder produced.
GameState = Dict[str, Any]

# Action is an open dict. Keys are controller-defined (e.g. "key", "duration").
Action = Dict[str, Any]

# Sentinel for "do nothing".
NULL_ACTION: Action = {"type": "null"}


class PolicyBase(ABC):
    """Abstract base for all policies."""

    @abstractmethod
    def decide(self, state: GameState) -> Action:
        """Return an Action given the current game state.

        Args:
            state: Output of a StateBuilder.

        Returns:
            Action dict consumed by a Controller.
        """

    def reset(self) -> None:
        """Optional: reset any internal policy state between episodes."""


class NullPolicy(PolicyBase):
    """Always returns NULL_ACTION. Useful as a placeholder."""

    def decide(self, state: GameState) -> Action:
        return NULL_ACTION