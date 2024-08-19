import os

import PIL.Image
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import logging
logging.getLogger('tensorflow').setLevel(logging.FATAL)

logger = logging.getLogger(__name__)

logger.info("Подключаем нейронку...")

import numpy as np
from PIL import Image

from tensorflow import keras

from PIL.Image import Image as ImageType

from analyzer.analyzer_config import (
    FIELD_CATEGORIES_LABELS, FIELD_CATEGORIES)
from utils import parent_dir, join_path


model = keras.models.load_model(join_path(parent_dir(__file__), "models", "field_classifier.keras"))
model.load_weights(join_path(parent_dir(__file__), "models", "field_classifier.keras"))

def load_img_keras(img_name: str) -> ImageType:
    return keras.preprocessing.image.load_img(img_name, target_size=(512,512))

def classification(image: ImageType) -> str:
    image_array = np.array(image)
    image = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image)[0]

    i = np.argmax(predictions)

    logger.debug(f"Предсказания: {predictions}")
    logger.debug(f"Категории: {FIELD_CATEGORIES}")
    logger.debug(f"Описания: {FIELD_CATEGORIES_LABELS}")

    return FIELD_CATEGORIES_LABELS[i] + f" ({int(predictions[i] * 100)}%)"
