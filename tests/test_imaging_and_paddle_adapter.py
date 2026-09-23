import sys
import types
import cv2
import numpy as np
import pytest

from src.imaging.preprocess import ImageDecodeError, decode_image, prepare_ocr_image
from src.ocr.paddle_provider import PaddleOCRProvider, paddle_json_to_lines


def image_bytes(width=40, height=20):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    return encoded.tobytes()


def test_decode_image_rejects_invalid_bytes():
    with pytest.raises(ImageDecodeError):
        decode_image(b"not-an-image")


def test_prepare_ocr_image_caps_largest_dimension_without_upscaling():
    original = decode_image(image_bytes(width=80, height=40))
    same = prepare_ocr_image(image_bytes(width=80, height=40), max_dimension=100)
    resized = prepare_ocr_image(image_bytes(width=80, height=40), max_dimension=40)
    assert same.shape == original.shape
    assert resized.shape[:2] == (20, 40)


def test_paddle_json_adapter_supports_nested_res_payload():
    lines = paddle_json_to_lines(
        {
            "res": {
                "rec_texts": ["STONE'S THROW", "45% Alc./Vol."],
                "rec_scores": [0.99, 0.97],
                "rec_boxes": [[1, 2, 101, 22], [3, 30, 90, 50]],
            }
        }
    )
    assert [line.text for line in lines] == ["STONE'S THROW", "45% Alc./Vol."]
    assert lines[0].score == pytest.approx(0.99)
    assert lines[0].box == (1, 2, 101, 22)


def test_paddle_json_adapter_accepts_numpy_scores_and_boxes_like_real_paddle_output():
    lines = paddle_json_to_lines(
        {
            "res": {
                "rec_texts": ["45% Alc./Vol."],
                "rec_scores": np.array([0.98]),
                "rec_boxes": np.array([[4, 5, 80, 24]], dtype=np.int16),
            }
        }
    )
    assert lines[0].score == pytest.approx(0.98)
    assert lines[0].box == (4, 5, 80, 24)


def test_paddle_json_adapter_skips_empty_recognition_text():
    lines = paddle_json_to_lines(
        {"rec_texts": ["", "750 mL"], "rec_scores": [0.3, 0.9], "rec_boxes": []}
    )
    assert len(lines) == 1
    assert lines[0].text == "750 mL"


class FakeResult:
    json = {
        "res": {
            "rec_texts": ["750 mL"],
            "rec_scores": [0.95],
            "rec_boxes": [[0, 0, 30, 10]],
        }
    }


class FakeEngine:
    def __init__(self):
        self.seen_shape = None

    def predict(self, image):
        self.seen_shape = image.shape
        return [FakeResult()]


def test_provider_uses_injected_engine_without_importing_or_downloading_models():
    engine = FakeEngine()
    provider = PaddleOCRProvider(engine=engine, max_dimension=30)
    lines = provider.recognize(image_bytes(width=60, height=30))
    assert engine.seen_shape[:2] == (15, 30)
    assert lines[0].text == "750 mL"


def test_default_engine_disables_mkldnn_for_paddle_33_cpu_regression(monkeypatch):
    captured = {}

    class FakePaddleOCR:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    fake_module = types.ModuleType("paddleocr")
    fake_module.PaddleOCR = FakePaddleOCR
    monkeypatch.setitem(sys.modules, "paddleocr", fake_module)

    provider = PaddleOCRProvider()
    engine = provider._get_engine()

    assert isinstance(engine, FakePaddleOCR)
    assert captured["enable_mkldnn"] is False
    assert captured["text_detection_model_name"] == "PP-OCRv5_mobile_det"
    assert captured["text_recognition_model_name"] == "PP-OCRv5_mobile_rec"
