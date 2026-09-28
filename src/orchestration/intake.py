from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from src.extraction.intake import LabelIntakeDraft, extract_label_intake
from src.ocr.interface import OCRLine, OCRProvider
from src.orchestration.verifier import VerificationExecutionError


@dataclass(frozen=True)
class LabelIntakeRun:
    draft: LabelIntakeDraft
    ocr_lines: tuple[OCRLine, ...]
    elapsed_seconds: float


def analyze_label_intake(
    image_bytes: bytes,
    provider: OCRProvider,
    *,
    clock: Callable[[], float] = perf_counter,
) -> LabelIntakeRun:
    start = clock()
    try:
        lines = tuple(provider.recognize(image_bytes))
        draft = extract_label_intake(lines)
    except Exception as exc:
        raise VerificationExecutionError(
            "The label could not be read safely. No TTB intake fields were generated."
        ) from exc
    elapsed = max(0.0, clock() - start)
    return LabelIntakeRun(draft=draft, ocr_lines=lines, elapsed_seconds=elapsed)
