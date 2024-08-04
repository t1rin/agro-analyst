import cv2
import numpy as np

from dearpygui.dearpygui import texture_registry, add_static_texture

from cv2.typing import MatLike
from numpy.typing import NDArray


def load_image(src: str) -> MatLike:
    return cv2.imread(src)

def convert_to_texture_data(img: MatLike) -> NDArray:
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    img_np = np.array(img_rgba)
    texture = img_np.flatten() / 255
    return texture

def create_texture(width: int = 0, height: int = 0, data: NDArray = []) -> int:
    with texture_registry():
        return add_static_texture(width, height, data)
