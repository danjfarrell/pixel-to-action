"""Base class for the perception layer.

Defines the interface that all perception modules must implement.
Downstream modules (state, policy) depend only on this contract,
not on any specific detector implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


# Type alias for the structured output every perception module must return.
# Keys are feature names; values are detection results (bool, float, dict, etc.)
PerceptionResult = dict[str, Any]


class PerceptionModule(ABC):
    """Abstract base class for all perception modules.

    Each subclass wraps one detection strategy (template matching, ML model,
    color thresholding, etc.) and exposes a single process() method.

    Subclasses must implement:
        process(frame) -> PerceptionResult

    The returned dict must always include at minimum:
        {
            "feature_detected": bool,   # True if anything meaningful was found
            "detections":       list,   # Zero or more structured detection records
            "metadata":         dict,   # Optional diagnostics (timing, confidence, etc.)
        }

    Downstream modules (StateBuilder, Policy) rely on this schema and should
    not need to know which detector produced the result.
    """

    @abstractmethod
    def process(self, frame: np.ndarray) -> PerceptionResult:
        """Run detection on a single frame.

        Args:
            frame: BGR image as a NumPy array, shape (H, W, 3).

        Returns:
            PerceptionResult dict conforming to the schema described above.
        """
        raise NotImplementedError


class NullPerception(PerceptionModule):
    """Passthrough perception module that always returns an empty result.

    Useful as a placeholder, a safe default, or in unit tests where
    real detection is not needed.
    """

    def process(self, frame: np.ndarray) -> PerceptionResult:
        """Return a well-formed but empty perception result.

        Args:
            frame: BGR image (not inspected).

        Returns:
            Minimal valid PerceptionResult with no detections.
        """
        return {
            "feature_detected": False,
            "detections": [],
            "metadata": {},
        }