from __future__ import annotations

from collections.abc import Mapping, Sequence
from threading import Lock
from typing import Any

from src.imaging.preprocess import prepare_ocr_image
from src.ocr.interface import OCRLine


def _payload_result(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = payload.get("res")
    if isinstance(nested, Mapping):
        return nested
    return payload


def paddle_json_to_lines(payload: Mapping[str, Any]) -> list[OCRLine]:
    """Adapt PaddleOCR 3.x result.json output to the provider-independent OCRLine model."""
    result = _payload_result(payload)
    texts = result.get("rec_texts")
    scores = result.get("rec_scores")
    boxes = result.get("rec_boxes")
    if texts is None:
        texts = []
    if scores is None:
        scores = []
    if boxes is None:
        boxes = []

    if not isinstance(texts, Sequence) or isinstance(texts, (str, bytes)):
        raise ValueError("PaddleOCR result rec_texts must be a sequence.")

    lines: list[OCRLine] = []
    for index, raw_text in enumerate(texts):
        text = str(raw_text).strip()
        if not text:
            continue

        raw_score = scores[index] if index < len(scores) else 0.0
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0

        box = None
        if index < len(boxes):
            raw_box = boxes[index]
            try:
                if len(raw_box) == 4:
                    box = tuple(int(value) for value in raw_box)
            except (TypeError, ValueError):
                box = None

        lines.append(OCRLine(text=text, score=score, box=box))
    return lines


class PaddleOCRProvider:
    """Local PaddleOCR adapter with lazy model loading for Streamlit caching."""

    def __init__(self, engine: Any | None = None, max_dimension: int = 1600):
        self._engine = engine
        self.max_dimension = max_dimension
        self._inference_lock = Lock()

    def _get_engine(self) -> Any:
        if self._engine is None:
            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="PP-OCRv5_mobile_rec",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
        return self._engine

    def recognize(self, image_bytes: bytes) -> list[OCRLine]:
        image = prepare_ocr_image(image_bytes, max_dimension=self.max_dimension)
        with self._inference_lock:
            results = list(self._get_engine().predict(image))
        if not results:
            return []

        payload = getattr(results[0], "json", None)
        if not isinstance(payload, Mapping):
            raise RuntimeError("PaddleOCR returned an unexpected result shape.")
        return paddle_json_to_lines(payload)
