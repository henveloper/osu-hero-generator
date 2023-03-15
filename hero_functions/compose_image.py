import math
import cv2
from typing import Tuple

TRANSITION_DELTA = 0.03


def rgb_by_position(color, note):
    # modifies the rgb value according to the distance (it gets brighter)

    # white is 255 255 255
    if abs(note - 0.5) > TRANSITION_DELTA:
        return color
    nudge = 1 - abs(note-0.5)/TRANSITION_DELTA
    return tuple(min(255, math.ceil(v + (255 - v) * nudge)) for v in color)


def radius_by_position(radius, note):
    if abs(note - 0.5) > TRANSITION_DELTA:
        return radius
    return math.floor(radius + radius * 0.5 * (1-abs(note-0.5) / TRANSITION_DELTA))


def compose_image(img, DIMENSION: Tuple[int, int], notes: list[float]):
    # notes: float [0, 1] determining the note position
    
    for note in notes:
        # rim
        cv2.circle(img,
                   (math.floor(DIMENSION[0] * note),
                    math.floor(0.9 * DIMENSION[1])),
                   radius_by_position(30, note),
                   (255, 255, 255),
                   -1)
        # inner ring
        cv2.circle(img,
                   (math.floor(DIMENSION[0] * note),
                    math.floor(0.9 * DIMENSION[1])),
                   radius_by_position(28, note),
                   (0, 0, 0),
                   -1)
        # body
        cv2.circle(img,
                   (math.floor(DIMENSION[0] * note),
                    math.floor(0.9 * DIMENSION[1])),
                   radius_by_position(23, note),
                   rgb_by_position((37, 150, 190), note),
                   -1)
