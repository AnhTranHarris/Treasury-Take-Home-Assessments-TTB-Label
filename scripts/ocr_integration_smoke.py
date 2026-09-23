from __future__ import annotations

from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from src.ocr.paddle_provider import PaddleOCRProvider
from src.orchestration.verifier import verify_label
from src.validation.models import ApplicationReference, Status


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


def demo_reference() -> ApplicationReference:
    return ApplicationReference(
        brand="Stone's Throw",
        class_type="Kentucky Straight Bourbon Whiskey",
        abv=45.0,
        net_contents="750 mL",
        name_address="Old Tom Distillery, Louisville, KY",
    )


def main() -> None:
    provider = PaddleOCRProvider(max_dimension=1600)

    start = perf_counter()
    lines = provider.recognize(synthetic_label_bytes())
    first_seconds = perf_counter() - start
    print(f"OCR integration returned {len(lines)} recognized lines in {first_seconds:.3f}s")
    for line in lines[:10]:
        print(f"{line.score:.3f}: {line.text}")
    if not lines:
        raise AssertionError("OCR provider returned no lines for the controlled OCR fixture.")

    demo_path = Path("sample_labels/demo_happy_path.png")
    if not demo_path.exists():
        raise AssertionError(f"Expected generated demo label at {demo_path}")

    run = verify_label(demo_reference(), demo_path.read_bytes(), provider)
    print(f"Full pipeline warm run: {run.elapsed_seconds:.3f}s")
    print(f"Overall supported automated status: {run.result.overall_status.value}")
    for item in run.result.field_results:
        print(f"{item.rule_id}: {item.status.value} | {item.detected or '—'}")

    required_rules = {
        "DS-BRAND-001",
        "DS-CLASS-001",
        "DS-ABV-001",
        "DS-ABV-002",
        "DS-NET-001",
        "DS-NET-002",
        "DS-NAME-001",
        "DS-WARN-001",
    }
    by_rule = {item.rule_id: item for item in run.result.field_results}
    missing = required_rules - set(by_rule)
    if missing:
        raise AssertionError(f"Pipeline omitted required rule results: {sorted(missing)}")

    if run.result.overall_status != Status.PASS:
        failures = [
            f"{item.rule_id}={item.status.value} ({item.reason})"
            for item in run.result.field_results
            if item.status not in {Status.PASS, Status.NOT_APPLICABLE}
        ]
        raise AssertionError(
            "Controlled full-label happy path did not PASS supported automated checks: "
            + "; ".join(failures)
        )


if __name__ == "__main__":
    main()
