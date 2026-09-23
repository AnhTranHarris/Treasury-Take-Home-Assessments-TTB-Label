from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from src.validation.core import GOVERNMENT_WARNING


def _wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = " ".join([*current, word])
        if current and len(candidate) > max_chars:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        lines.append(" ".join(current))
    return lines


def build_demo_label() -> np.ndarray:
    canvas = np.full((1600, 1500, 3), 255, dtype=np.uint8)

    cv2.putText(canvas, "STONE'S THROW", (80, 140), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(canvas, "Kentucky Straight Bourbon Whiskey", (80, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "45% Alc./Vol. (90 Proof)", (80, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "750 mL", (80, 440), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "Old Tom Distillery", (80, 560), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "Louisville", (80, 640), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(canvas, "KY", (80, 720), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (0, 0, 0), 3, cv2.LINE_AA)

    y = 890
    for line in _wrap_text(GOVERNMENT_WARNING, max_chars=72):
        cv2.putText(canvas, line, (80, y), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 0), 2, cv2.LINE_AA)
        y += 62

    return canvas


def main() -> None:
    output_dir = Path("sample_labels")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "demo_happy_path.png"

    ok = cv2.imwrite(str(output), build_demo_label())
    if not ok:
        raise RuntimeError(f"Could not write {output}")

    image = cv2.imread(str(output))
    if image is None:
        raise RuntimeError(f"Generated image could not be read back: {output}")

    height, width = image.shape[:2]
    print(f"Generated {output} ({width}x{height})")


if __name__ == "__main__":
    main()
