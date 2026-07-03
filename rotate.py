"""
Handles Google Earth rotation using open-hand gestures.
"""

# Standard library
import time

# Third-party
import pyautogui

# Local modules
from config import ROTATE_THRESHOLD, ROTATE_SPEED, ROTATE_DELAY


class RotateController:

    def __init__(self, rotate_threshold=ROTATE_THRESHOLD, rotate_speed=ROTATE_SPEED, rotate_delay=ROTATE_DELAY):

        self.is_rotating = False

        self.previous_x = None
        self.previous_y = None

        self.rotate_threshold = rotate_threshold      # Dead zone
        self.rotate_speed = rotate_speed

        self.rotate_delay = rotate_delay         # Hold palm 0.4 sec
        self.rotate_start_time = None

    def update(self, gesture, palm_x, palm_y, current_time):

        # Start tracking when palm is held open.
        if gesture == "ROTATE":

            if self.rotate_start_time is None:
                self.rotate_start_time = current_time
                return

            # Engage drag once duration exceeds delay threshold.
            if (
                not self.is_rotating and
                time.time() - self.rotate_start_time > self.rotate_delay
            ):

                pyautogui.mouseDown()

                self.is_rotating = True

                self.previous_x = palm_x
                self.previous_y = palm_y

                return

            if self.is_rotating:

                dx = palm_x - self.previous_x
                dy = palm_y - self.previous_y

                move_x = 0
                move_y = 0

                # Avoid minor twitch adjustments by checking threshold.
                if abs(dx) > self.rotate_threshold:
                    move_x = int(dx * self.rotate_speed)

                if abs(dy) > self.rotate_threshold:
                    move_y = int(dy * self.rotate_speed)

                if move_x != 0 or move_y != 0:
                    x, y = pyautogui.position()
                    
                    pyautogui.moveTo(
                        x + move_x,
                        y + move_y,
                        duration=0
                        )

                self.previous_x = palm_x
                self.previous_y = palm_y

        # Release rotation hold when exiting rotation posture.
        else:

            self.rotate_start_time = None

            if self.is_rotating:

                pyautogui.mouseUp()

                self.is_rotating = False

                self.previous_x = None
                self.previous_y = None