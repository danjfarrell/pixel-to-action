from capture.screen_capture import ScreenCapture
import cv2

def main():
    print("Pixel-to-Action")
    print("Status: scaffold created")
    print("current step: implementing screen capture module")
    capture = ScreenCapture()
    frame = capture.get_frame()

    if frame is not None:
        print("Frame captured successfully.")
    else:
        print("Frame capture failed.")


if __name__ == "__main__":
    main()
