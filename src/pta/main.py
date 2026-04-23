# """Pixel-to-Action entry point.

# Runs the first three stages of the autonomy pipeline:
#     ScreenCapture -> PerceptionModule -> StateBuilder

# Current wiring:
#     - TemplateMatchPerception with a single test template
#     - NullStateBuilder (placeholder until state module is implemented)

# Controls:
#     - Q : quit
# """

# from pathlib import Path

# import cv2

# from capture.screen_capture import ScreenCapture
# from perception.template_match import TemplateMatchPerception
# from state.base import NullStateBuilder

# TEMPLATE_PATH = Path("assets/templates/heart_full.png")
# CONFIDENCE_THRESHOLD = 0.85

# # Restrict capture to the emulator window — update these values to match
# # the actual position and size of your emulator on screen.
# EMULATOR_REGION = None  # e.g. (100, 50, 512, 480)


# def main() -> None:
#     capture = ScreenCapture(region=EMULATOR_REGION)

#     perception = TemplateMatchPerception(
#         templates={"heart_full": TEMPLATE_PATH},
#         threshold=CONFIDENCE_THRESHOLD,
#         region=None,  # set to HUD sub-region once emulator bounds are known
#     )

#     state_builder = NullStateBuilder()

#     print("Running — press Q in the capture window to quit.")

#     while True:
#         frame = capture.get_frame()
#         result = perception.process(frame)
#         state = state_builder.build(result)

#         # Debug output — replace with structured logging later.
#         detected = result["feature_detected"]
#         count = len(result["detections"])
#         print(f"detected={detected}  matches={count}  state={state}")

#         # Minimal display so we can see what the agent sees.
#         cv2.imshow("Pixel-to-Action", frame)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     capture.close()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()

"""pixel-to-action entry point.

Configuration is driven by the CONFIG dict below.
Swap in real components by editing CONFIG — defaults to safe no-op mode.
"""

from __future__ import annotations

import logging
import time

import cv2

from capture.screen_capture import ScreenCapture
from control.base import NullController
from control.keyboard_controller import KeyboardController  # noqa: F401 — available for config
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
}
# -----------------------------------------------------------------------------


def main() -> None:
    capture = ScreenCapture(region=CONFIG["region"])
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
            state = state_builder.update(result)
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