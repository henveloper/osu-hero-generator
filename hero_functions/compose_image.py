import math
import cv2
from typing import Tuple

# notes: float [0, 1] determining the note position


def compose_image(img, DIMENSION: Tuple[int, int], notes: list[float]):
    for note in notes:
        # rim
        cv2.circle(img,
                (math.floor(DIMENSION[0] * note), math.floor(0.9 * DIMENSION[1])),
                30, 
                (255, 255, 255),
                -1)
        # inner ring
        cv2.circle(img,
                (math.floor(DIMENSION[0] * note), math.floor(0.9 * DIMENSION[1])),
                28, 
                (0, 0, 0),
                -1)
        # body
        cv2.circle(img,
                (math.floor(DIMENSION[0] * note), math.floor(0.9 * DIMENSION[1])),
                23, 
                (53, 81, 92),
                -1)
