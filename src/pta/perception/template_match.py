"""Template matching perception module.

Detects one or more visual templates within a frame using OpenCV's
normalized cross-correlation. Game-specific knowledge (which templates
to load, what they mean) lives in the game adapter layer, not here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import cv2
import numpy as np

from perception.base import PerceptionModule, PerceptionResult


# A template can be supplied as a file path or a pre-loaded BGR array.
TemplateSource = Union[str, Path, np.ndarray]


class TemplateMatchPerception(PerceptionModule):
    """Detects named templates in a frame using normalized cross-correlation.

    Args:
        templates:  Dict mapping a label (e.g. "heart_full") to either a
                    file path or a pre-loaded BGR NumPy array.
        threshold:  Minimum match confidence in [0.0, 1.0]. Matches below
                    this value are discarded. Default is 0.8.
        region:     Optional (x, y, w, h) tuple to crop the frame before
                    matching. Useful for restricting search to a known HUD
                    area and improving speed.

    Example::

        detector = TemplateMatchPerception(
            templates={"heart_full": "assets/heart_full.png"},
            threshold=0.85,
            region=(0, 0, 256, 64),   # top-left HUD strip
        )
        result = detector.process(frame)
    """

    def __init__(
        self,
        templates: dict[str, TemplateSource],
        threshold: float = 0.8,
        region: tuple[int, int, int, int] | None = None,
    ) -> None:
        if not templates:
            raise ValueError("At least one template must be provided.")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold}.")

        self._threshold = threshold
        self._region = region
        self._templates = self._load_templates(templates)

    # ------------------------------------------------------------------
    # PerceptionModule interface
    # ------------------------------------------------------------------

    def process(self, frame: np.ndarray) -> PerceptionResult:
        """Search for all registered templates in the frame.

        Args:
            frame: Full BGR frame from ScreenCapture.

        Returns:
            PerceptionResult with keys:
                feature_detected (bool): True if at least one match found.
                detections (list[dict]): One entry per match:
                    - label (str):       Template name.
                    - confidence (float): Match score in [0.0, 1.0].
                    - bbox (list):       [x, y, w, h] in frame coordinates.
                metadata (dict):
                    - region (list|None): Crop region applied, if any.
                    - templates_checked (int): Number of templates searched.
        """
        search_frame = self._apply_region(frame)
        offset_x, offset_y = self._region_offset()

        detections = []
        for label, template in self._templates.items():
            matches = self._match(search_frame, template)
            for confidence, (x, y) in matches:
                h, w = template.shape[:2]
                detections.append(
                    {
                        "label": label,
                        "confidence": round(float(confidence), 4),
                        # bbox is always in full-frame coordinates.
                        "bbox": [x + offset_x, y + offset_y, w, h],
                    }
                )

        return {
            "feature_detected": len(detections) > 0,
            "detections": detections,
            "metadata": {
                "region": list(self._region) if self._region else None,
                "templates_checked": len(self._templates),
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_templates(
        self, sources: dict[str, TemplateSource]
    ) -> dict[str, np.ndarray]:
        """Load all templates, converting paths to BGR arrays."""
        loaded: dict[str, np.ndarray] = {}
        for label, source in sources.items():
            if isinstance(source, np.ndarray):
                loaded[label] = source
            else:
                path = Path(source)
                img = cv2.imread(str(path))
                if img is None:
                    raise FileNotFoundError(
                        f"Template '{label}' could not be loaded from: {path}"
                    )
                loaded[label] = img
        return loaded

    def _apply_region(self, frame: np.ndarray) -> np.ndarray:
        """Crop the frame to the configured region, if any."""
        if self._region is None:
            return frame
        x, y, w, h = self._region
        return frame[y : y + h, x : x + w]

    def _region_offset(self) -> tuple[int, int]:
        """Return (x, y) offset to translate crop coords back to frame coords."""
        if self._region is None:
            return 0, 0
        return self._region[0], self._region[1]

    def _match(
        self, frame: np.ndarray, template: np.ndarray
    ) -> list[tuple[float, tuple[int, int]]]:
        """Run matchTemplate and return all hits above the threshold.

        Uses TM_CCOEFF_NORMED so scores are always in [-1.0, 1.0] and
        comparable across templates of different sizes.

        Returns:
            List of (confidence, (x, y)) tuples for each match found.
        """
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= self._threshold)

        hits = []
        for y, x in zip(*locations):
            confidence = result[y, x]
            hits.append((float(confidence), (int(x), int(y))))

        return hits
