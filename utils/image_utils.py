import cv2


def load_image(src: str) -> cv2.typing.MatLike:
    return cv2.imread(src)

...
