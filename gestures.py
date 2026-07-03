"""
Classifies hand gestures based on joint angles and relative distance thresholds.
"""

# Local modules
from config import ZOOM_THRESHOLD, CLICK_GESTURE_THRESHOLD
from utils import is_open_palm


def detect_gesture(
    is_dragging,
    is_pinched,
    thumb_folded,
    index_folded,
    middle_folded,
    ring_folded,
    pinky_folded,
    click_distance,
    index_middle_distance
):

    is_click_gesture = (
        click_distance < CLICK_GESTURE_THRESHOLD or is_dragging or is_pinched
    )

    is_zoom_gesture = (
        index_middle_distance < ZOOM_THRESHOLD and
        not is_click_gesture
    )

    is_rotate_gesture = (
        is_open_palm(
            thumb_folded,
            index_folded,
            middle_folded,
            ring_folded,
            pinky_folded
        )
    )

    if is_rotate_gesture:
        return "ROTATE"

    if is_dragging:
        return "DRAG"

    if is_click_gesture:
        return "CLICK"

    if is_zoom_gesture:
        return "ZOOM"

    return "MOVE"

