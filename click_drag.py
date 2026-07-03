"""
Handles click and drag gestures using thumb-index pinch detection.
"""

# Third-party
import pyautogui

# Local modules
from config import PINCH_START_THRESHOLD, PINCH_RELEASE_THRESHOLD, CLICK_COOLDOWN, PINCH_DRAG_DELAY


class ClickDragController:
    def __init__(self, pinch_start_threshold=PINCH_START_THRESHOLD, pinch_release_threshold=PINCH_RELEASE_THRESHOLD, click_cooldown=CLICK_COOLDOWN, pinch_drag_delay=PINCH_DRAG_DELAY):
        self.pinch_start_threshold = pinch_start_threshold
        self.pinch_release_threshold = pinch_release_threshold
        self.click_cooldown = click_cooldown
        self.pinch_drag_delay = pinch_drag_delay
        
        self.is_dragging = False
        self.is_pinched = False
        self.pinch_start_time = 0.0
        self.last_click_time = 0.0

    def update(self, click_distance, thumb_folded, index_folded, current_time):
        """
        Update the click/drag state machine.
        """
        if self.is_dragging:
            # Release drag once distance exceeds threshold or hand posture changes.
            if click_distance > self.pinch_release_threshold or thumb_folded or index_folded:
                pyautogui.mouseUp()
                self.is_dragging = False
                self.is_pinched = False
        else:
            # Start tracking a pinch if fingertips are close enough.
            if click_distance < self.pinch_start_threshold:
                if not self.is_pinched:
                    self.is_pinched = True
                    self.pinch_start_time = current_time
                else:
                    hold_time = current_time - self.pinch_start_time
                    # Transition to drag if pinch is held long enough.
                    if hold_time > self.pinch_drag_delay:
                        pyautogui.mouseDown()
                        self.is_dragging = True
            else:
                # Handle pinch release logic.
                if self.is_pinched:
                    hold_time = current_time - self.pinch_start_time
                    # Trigger a click if the pinch was brief (non-drag gesture).
                    if hold_time < self.pinch_drag_delay:
                        if current_time - self.last_click_time > self.click_cooldown:
                            pyautogui.click()
                            self.last_click_time = current_time
                    self.is_pinched = False
