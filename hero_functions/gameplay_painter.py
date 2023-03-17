import math
import cv2
from typing import Tuple

# configs
# transition delta - ratio approaching center to enlarge/whitens the notes
TRANSITION_DELTA = 0.03
BEAT_BAR_HEIGHT = 0.95
# bar
BEAT_BAR_GIRTH_1 = 8
BEAT_BAR_GIRTH_2 = 6
# hitmark
HITMARK_RADIUS_1 = 10
HITMARK_RADIUS_2 = 9
HITMARK_COLOR = (118, 68, 235)  # fushia


def rgb_by_position(color, portion: int):
    """
    brightens the rgb value as it approaches the center
    """

    # white is 255 255 255
    if abs(portion - 0.5) > TRANSITION_DELTA:
        return color
    nudge = 1 - abs(portion-0.5)/TRANSITION_DELTA

    # some arbitary math
    return tuple(min(255, math.ceil(v + (255 - v) * nudge)) for v in color)


def radius_by_position(radius, portion: int):
    """
    increases the radius as it approaches the center
    """
    if abs(portion - 0.5) > TRANSITION_DELTA:
        return radius
    return math.floor(radius + radius * 0.5 * (1-abs(portion-0.5) / TRANSITION_DELTA))


def add_beatmarks(canvas, notes: list[int]):
    """
    this function takes in canvas and draw the beats

    notes are represented by an array of (0, 1) representing position
    """
    w = canvas.shape[1]
    h = canvas.shape[0]

    for note in notes:
        # rim
        center = (note, math.floor(BEAT_BAR_HEIGHT * h))
        cv2.circle(canvas, center,
                   radius_by_position(HITMARK_RADIUS_2+1, note / w),
                   (255, 255, 255),
                   -1,
                   lineType=cv2.LINE_AA)
        # inner ring
        cv2.circle(canvas, center,
                   radius_by_position(HITMARK_RADIUS_2, note / w),
                   (0, 0, 0),
                   -1,
                   lineType=cv2.LINE_AA)
        # body
        cv2.circle(canvas, center,
                   radius_by_position(HITMARK_RADIUS_2-1, note / w),
                   rgb_by_position(HITMARK_COLOR, note / w),
                   -1,
                   lineType=cv2.LINE_AA)


def add_main_beatbar(canvas):
    """
    adds the main beatbar to canvas

    1. the line (inner/outer)
    2. the hitmark circle
    """

    w = canvas.shape[1]
    h = canvas.shape[0]
    black = (0, 0, 0)
    white = (255, 255, 255)
    # main line
    main_line_from = (0, math.floor(BEAT_BAR_HEIGHT * h))
    main_line_to = (w, math.floor(BEAT_BAR_HEIGHT * h))

    # line - outer
    cv2.line(canvas, main_line_from, main_line_to,
             color=black, thickness=BEAT_BAR_GIRTH_1)

    # hit mark
    hit_mark_position = (math.floor(w * 0.5), math.floor(BEAT_BAR_HEIGHT * h))
    cv2.circle(canvas, hit_mark_position, radius=HITMARK_RADIUS_1, color=black,
               thickness=cv2.FILLED, lineType=cv2.LINE_AA)
    cv2.circle(canvas, hit_mark_position, radius=HITMARK_RADIUS_2, color=white,
               thickness=cv2.FILLED, lineType=cv2.LINE_AA)

    # line - inner
    cv2.line(canvas, main_line_from, main_line_to,
             color=white, thickness=BEAT_BAR_GIRTH_2)