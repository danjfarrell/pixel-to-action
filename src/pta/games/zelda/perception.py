"""Zelda-specific perception instances.

Factory functions that construct generic perception modules wired with
Zelda-specific parameters. All game knowledge (HSV ranges, template
paths, regions) lives here. The generic modules in perception/ stay
free of game-specific values.

HSV tuning notes
----------------
Link's green tunic on NES via RetroArch (QuickNES palette):
    Hue:        ~68–85  (yellow-green to green)
    Saturation: ~120–255 (vivid; NES palette is saturated)
    Value:      ~80–200  (not too dark, not blown out)

These are reasonable starting defaults. If detection is unreliable:
    - Run with mask_debug=True (add a cv2.imshow of the mask) to see
      what the threshold is capturing.
    - Use tools/calibrate_region.py to sample pixel colors in HSV.
    - Common failure modes:
        * Hue too wide → picks up green tiles/bushes
        * min_area too small → noise detections
        * min_area too large → misses Link at screen edges

Region note
-----------
The HUD occupies roughly the top 56px of the NES frame (224px tall).
The play area is rows 56–224. Adjust if your capture region differs.
These are expressed in full-frame coordinates of the captured window.
"""

from __future__ import annotations

from pathlib import Path

from perception.color_mask import ColorMaskPerception
from perception.template_match import TemplateMatchPerception

# Asset root — two levels up from games/zelda/ to reach repo root.
_ASSETS = Path(__file__).parent.parent.parent.parent / "assets"

# ---------------------------------------------------------------------------
# HSV defaults for Link's tunic (tune to your palette/emulator settings)
# ---------------------------------------------------------------------------
_LINK_HSV_LOWER = (68, 120, 80)
_LINK_HSV_UPPER = (85, 255, 200)
_LINK_MIN_AREA = 60   # pixels; Link's sprite is ~16x16 = 256px at 1x

# HUD strip height in pixels (NES: top ~56px are HUD, play area below)
_HUD_HEIGHT = 56


def build_link_detector() -> ColorMaskPerception:
    """Construct a ColorMaskPerception tuned for Link's green tunic.

    Searches the full frame. Once HSV range is validated, narrow to
    the play area by passing a region to exclude the HUD strip.

    Returns:
        ColorMaskPerception instance ready to call .process(frame).
    """
    return ColorMaskPerception(
        hsv_lower=_LINK_HSV_LOWER,
        hsv_upper=_LINK_HSV_UPPER,
        min_area=_LINK_MIN_AREA,
        region=None,
    )


def build_hud_detector() -> TemplateMatchPerception:
    """Construct a TemplateMatchPerception for the Zelda HUD hearts.

    Returns:
        TemplateMatchPerception instance for heart_full / heart_half.
    """
    templates = {
        "heart_full": _ASSETS / "templates" / "heart_full.png",
        "heart_half": _ASSETS / "templates" / "heart_half.png",
    }
    return TemplateMatchPerception(
        templates=templates,
        threshold=0.85,
    )
