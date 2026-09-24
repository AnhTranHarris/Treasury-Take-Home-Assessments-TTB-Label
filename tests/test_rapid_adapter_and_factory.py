import numpy as np
import pytest

from src.ocr.factory import choose_ocr_backend
from src.ocr.rapid_provider import RapidOCRProvider, rapid_result_to_lines


class FakeRapidResult:
    txts = ("STONE'S THROW", "45% Alc./Vol.")
    scores = (0.99, 0.97)
    boxes = np.array(
        [
            [[1, 2], [101, 2], [101, 22], [1, 22]],
            [[3, 30], [90, 30], [90, 50], [3, 50]],
        ],
        dtype=np.float32,
    )


class FakeRapidEngine:
    def __init__(self):
        self.seen_shape = None

    def __call__(self, image):
        self.seen_shape = image.shape
        return FakeRapidResult()


def test_rapid_result_adapter_preserves_text_score_and_rectangular_box():
    lines = rapid_result_to_lines(FakeRapidResult())
    assert [line.text for line in lines] == ["STONE'S THROW", "45% Alc./Vol."]
    assert lines[0].score == pytest.approx(0.99)
    assert lines[0].box == (1, 2, 101, 22)


def test_rapid_provider_uses_injected_engine_without_importing_runtime():
    import cv2

    image = np.zeros((30, 60, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", image)
    assert ok

    engine = FakeRapidEngine()
    provider = RapidOCRProvider(engine=engine, max_dimension=30)
    lines = provider.recognize(encoded.tobytes())

    assert engine.seen_shape[:2] == (15, 30)
    assert lines[1].text == "45% Alc./Vol."


def test_backend_defaults_to_paddle_before_python_314():
    assert choose_ocr_backend(python_version=(3, 11), override="") == "paddle"
    assert choose_ocr_backend(python_version=(3, 13), override="") == "paddle"


def test_backend_defaults_to_rapid_on_python_314():
    assert choose_ocr_backend(python_version=(3, 14), override="") == "rapid"


def test_backend_override_is_explicit_and_validated():
    assert choose_ocr_backend(python_version=(3, 14), override="paddle") == "paddle"
    assert choose_ocr_backend(python_version=(3, 11), override="rapid") == "rapid"
    with pytest.raises(ValueError):
        choose_ocr_backend(python_version=(3, 11), override="unknown")
