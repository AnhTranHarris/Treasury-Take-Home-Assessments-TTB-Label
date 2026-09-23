import pytest

from src.ocr.interface import OCRLine
from src.orchestration.verifier import VerificationExecutionError, verify_label
from src.validation.core import GOVERNMENT_WARNING
from src.validation.models import ApplicationReference, Status


def reference():
    return ApplicationReference(
        brand="Stone's Throw",
        class_type="Kentucky Straight Bourbon Whiskey",
        abv=45.0,
        net_contents="750 mL",
        name_address="Old Tom Distillery, Louisville, KY",
    )


def recognized_lines():
    return [
        OCRLine("STONE'S THROW", 0.99),
        OCRLine("Kentucky Straight Bourbon Whiskey", 0.99),
        OCRLine("45% Alc./Vol.", 0.99),
        OCRLine("750 mL", 0.99),
        OCRLine("Old Tom Distillery", 0.99),
        OCRLine("Louisville", 0.99),
        OCRLine("KY", 0.99),
        OCRLine(GOVERNMENT_WARNING, 0.99),
    ]


class FakeProvider:
    def __init__(self, lines):
        self.lines = lines
        self.calls = 0

    def recognize(self, image_bytes):
        self.calls += 1
        assert image_bytes == b"image"
        return self.lines


def test_orchestrator_runs_one_ocr_pass_and_returns_supported_pass():
    provider = FakeProvider(recognized_lines())
    ticks = iter([10.0, 10.25])
    run = verify_label(reference(), b"image", provider, clock=lambda: next(ticks))
    assert provider.calls == 1
    assert run.result.overall_status == Status.PASS
    assert run.evidence.brand == "STONE'S THROW"
    assert run.elapsed_seconds == pytest.approx(0.25)


def test_orchestrator_preserves_deterministic_fail():
    lines = recognized_lines()
    lines[2] = OCRLine("46% Alc./Vol.", 0.99)
    run = verify_label(reference(), b"image", FakeProvider(lines))
    assert run.result.overall_status == Status.FAIL


class BrokenProvider:
    def recognize(self, image_bytes):
        raise RuntimeError("model failure")


def test_orchestrator_does_not_fabricate_result_on_internal_error():
    with pytest.raises(VerificationExecutionError) as exc:
        verify_label(reference(), b"image", BrokenProvider())
    assert "No compliance result was generated" in str(exc.value)
