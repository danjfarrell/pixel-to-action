"""pixel-to-action entry point.

Configuration is driven by the CONFIG dict below.
Swap in real components by editing CONFIG - defaults to safe no-op mode.
"""

from __future__ import annotations

import logging
import time

import cv2
import pygetwindow as gw
import win32gui

from capture.screen_capture import ScreenCapture
from control.base import NullController
from control.keyboard_controller import KeyboardController  # noqa: F401 - available for config
from perception.base import NullPerception
from perception.template_match import TemplateMatchPerception  # noqa: F401
from policy.base import NullPolicy
from games.zelda.policy import ZeldaPolicy  # noqa: F401
from games.zelda.state import ZeldaStateBuilder
from state.base import NullStateBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration -----------------------------------------------------------
# Default: safe no-op mode. Nothing is sent to the keyboard.
#
# To run with real Zelda components, replace with:
#   "perception": TemplateMatchPerception(templates={...}),
#   "state":      ZeldaStateBuilder(),
#   "policy":     ZeldaPolicy(),
#   "controller": KeyboardController(),
#
CONFIG = {
    "perception": NullPerception(),
    "state":      NullStateBuilder(),
    "policy":     NullPolicy(),
    "controller": NullController(),
    "target_fps": 30,
    "region":     None,  # (x, y, w, h) or None for full screen
    "auto_detect_emulator": True,       # set False to use capture_region instead
    "emulator_title": "RetroArch",
}
# -----------------------------------------------------------------------------

def get_emulator_region(title: str) -> tuple:
    wins = gw.getWindowsWithTitle(title)
    if not wins:
        raise RuntimeError(f"Window '{title}' not found - is it running?")
    win = wins[0]
    win.activate()
    time.sleep(0.1)

    hwnd = win32gui.FindWindow(None, win.title)
    rect = win32gui.GetClientRect(hwnd)          # (0, 0, width, height) relative
    point = win32gui.ClientToScreen(hwnd, (0, 0)) # top-left in screen coords
    left_offset = 10    # trim left edge
    top_offset = 30     # trim title bar + menu bar
    x, y = point
    w = rect[2]
    h = rect[3] 
    logger.info(f"Detected '{CONFIG['emulator_title']}' at region {x, y, w, h}")

    return (x, y, w, h)

def main() -> None:

    # Resolve capture region
    if CONFIG["auto_detect_emulator"]:
        region = get_emulator_region(CONFIG["emulator_title"])
        logger.info(f"Detected '{CONFIG['emulator_title']}' at region {region}")
    else:
        region = CONFIG["region"]  # may be None (full screen)
    capture = ScreenCapture(region=region)
    logger.info(f"ScreenCapture region: {capture._region}")
    perception = CONFIG["perception"]
    state_builder = CONFIG["state"]
    policy = CONFIG["policy"]
    controller = CONFIG["controller"]

    target_fps = CONFIG["target_fps"]
    frame_duration = 1.0 / target_fps

    logger.info("Starting loop at %d FPS", target_fps)

    try:
        while True:
            t0 = time.monotonic()

            frame = capture.get_frame()
            result = perception.process(frame)
            state = state_builder.build(result)
            action = policy.decide(state)
            controller.execute(action)

            cv2.imshow("pixel-to-action", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            elapsed = time.monotonic() - t0
            sleep_time = frame_duration - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    finally:
        capture.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()