"""Pixel-to-Action entry point.

Runs the first three stages of the autonomy pipeline:
    ScreenCapture -> PerceptionModule -> StateBuilder

Current wiring:
    - TemplateMatchPerception with a single test template
    - NullStateBuilder (placeholder until state module is implemented)

Controls:
    - Q : quit
"""

from pathlib import Path

import cv2

from capture.screen_capture import ScreenCapture
from perception.template_match import TemplateMatchPerception
from state.base import NullStateBuilder

TEMPLATE_PATH = Path("assets/templates/heart_full.png")
CONFIDENCE_THRESHOLD = 0.85

# Restrict capture to the emulator window — update these values to match
# the actual position and size of your emulator on screen.
EMULATOR_REGION = None  # e.g. (100, 50, 512, 480)


def main() -> None:
    capture = ScreenCapture(region=EMULATOR_REGION)

    perception = TemplateMatchPerception(
        templates={"heart_full": TEMPLATE_PATH},
        threshold=CONFIDENCE_THRESHOLD,
        region=None,  # set to HUD sub-region once emulator bounds are known
    )

    state_builder = NullStateBuilder()

    print("Running — press Q in the capture window to quit.")

    while True:
        frame = capture.get_frame()
        result = perception.process(frame)
        state = state_builder.build(result)

        # Debug output — replace with structured logging later.
        detected = result["feature_detected"]
        count = len(result["detections"])
        print(f"detected={detected}  matches={count}  state={state}")

        # Minimal display so we can see what the agent sees.
        cv2.imshow("Pixel-to-Action", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()