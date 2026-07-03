"""
Handles Google Earth zoom using index-middle finger gestures.
"""

# Third-party
import pyautogui

# Local modules
from config import ZOOM_SENSITIVITY, ZOOM_SCROLL_AMOUNT, ZOOM_COOLDOWN


class ZoomController:
    def __init__(self, zoom_sensitivity=ZOOM_SENSITIVITY, zoom_scroll_amount=ZOOM_SCROLL_AMOUNT, zoom_cooldown=ZOOM_COOLDOWN):
        self.zoom_sensitivity = zoom_sensitivity
        self.zoom_scroll_amount = zoom_scroll_amount
        self.zoom_cooldown = zoom_cooldown
        
        self.previous_zoom_y = None
        self.last_zoom_time = 0.0

    def scroll(self, middle_y, current_time):
        """
        Perform scroll operations based on the y coordinate movement of the middle finger.
        """
        if self.previous_zoom_y is None:
            self.previous_zoom_y = middle_y
        else:
            delta = middle_y - self.previous_zoom_y
            # Scroll only when motion is significant and cooldown period has passed.
            if abs(delta) > self.zoom_sensitivity and current_time - self.last_zoom_time > self.zoom_cooldown:
                if delta < 0:
                    pyautogui.scroll(self.zoom_scroll_amount)
                else:
                    pyautogui.scroll(-self.zoom_scroll_amount)
                self.last_zoom_time = current_time
                self.previous_zoom_y = middle_y

    def reset(self):
        self.previous_zoom_y = None
