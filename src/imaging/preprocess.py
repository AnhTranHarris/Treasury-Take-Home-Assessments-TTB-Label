from __future__ import annotations

import cv2
import numpy as np


class ImageDecodeError(ValueError):
    """Raised when uploaded bytes cannot be decoded as an image."""


def decode_image(image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise ImageDecodeError("The uploaded image is empty.")

    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ImageDecodeError("The uploaded file could not be decoded as a supported image.")
    return image


def resize_for_ocr(image: np.ndarray, max_dimension: int = 1600) -> np.ndarray:
    if max_dimension <= 0:
        raise ValueError("max_dimension must be positive.")
    if image.ndim < 2 or image.size == 0:
        raise ValueError("image must be a non-empty image array.")

    height, width = image.shape[:2]
    largest = max(height, width)
    if largest <= max_dimension:
        return image

    scale = max_dimension / float(largest)
    target = (max(1, round(width * scale)), max(1, round(height * scale)))
    return cv2.resize(image, target, interpolation=cv2.INTER_AREA)


def prepare_ocr_image(image_bytes: bytes, max_dimension: int = 1600) -> np.ndarray:
    """First-pass image preparation: decode and cap resolution without speculative enhancement."""
    return resize_for_ocr(decode_image(image_bytes), max_dimension=max_dimension)
