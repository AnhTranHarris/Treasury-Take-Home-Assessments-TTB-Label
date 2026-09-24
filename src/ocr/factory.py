from __future__ import annotations

import os
import sys

from src.ocr.interface import OCRProvider

_SUPPORTED_BACKENDS = {"paddle", "rapid"}


def choose_ocr_backend(
    *,
    python_version: tuple[int, int] | None = None,
    override: str | None = None,
) -> str:
    """Select one local OCR backend without loading both runtimes."""
    requested = override
    if requested is None:
        requested = os.getenv("TTB_OCR_BACKEND", "")
    requested = requested.strip().lower()

    if requested:
        if requested not in _SUPPORTED_BACKENDS:
            raise ValueError(
                "TTB_OCR_BACKEND must be 'paddle' or 'rapid'."
            )
        return requested

    version = python_version or (sys.version_info.major, sys.version_info.minor)
    # PaddlePaddle 3.3.1 has no CPython 3.14 wheel. RapidOCR + ONNX Runtime is
    # the approved deployment contingency for that environment.
    return "rapid" if version >= (3, 14) else "paddle"


def build_default_ocr_provider() -> OCRProvider:
    backend = choose_ocr_backend()
    if backend == "rapid":
        from src.ocr.rapid_provider import RapidOCRProvider

        return RapidOCRProvider()

    from src.ocr.paddle_provider import PaddleOCRProvider

    return PaddleOCRProvider()
