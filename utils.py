"""
Utility helper functions for mathematical calculations and hand landmarks processing.
"""

# Standard library
import math

# Local modules
from config import FOLDING_THRESHOLD


def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two 2D points (x, y)."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def get_landmarks_px(hand, w, h):
    """Get pixel coordinates for key points of the hand."""
    thumb_mcp = (int(hand.landmark[2].x * w), int(hand.landmark[2].y * h))
    thumb_ip = (int(hand.landmark[3].x * w), int(hand.landmark[3].y * h))
    thumb = (int(hand.landmark[4].x * w), int(hand.landmark[4].y * h))
    
    index_mcp = (int(hand.landmark[5].x * w), int(hand.landmark[5].y * h))
    index_pip = (int(hand.landmark[6].x * w), int(hand.landmark[6].y * h))
    index = (int(hand.landmark[8].x * w), int(hand.landmark[8].y * h))
    
    middle_mcp = (int(hand.landmark[9].x * w), int(hand.landmark[9].y * h))
    middle_pip = (int(hand.landmark[10].x * w), int(hand.landmark[10].y * h))
    middle = (int(hand.landmark[12].x * w), int(hand.landmark[12].y * h))
    ring_pip = (int(hand.landmark[14].x * w), int(hand.landmark[14].y * h))
    ring = (int(hand.landmark[16].x * w), int(hand.landmark[16].y * h))
    pinky_pip = (int(hand.landmark[18].x * w), int(hand.landmark[18].y * h))
    pinky = (int(hand.landmark[20].x * w), int(hand.landmark[20].y * h))
    
    palm_x = int(
        (
        hand.landmark[0].x +
        hand.landmark[5].x +
        hand.landmark[9].x +
        hand.landmark[13].x +
        hand.landmark[17].x
    ) / 5 * w
    )

    palm_y = int(
        (
        hand.landmark[0].y +
        hand.landmark[5].y +
        hand.landmark[9].y +
        hand.landmark[13].y +
        hand.landmark[17].y
    ) / 5 * h
    )

    return {
        "thumb_mcp": thumb_mcp,
        "thumb_ip": thumb_ip,
        "thumb": thumb,
        "index_mcp": index_mcp,
        "index_pip": index_pip,
        "index": index,
        "middle_mcp": middle_mcp,
        "middle_pip": middle_pip,
        "middle": middle,
        "ring_pip": ring_pip,
        "ring": ring,
        "pinky_pip": pinky_pip,
        "pinky": pinky,
        "palm": (palm_x, palm_y)
    }

def get_finger_folding_states(landmarks):
    """
    Determine if thumb, index, and middle fingers are folded.
    Returns:
        tuple: (thumb_folded, index_folded, middle_folded, click_distance, middle_distance, index_middle_distance)
    """
    thumb = landmarks["thumb"]
    thumb_mcp = landmarks["thumb_mcp"]
    thumb_ip = landmarks["thumb_ip"]
    index = landmarks["index"]
    index_pip = landmarks["index_pip"]
    middle = landmarks["middle"]
    middle_pip = landmarks["middle_pip"]
    ring = landmarks["ring"]
    ring_pip = landmarks["ring_pip"]
    pinky = landmarks["pinky"]
    pinky_pip = landmarks["pinky_pip"]

    raw_click_dist = calculate_distance(index, thumb)
    raw_middle_dist = calculate_distance(middle, thumb)
    raw_index_middle_dist = calculate_distance(index, middle)

    index_folded = (index[1] > index_pip[1]) and (raw_click_dist > FOLDING_THRESHOLD)
    middle_folded = (middle[1] > middle_pip[1]) and (raw_index_middle_dist > FOLDING_THRESHOLD)
    ring_folded = ring[1] > ring_pip[1]
    pinky_folded = pinky[1] > pinky_pip[1]
    
    thumb_to_mcp = calculate_distance(thumb, thumb_mcp)
    ip_to_mcp = calculate_distance(thumb_ip, thumb_mcp)
    thumb_folded = (thumb_to_mcp < ip_to_mcp * 1.2) and (raw_click_dist > FOLDING_THRESHOLD)

    click_distance = raw_click_dist if not (index_folded or thumb_folded) else float('inf')
    middle_distance = raw_middle_dist if not (middle_folded or thumb_folded) else float('inf')
    index_middle_distance = raw_index_middle_dist if not (index_folded or middle_folded) else float('inf')

    return (
        thumb_folded,
        index_folded,
        middle_folded,
        ring_folded,
        pinky_folded,
        click_distance,
        middle_distance,
        index_middle_distance
    )

def is_open_palm(
    thumb_folded,
    index_folded,
    middle_folded,
    ring_folded,
    pinky_folded
):
    return (
        not thumb_folded and
        not index_folded and
        not middle_folded and
        not ring_folded and
        not pinky_folded
    )