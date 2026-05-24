"""Zelda-specific state builder.

Converts perception detections into a structured GameState for
The Legend of Zelda (NES). This is the only module allowed to know
Zelda-specific concepts — the rest of the pipeline stays generic.

Expected perception result keys
--------------------------------
From HUD detector (TemplateMatchPerception):
    detections with label "heart_full" or "heart_half"

From Link detector (ColorMaskPerception):
    detections with keys "centroid", "bbox", "area"

Both detectors feed into a single merged PerceptionResult dict before
being passed to build(). See main.py wiring notes below.

Wiring note
-----------
Two perception modules now run per frame. The results are merged at
the main loop level by combining their "detections" lists under a
shared PerceptionResult. Alternatively, run each module separately and
pass both results to build() — handled via the optional second arg.

For now, build() accepts a single merged result where detections may
contain both heart entries (label key) and link entries (centroid key).
This keeps the StateBuilder interface unchanged (single dict in).
"""

from __future__ import annotations

from state.base import StateBuilder, GameState
from perception.base import PerceptionResult


MAX_HEARTS = 16


class ZeldaStateBuilder(StateBuilder):
    """Interprets merged perception output in terms of Zelda game concepts.

    Tracks:
        hearts_full  (int):         Full heart containers detected.
        hearts_half  (int):         Half heart containers detected.
        health_ratio (float):       Approximate health fraction.
        link_pos     (list|None):   [x, y] centroid of Link in frame coords,
                                    or None if not detected this frame.

    Perception detection shapes recognized:
        Heart:  {"label": "heart_full"|"heart_half", "bbox": [...], ...}
        Link:   {"centroid": [x, y], "bbox": [...], "area": float}
    """

    def build(self, perception_result: PerceptionResult) -> GameState:
        """Build a Zelda GameState from a merged perception result.

        Args:
            perception_result: Combined output from HUD + Link detectors.

        Returns:
            GameState with keys:
                hearts_full  (int)
                hearts_half  (int)
                health_ratio (float)
                link_pos     (list[int, int] | None)
        """
        detections = perception_result.get("detections", [])

        hearts_full = sum(1 for d in detections if d.get("label") == "heart_full")
        hearts_half = sum(1 for d in detections if d.get("label") == "heart_half")

        health_ratio = min(
            (hearts_full + 0.5 * hearts_half) / MAX_HEARTS,
            1.0,
        )

        # Link position: take the largest blob (first after area sort).
        link_detections = [d for d in detections if "centroid" in d]
        link_pos = link_detections[0]["centroid"] if link_detections else None

        return {
            "hearts_full":  hearts_full,
            "hearts_half":  hearts_half,
            "health_ratio": round(health_ratio, 3),
            "link_pos":     link_pos,
        }
