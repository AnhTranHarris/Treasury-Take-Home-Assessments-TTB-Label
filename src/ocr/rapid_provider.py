from __future__ import annotations

from collections.abc import Sequence
from threading import Lock
from typing import Any

from src.imaging.preprocess import prepare_ocr_image
from src.ocr.interface import OCRLine


def _box_to_rect(raw_box: Any) -> tuple[int, int, int, int] | None:
    """Convert a RapidOCR four-point box to the project's x1,y1,x2,y2 rectangle."""
    if raw_box is None:
        return None
    try:
        points = list(raw_box)
        if len(points) != 4:
            return None
        xs = [float(point[0]) for point in points]
        ys = [float(point[1]) for point in points]
    except (TypeError, ValueError, IndexError):
        return None
    return (
        int(round(min(xs))),
        int(round(min(ys))),
        int(round(max(xs))),
        int(round(max(ys))),
    )


def rapid_result_to_lines(result: Any) -> list[OCRLine]:
    """Adapt RapidOCR 3.x RapidOCROutput to the provider-independent OCRLine model."""
    texts = getattr(result, "txts", None)
    scores = getattr(result, "scores", None)
    boxes = getattr(result, "boxes", None)

    if texts is None:
        return []
    if not isinstance(texts, Sequence) or isinstance(texts, (str, bytes)):
        raise ValueError("RapidOCR result txts must be a sequence.")

    score_values = scores if scores is not None else ()
    box_values = boxes if boxes is not None else ()

    lines: list[OCRLine] = []
    for index, raw_text in enumerate(texts):
        text = str(raw_text).strip()
        if not text:
            continue

        raw_score = score_values[index] if index < len(score_values) else 0.0
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0

        box = _box_to_rect(box_values[index]) if index < len(box_values) else None
        lines.append(OCRLine(text=text, score=score, box=box))
    return lines


class RapidOCRProvider:
    """Local ONNX Runtime OCR adapter used when PaddlePaddle is unavailable."""

    def __init__(self, engine: Any | None = None, max_dimension: int = 1600):
        self._engine = engine
        self.max_dimension = max_dimension
        self._inference_lock = Lock()

    def _get_engine(self) -> Any:
        if self._engine is None:
            from rapidocr import RapidOCR

            self._engine = RapidOCR(
                params={
                    "EngineConfig.onnxruntime.intra_op_num_threads": 1,
                    "EngineConfig.onnxruntime.inter_op_num_threads": 1,
                }
            )
        return self._engine

    def recognize(self, image_bytes: bytes) -> list[OCRLine]:
        image = prepare_ocr_image(image_bytes, max_dimension=self.max_dimension)
        with self._inference_lock:
            result = self._get_engine()(image)
        if result is None:
            return []
        return rapid_result_to_lines(result)
