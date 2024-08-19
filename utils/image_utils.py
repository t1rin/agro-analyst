import cv2
import logging
import numpy as np

from dearpygui.dearpygui import texture_registry, add_static_texture

from utils.file_utils import file_exists

from cv2.typing import MatLike
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


def load_image(src: str) -> MatLike:
    return cv2.imread(src)

def image_record(path: str, img: MatLike) -> None:
    cv2.imwrite(path, img)

def image_exists(file: str) -> bool:
    if not file_exists(file):
        return False
    try:
        img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        return (img is not None)
    except:
        return False

def make_square_image(img: MatLike, size: int) -> MatLike:
    if not isinstance(size, int):
        logger.error(f"size не целочисленное! ({size=})")
    img_np = np.array(img)
    height, width = img_np.shape[:2]
    size_ = min(height, width)
    x_0 = (width - size_) // 2
    y_0 = (height - size_) // 2
    x_1 = x_0 + size_
    y_1 = y_0 + size_
    square = img_np[y_0:y_1, x_0:x_1, :]
    return cv2.resize(square, (size, size))

def convert_to_texture_data(img: MatLike) -> NDArray:
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    img_np = np.array(img_rgba)
    texture = img_np.flatten() / 255
    return texture

def create_texture(width: int = 0, height: int = 0, data: NDArray = [], *, tag: int = 0) -> int:
    with texture_registry():
        if tag:
            return add_static_texture(width, height, data, tag=tag)
        else:
            return add_static_texture(width, height, data)
