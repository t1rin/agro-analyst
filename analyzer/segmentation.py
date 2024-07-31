import cv2
import numpy as np

from cv2.typing import Size, MatLike


def _size_optimization(img_size: Size) -> Size:
    MAX_HEIGHT = 200
    MAX_WIDTH = 200
    
    height, width = img_size

    k = 1
    if height > MAX_HEIGHT or width > MAX_WIDTH:
        k = min(MAX_HEIGHT / height, MAX_WIDTH / width)

    return Size(int(k * height), int(k * width))


def segmentation(img: MatLike, k_blur: int = 3) -> list[MatLike]:
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_img = cv2.medianBlur(gray_img, k_blur)

    shape = _size_optimization(blur_img.shape)
    resized_img = cv2.resize(blur_img, shape)

    img_np = np.array(resized_img.copy())
    edges = np.zeros(shape)
    rows, cols = shape

    x_d = np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1])
    y_d = np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1])
    x_mask = np.array([-1, -2, -1, 0, 0, 0, 1, 2, 1])
    y_mask = np.array([-1, 0, 1, -2, 0, 2, -1, 0, 1])

    for i in range(1, rows-1):
        for j in range(1, cols-1):
            s1 = np.sum(img_np[i+y_d, j+x_d] * x_mask)
            s2 = np.sum(img_np[i+y_d, j+x_d] * y_mask)
            sum_ = np.abs(s1) + np.abs(s2)
            
            if sum_ < 180:
                sum_ = 0

            edges[i][j] = min(sum_, 255)

    _, thresh = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # masks = []
    # for contour in contours:
        # mask = np.zeros(shape)
        # cv2.drawContours(mask, [contour], -1, (255), thickness=cv2.FILLED)
        # masks.append(mask)

    mask = np.zeros(shape)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)

    return [cv2.resize(mask, img.shape[:2])]


