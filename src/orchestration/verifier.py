from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from src.extraction.fields import extract_evidence
from src.ocr.interface import OCRLine, OCRProvider
from src.validation.core import verify
from src.validation.models import ApplicationReference, DetectedEvidence, VerificationResult


class VerificationExecutionError(RuntimeError):
    """Raised when the verification pipeline cannot execute safely."""


@dataclass(frozen=True)
class VerificationRun:
    result: VerificationResult
    evidence: DetectedEvidence
    ocr_lines: tuple[OCRLine, ...]
    elapsed_seconds: float


def verify_label(
    reference: ApplicationReference,
    image_bytes: bytes,
    provider: OCRProvider,
    *,
    clock: Callable[[], float] = perf_counter,
) -> VerificationRun:
    start = clock()
    try:
        lines = tuple(provider.recognize(image_bytes))
        evidence = extract_evidence(reference, lines)
        result = verify(reference, evidence)
    except Exception as exc:
        raise VerificationExecutionError(
            "The label could not be processed safely. No compliance result was generated."
        ) from exc
    elapsed = max(0.0, clock() - start)
    return VerificationRun(
        result=result,
        evidence=evidence,
        ocr_lines=lines,
        elapsed_seconds=elapsed,
    )
