"""Screen capture utilities for the capture layer.

Simple, low-overhead wrapper around mss that returns frames as NumPy arrays.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

try:
    from mss import mss
except ImportError as exc:  # pragma: no cover - import-time feedback is intentional
    raise ImportError(
        "mss is required for ScreenCapture. Install it with: pip install mss"
    ) from exc


Region = Tuple[int, int, int, int]


class ScreenCapture:
    """Capture full-screen or region-limited frames.

    Args:
        region: Optional (x, y, width, height) tuple. If omitted, captures the
            primary monitor.
    """

    def __init__(self, region: Optional[Region] = None) -> None:
        self._sct = mss()
        self._region = region

    def _build_monitor(self, region: Optional[Region] = None) -> dict:
        active_region = region if region is not None else self._region
        if active_region is None:
            # mss uses monitor index 1 for the primary display.
            return self._sct.monitors[1]

        x, y, width, height = active_region
        return {"left": x, "top": y, "width": width, "height": height}

    def get_frame(self, region: Optional[Region] = None) -> np.ndarray:
        """Capture a frame and return it as a BGR NumPy array.

        Args:
            region: Optional override region (x, y, width, height).

        Returns:
            Captured frame as ``np.ndarray`` in BGR channel order.
        """
        monitor = self._build_monitor(region)
        raw = self._sct.grab(monitor)
        frame = np.asarray(raw)
        return frame[:, :, :3]  # Drop alpha channel (BGRA -> BGR)

    def close(self) -> None:
        """Release native screen-capture resources."""
        if self._sct is not None:
            self._sct.close()
            self._sct = None

    def __del__(self) -> None:
        self.close()


if __name__ == "__main__":
    import cv2

    capture = ScreenCapture()

    try:
        while True:
            frame = capture.get_frame()
            cv2.imshow("Screen Capture", frame)

            # Press q to exit.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.close()
        cv2.destroyAllWindows()
