import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import logging
logging.getLogger('tensorflow').setLevel(logging.FATAL)

logger = logging.getLogger(__name__)

logger.info("Подключаем нейронку...")

import keras
import cv2
import numpy as np

from analyzer.analyzer_config import FIELD_CATEGORIES_LABELS, FIELD_CATEGORIES

from utils import parent_dir, join_path


model = keras.models.load_model(join_path(parent_dir(__file__), "models", "field_classifier.keras"))

def classification(image: cv2.typing.MatLike) -> str:
    image = cv2.resize(image, (512, 512))
    image_array = image.astype('float32') / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array)[0]

    i = np.argmax(predictions)

    logger.debug(f"Предсказания: {predictions}")
    logger.debug(f"Категории: {FIELD_CATEGORIES}")
    logger.debug(f"Описания: {FIELD_CATEGORIES_LABELS}")

    return FIELD_CATEGORIES_LABELS[i] + f" ({int(predictions[i] * 100)}%)"
