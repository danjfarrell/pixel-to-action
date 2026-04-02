"""Pixel-to-Action entry point.

Runs the first two stages of the autonomy pipeline:
    ScreenCapture -> PerceptionModule -> (state, policy, control coming later)
"""

from capture.screen_capture import ScreenCapture
from perception.base import NullPerception


def main() -> None:
    capture = ScreenCapture()
    perception = NullPerception()

    frame = capture.get_frame()
    result = perception.process(frame)

    print(f"feature_detected : {result['feature_detected']}")
    print(f"detections       : {result['detections']}")
    print(f"metadata         : {result['metadata']}")


if __name__ == "__main__":
    main()