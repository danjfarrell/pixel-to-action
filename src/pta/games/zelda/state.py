"""Zelda-specific state builder.

Converts perception detections into a structured GameState for
The Legend of Zelda (NES). This is the only module allowed to know
Zelda-specific concepts - the rest of the pipeline stays generic.
"""

from __future__ import annotations

from state.base import StateBuilder, GameState
from perception.base import PerceptionResult


# Maximum number of hearts Link can have in the base game.
MAX_HEARTS = 16


class ZeldaStateBuilder(StateBuilder):
    """Interprets perception output in terms of Zelda game concepts.

    Currently tracks:
        hearts_full (int): Number of fully filled heart containers detected.
        hearts_half (int): Number of half-filled heart containers detected.
        health_ratio (float): Approximate health as a fraction of full hearts.

    Expected perception labels:
        "heart_full" - a completely filled heart
        "heart_half" - a half-filled heart

    Any labels not listed above are ignored, making this robust to
    perception modules that detect additional features.
    """

    def build(self, perception_result: PerceptionResult) -> GameState:
        """Build a Zelda GameState from a perception result.

        Args:
            perception_result: Output from PerceptionModule.process().

        Returns:
            GameState with keys:
                hearts_full  (int)   : count of full hearts detected
                hearts_half  (int)   : count of half hearts detected
                health_ratio (float) : (full + 0.5 * half) / MAX_HEARTS
        """
        detections = perception_result.get("detections", [])

        hearts_full = sum(1 for d in detections if d["label"] == "heart_full")
        hearts_half = sum(1 for d in detections if d["label"] == "heart_half")

        health_ratio = min(
            (hearts_full + 0.5 * hearts_half) / MAX_HEARTS,
            1.0,
        )

        return {
            "hearts_full": hearts_full,
            "hearts_half": hearts_half,
            "health_ratio": round(health_ratio, 3),
        }