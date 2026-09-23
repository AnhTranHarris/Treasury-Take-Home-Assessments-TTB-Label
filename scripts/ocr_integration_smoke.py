from __future__ import annotations

import cv2
import numpy as np

from src.ocr.paddle_provider import PaddleOCRProvider


def synthetic_label_bytes() -> bytes:
    canvas = np.full((500, 1200, 3), 255, dtype=np.uint8)
    lines = [
        "STONE'S THROW",
        "Kentucky Straight Bourbon Whiskey",
        "45% Alc./Vol.",
        "750 mL",
    ]
    for index, text in enumerate(lines):
        cv2.putText(
            canvas,
            text,
            (40, 90 + index * 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            (0, 0, 0),
            3,
            cv2.LINE_AA,
        )
    ok, encoded = cv2.imencode(".png", canvas)
    if not ok:
        raise RuntimeError("Could not encode integration-test image.")
    return encoded.tobytes()


def main() -> None:
    provider = PaddleOCRProvider(max_dimension=1600)
    lines = provider.recognize(synthetic_label_bytes())
    print(f"OCR integration returned {len(lines)} recognized lines")
    for line in lines[:10]:
        print(f"{line.score:.3f}: {line.text}")
    if not isinstance(lines, list):
        raise AssertionError("OCR provider did not return a list.")


if __name__ == "__main__":
    main()
