"""Base class for the state estimation layer.

Converts raw perception output into a structured world state that the
policy layer can reason about. Perception speaks in detections;
state speaks in game concepts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from perception.base import PerceptionResult


# Structured representation of the world at a single point in time.
# Keys are domain concepts (e.g. "hearts", "enemy_nearby");
# values are whatever type best represents that concept.
GameState = dict[str, Any]


class StateBuilder(ABC):
    """Abstract base class for all state builders.

    Each subclass knows how to interpret a specific game's perception output
    and convert it into a clean GameState dict. The policy layer depends only
    on GameState — it never sees raw detections.

    Subclasses must implement:
        build(perception_result) -> GameState
    """

    @abstractmethod
    def build(self, perception_result: PerceptionResult) -> GameState:
        """Convert a perception result into a structured game state.

        Args:
            perception_result: Output from PerceptionModule.process().

        Returns:
            GameState dict. Keys and value types are defined by the
            concrete subclass and should be documented there.
        """
        raise NotImplementedError


class NullStateBuilder(StateBuilder):
    """Passthrough state builder that returns an empty state.

    Useful as a placeholder while the real state module is being built,
    or in tests where state content does not matter.
    """

    def build(self, perception_result: PerceptionResult) -> GameState:
        """Return an empty but valid GameState.

        Args:
            perception_result: Ignored.

        Returns:
            Empty GameState dict.
        """
        return {}