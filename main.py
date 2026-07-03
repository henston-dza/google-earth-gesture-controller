"""
Main entry point executing the gesture controller loop.
"""

# Standard library
import time

# Third-party
import cv2
import mediapipe as mp
import pyautogui

# Local modules
from click_drag import ClickDragController
from config import (
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    CLICK_COOLDOWN,
    FRAME_REDUCTION,
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_COMPLEXITY,
    PINCH_DRAG_DELAY,
    PINCH_RELEASE_THRESHOLD,
    PINCH_START_THRESHOLD,
    ROTATE_DELAY,
    ROTATE_SPEED,
    ROTATE_THRESHOLD,
    SMOOTHENING,
    ZOOM_COOLDOWN,
    ZOOM_SCROLL_AMOUNT,
    ZOOM_SENSITIVITY,
)
from cursor import CursorController
from gestures import detect_gesture
from rotate import RotateController
from utils import get_finger_folding_states, get_landmarks_px
from zoom import ZoomController

# PyAutoGUI configurations
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

WINDOW_TITLE = "Gesture Earth Controller v1.0"

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=MAX_NUM_HANDS,
        model_complexity=MODEL_COMPLEXITY,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE
    )

    # Initialize controllers
    cursor_ctrl = CursorController(
        smoothening=SMOOTHENING,
        frame_reduction=FRAME_REDUCTION
    )
    click_drag_ctrl = ClickDragController(
        pinch_start_threshold=PINCH_START_THRESHOLD,
        pinch_release_threshold=PINCH_RELEASE_THRESHOLD,
        click_cooldown=CLICK_COOLDOWN,
        pinch_drag_delay=PINCH_DRAG_DELAY
    )
    zoom_ctrl = ZoomController(
        zoom_sensitivity=ZOOM_SENSITIVITY,
        zoom_scroll_amount=ZOOM_SCROLL_AMOUNT,
        zoom_cooldown=ZOOM_COOLDOWN
    )
    rotate_ctrl = RotateController(
        rotate_threshold=ROTATE_THRESHOLD,
        rotate_speed=ROTATE_SPEED,
        rotate_delay=ROTATE_DELAY
    )
    prev_time = 0
    show_dashboard = True
    show_landmarks = True

    cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_TITLE, 500, 350)
    cv2.moveWindow(WINDOW_TITLE, 20, 20)
    try:
        cv2.setWindowProperty(WINDOW_TITLE, cv2.WND_PROP_TOPMOST, 1)
    except:
        pass

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read camera.")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        current_time = time.time()
        gesture = "MOVE"

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            
            # Map landmarks to pixel coordinates.
            landmarks = get_landmarks_px(hand, w, h)
            
            # Gather finger posture details.
            thumb_folded, index_folded, middle_folded, ring_folded, pinky_folded, click_distance, middle_distance, index_middle_distance = get_finger_folding_states(landmarks)

            # Draw visual markers on active key points.
            if show_landmarks:
                if not thumb_folded:
                    cv2.circle(frame, landmarks["thumb"], 8, (255, 0, 0), -1)

                if not index_folded:
                    cv2.circle(frame, landmarks["index"], 8, (0, 255, 0), -1)

                if not middle_folded:
                    cv2.circle(frame, landmarks["middle"], 8, (0, 255, 255), -1)

            # Determine matching state based on hand configuration.
            gesture = detect_gesture(
                click_drag_ctrl.is_dragging,
                click_drag_ctrl.is_pinched,
                thumb_folded,
                index_folded,
                middle_folded,
                ring_folded,
                pinky_folded,
                click_distance,
                index_middle_distance
            )
            
            # Palm center is used for stable rotation tracking.
            palm_x, palm_y = landmarks["palm"]

            # Route execution path to specific controllers.
            if gesture == "CLICK":
                zoom_ctrl.reset()
                click_drag_ctrl.update(click_distance, thumb_folded, index_folded, current_time)

            elif gesture == "DRAG":
                zoom_ctrl.reset()
                click_drag_ctrl.update(click_distance, thumb_folded, index_folded, current_time)
                cursor_ctrl.move(landmarks, True, index_folded, w, h)

            elif gesture == "ZOOM":
                zoom_ctrl.scroll(landmarks["middle"][1], current_time)

            elif gesture == "ROTATE":
                zoom_ctrl.reset()

                if click_drag_ctrl.is_dragging:
                    pyautogui.mouseUp()
                    click_drag_ctrl.is_dragging = False

                click_drag_ctrl.is_pinched = False

            else: # MOVE
                zoom_ctrl.reset()
                cursor_ctrl.move(landmarks, False, index_folded, w, h)
                
            # Keep rotation engine synced with current hands frame.
            rotate_ctrl.update(
                gesture,
                palm_x,
                palm_y,
                current_time
                )

        # Calculate FPS
        fps = 1 / (current_time - prev_time) if prev_time else 0
        prev_time = current_time

        # Determine tracking status details
        has_hand = results.multi_hand_landmarks is not None
        tracking_status = "ACTIVE" if has_hand else "SEARCHING..."
        tracking_color = (0, 255, 0) if has_hand else (0, 0, 255) # Green / Red

        # Draw semi-transparent black dashboard card
        card_w, card_h = 300, 100
        if show_dashboard:
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (10 + card_w, 10 + card_h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        # Draw dashboard elements
            cv2.putText(frame, f"FPS       : {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "Tracking  : ", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, tracking_status, (120, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, tracking_color, 1, cv2.LINE_AA)
            if has_hand:
                # Dynamic gesture labels
                gesture_colors = {
                    "MOVE": (0, 255, 0),      # Green
                    "DRAG": (0, 0, 255),      # Red
                    "CLICK": (255, 0, 0),     # Blue
                    "ZOOM": (0, 255, 255),    # Yellow
                    "ROTATE": (255, 0, 255)   # Purple
                }
                g_color = gesture_colors.get(gesture, (255, 255, 255))
                cv2.putText(frame, "Gesture   : ", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, gesture, (120, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, g_color, 1, cv2.LINE_AA)

        cv2.imshow(WINDOW_TITLE, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord("h"):
            show_dashboard = not show_dashboard

        elif key == ord("d"):
            show_landmarks = not show_landmarks

    cap.release()
    hands.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()