from __future__ import annotations

from pathlib import Path

from src.ocr.factory import build_default_ocr_provider, choose_ocr_backend
from src.orchestration.verifier import verify_label
from src.validation.models import ApplicationReference, Status


def demo_reference() -> ApplicationReference:
    return ApplicationReference(
        brand="Stone's Throw",
        class_type="Kentucky Straight Bourbon Whiskey",
        abv=45.0,
        net_contents="750 mL",
        name_address="Old Tom Distillery, Louisville, KY",
    )


def main() -> None:
    backend = choose_ocr_backend()
    print(f"Selected deployment OCR backend: {backend}")
    if backend != "rapid":
        raise AssertionError("Python 3.14 deployment smoke test must select RapidOCR.")

    demo_path = Path("sample_labels/demo_happy_path.png")
    if not demo_path.exists():
        raise AssertionError(f"Expected generated demo label at {demo_path}")

    provider = build_default_ocr_provider()
    run = verify_label(demo_reference(), demo_path.read_bytes(), provider)

    print(f"Deployment-compatible full pipeline: {run.elapsed_seconds:.3f}s")
    print(f"Overall supported automated status: {run.result.overall_status.value}")
    for line in run.ocr_lines[:20]:
        print(f"OCR {line.score:.3f}: {line.text}")
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
        unresolved = [
            f"{item.rule_id}={item.status.value} ({item.reason})"
            for item in run.result.field_results
            if item.status not in {Status.PASS, Status.NOT_APPLICABLE}
        ]
        raise AssertionError(
            "Controlled RapidOCR deployment happy path did not PASS supported automated checks: "
            + "; ".join(unresolved)
        )


if __name__ == "__main__":
    main()
