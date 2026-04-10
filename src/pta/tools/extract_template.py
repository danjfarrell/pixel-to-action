"""Template extraction utility.

Interactive tool for capturing a frame and selecting a region to save
as a template image. Run this standalone to build up the assets/templates
directory without leaving Python.

Usage:
    python tools/extract_template.py --output assets/templates/heart_full.png

Controls:
    - Click and drag to draw a selection rectangle
    - Press ENTER or SPACE to save the selected region
    - Press R to reset the selection and try again
    - Press Q or ESC to quit without saving
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from pta.capture.screen_capture import ScreenCapture


# ------------------------------------------------------------------
# Selection state — shared between mouse callback and main loop
# ------------------------------------------------------------------

class _Selection:
    """Tracks the current drag rectangle in pixel coordinates."""

    def __init__(self) -> None:
        self.start: tuple[int, int] | None = None
        self.end: tuple[int, int] | None = None
        self.dragging: bool = False

    def reset(self) -> None:
        self.start = None
        self.end = None
        self.dragging = False

    @property
    def ready(self) -> bool:
        """True when a completed (non-zero-area) rectangle exists."""
        return (
            self.start is not None
            and self.end is not None
            and not self.dragging
            and self.start != self.end
        )

    def to_rect(self) -> tuple[int, int, int, int]:
        """Return (x, y, w, h) with top-left origin, regardless of drag direction."""
        x0, y0 = self.start
        x1, y1 = self.end
        x = min(x0, x1)
        y = min(y0, y1)
        w = abs(x1 - x0)
        h = abs(y1 - y0)
        return x, y, w, h


def _make_mouse_callback(sel: _Selection):
    """Return an OpenCV mouse callback that writes into sel."""

    def callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            sel.start = (x, y)
            sel.end = (x, y)
            sel.dragging = True

        elif event == cv2.EVENT_MOUSEMOVE and sel.dragging:
            sel.end = (x, y)

        elif event == cv2.EVENT_LBUTTONUP and sel.dragging:
            sel.end = (x, y)
            sel.dragging = False

    return callback


# ------------------------------------------------------------------
# Drawing helpers
# ------------------------------------------------------------------

def _draw_overlay(frame: np.ndarray, sel: _Selection) -> np.ndarray:
    """Return a copy of frame with the selection rectangle drawn on it."""
    display = frame.copy()
    if sel.start and sel.end:
        x, y, w, h = sel.to_rect()
        cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{w} x {h} px"
        cv2.putText(
            display, label,
            (x, max(y - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA,
        )
    _draw_instructions(display)
    return display


def _draw_instructions(frame: np.ndarray) -> None:
    """Overlay control hints in the top-left corner (in-place)."""
    lines = [
        "Drag to select region",
        "ENTER / SPACE : save",
        "R : reset",
        "Q / ESC : quit",
    ]
    for i, text in enumerate(lines):
        cv2.putText(
            frame, text,
            (8, 18 + i * 18),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
        )


# ------------------------------------------------------------------
# Save helper
# ------------------------------------------------------------------

def _save_crop(frame: np.ndarray, sel: _Selection, output_path: Path) -> bool:
    """Crop the selected region and write it to disk.

    Returns True on success, False if the selection is invalid.
    """
    if not sel.ready:
        print("No valid selection to save.")
        return False

    x, y, w, h = sel.to_rect()
    crop = frame[y : y + h, x : x + w]

    if crop.size == 0:
        print("Selection has zero area — nothing to save.")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), crop)
    print(f"Saved {w}x{h} template -> {output_path}")
    return True


# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------

def run(output_path: Path, region: tuple[int, int, int, int] | None = None) -> None:
    """Capture a frame, let the user select a region, and save it.

    Args:
        output_path: Where to write the cropped template PNG.
        region:      Optional (x, y, w, h) to restrict the capture area
                     to the emulator window.
    """
    capture = ScreenCapture(region=region)
    frame = capture.get_frame()
    capture.close()

    sel = _Selection()

    window = "Template Extractor"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window, _make_mouse_callback(sel))

    print("Frame captured. Draw a selection rectangle, then press ENTER to save.")

    while True:
        display = _draw_overlay(frame, sel)
        cv2.imshow(window, display)

        key = cv2.waitKey(16) & 0xFF  # ~60 fps refresh

        if key in (13, 32):  # ENTER or SPACE
            if _save_crop(frame, sel, output_path):
                break
            else:
                print("Make a selection first.")

        elif key == ord("r"):
            sel.reset()
            print("Selection reset.")

        elif key in (ord("q"), 27):  # Q or ESC
            print("Quit without saving.")
            break

    cv2.destroyAllWindows()


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture a screen frame and save a cropped region as a template."
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("assets/templates/template.png"),
        help="Output path for the saved template (default: assets/templates/template.png)",
    )
    parser.add_argument(
        "--region", "-r",
        type=int,
        nargs=4,
        metavar=("X", "Y", "W", "H"),
        default=None,
        help="Restrict capture to this screen region: X Y W H",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    region = tuple(args.region) if args.region else None
    run(output_path=args.output, region=region)
