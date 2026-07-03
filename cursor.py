"""
Handles mouse cursor movement and smoothing.
"""

# Third-party
import pyautogui

# Local modules
from config import SMOOTHENING, FRAME_REDUCTION


class CursorController:
    def __init__(self, smoothening=SMOOTHENING, frame_reduction=FRAME_REDUCTION):
        self.screen_w, self.screen_h = pyautogui.size()
        self.smoothening = smoothening
        self.frame_reduction = frame_reduction
        self.prev_x = 0
        self.prev_y = 0

    def move(self, landmarks, is_dragging, index_folded, w, h):
        """
        Move the cursor based on hand landmark positions.
        """
        if index_folded and not is_dragging:
            return

        tx, ty = landmarks["thumb"]
        ix, iy = landmarks["index"]

        if is_dragging:
            control_x = (ix + tx) // 2
            control_y = (iy + ty) // 2
        else:
            control_x = ix
            control_y = iy

        # Scale coordinates to fit the active control frame area.
        denom_x = w - 2 * self.frame_reduction
        denom_y = h - 2 * self.frame_reduction
        
        # Prevent division by zero errors if frame size is reduced to zero.
        if denom_x <= 0: denom_x = 1
        if denom_y <= 0: denom_y = 1

        mouse_x = ((control_x - self.frame_reduction) / denom_x) * self.screen_w
        mouse_y = ((control_y - self.frame_reduction) / denom_y) * self.screen_h

        # Keep the cursor within monitor bounds.
        mouse_x = max(0, min(self.screen_w, mouse_x))
        mouse_y = max(0, min(self.screen_h, mouse_y))

        # Smooth cursor trajectory to reduce hand tremor jitter.
        curr_x = self.prev_x + (mouse_x - self.prev_x) / self.smoothening
        curr_y = self.prev_y + (mouse_y - self.prev_y) / self.smoothening

        pyautogui.moveTo(curr_x, curr_y)
        self.prev_x, self.prev_y = curr_x, curr_y
