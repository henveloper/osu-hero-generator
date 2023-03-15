import os
import cv2
from typing import List, Tuple


def assert_image_dimension_consistent(image_folder_path: str) -> Tuple[List[str], Tuple[int, int]]:
    img_names = [os.path.join(image_folder_path, n)
                 for n in os.listdir(image_folder_path)]
    dimension = None
    for img_name in img_names:
        img = cv2.imread(img_name)
        h, w, _ = img.shape
        if dimension is None:
            dimension = (w, h)
            continue
        if (w, h) != dimension:
            raise Exception(f"{img_name} shape != {dimension}")
        
    return img_names, dimension
