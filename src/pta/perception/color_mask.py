"""Color mask perception module.

Detects the presence and position of a colored object in a frame using
HSV thresholding and blob analysis. Animation-invariant — works regardless
of sprite pose or frame, as long as the target color is consistent.

Game-specific HSV ranges and blob parameters live in the game adapter
layer (games/<game>/perception.py), not here.
"""

from __future__ import annotations

import cv2
import numpy as np

from perception.base import PerceptionModule, PerceptionResult


class ColorMaskPerception(PerceptionModule):
    """Detects a colored object by HSV range and returns its centroid.

    Thresholds the frame in HSV space, finds contours, filters by minimum
    blob area, and returns the centroid of the largest qualifying blob as
    the object's position.

    Args:
        hsv_lower:  Lower HSV bound as (H, S, V). H in [0, 179].
        hsv_upper:  Upper HSV bound as (H, S, V).
        min_area:   Minimum contour area in pixels. Blobs smaller than
                    this are discarded as noise. Default 50.
        region:     Optional (x, y, w, h) crop applied before masking.
                    Bboxes and centroids are always returned in full-frame
                    coordinates regardless of crop. Pass the game area
                    minus the HUD strip to avoid false matches.

    Example::

        detector = ColorMaskPerception(
            hsv_lower=(40, 80, 80),
            hsv_upper=(80, 255, 255),
            min_area=80,
            region=(0, 48, 256, 432),  # exclude top HUD strip
        )
        result = detector.process(frame)
    """

    def __init__(
        self,
        hsv_lower: tuple[int, int, int],
        hsv_upper: tuple[int, int, int],
        min_area: int = 50,
        region: tuple[int, int, int, int] | None = None,
    ) -> None:
        self._lower = np.array(hsv_lower, dtype=np.uint8)
        self._upper = np.array(hsv_upper, dtype=np.uint8)
        self._min_area = min_area
        self._region = region

    def process(self, frame: np.ndarray) -> PerceptionResult:
        """Detect the target color blob in the frame.

        Args:
            frame: Full BGR frame from ScreenCapture.

        Returns:
            PerceptionResult with keys:
                feature_detected (bool): True if at least one blob found.
                detections (list[dict]): One entry per qualifying blob,
                    sorted largest-first:
                    - centroid (list):   [x, y] in full-frame coordinates.
                    - bbox (list):       [x, y, w, h] in full-frame coords.
                    - area (float):      Contour area in pixels.
                metadata (dict):
                    - region (list|None): Crop region applied, if any.
                    - blobs_found (int):  Number of qualifying blobs.
                    - mask_coverage (float): Fraction of search area masked.
        """
        search_frame, offset_x, offset_y = self._apply_region(frame)

        hsv = cv2.cvtColor(search_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self._lower, self._upper)

        # Light morphological cleanup to remove single-pixel noise.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self._min_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"]) + offset_x
            cy = int(M["m01"] / M["m00"]) + offset_y

            detections.append({
                "centroid": [cx, cy],
                "bbox": [x + offset_x, y + offset_y, w, h],
                "area": round(float(area), 1),
            })

        # Largest blob first — caller typically wants the dominant match.
        detections.sort(key=lambda d: d["area"], reverse=True)

        total_pixels = search_frame.shape[0] * search_frame.shape[1]
        mask_coverage = float(np.count_nonzero(mask)) / total_pixels if total_pixels else 0.0

        return {
            "feature_detected": len(detections) > 0,
            "detections": detections,
            "metadata": {
                "region": list(self._region) if self._region else None,
                "blobs_found": len(detections),
                "mask_coverage": round(mask_coverage, 4),
            },
        }

    def _apply_region(
        self, frame: np.ndarray
    ) -> tuple[np.ndarray, int, int]:
        """Crop to region and return (cropped_frame, offset_x, offset_y)."""
        if self._region is None:
            return frame, 0, 0
        x, y, w, h = self._region
        return frame[y: y + h, x: x + w], x, y
