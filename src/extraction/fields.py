from __future__ import annotations

import re
from typing import Iterable, Sequence

from src.ocr.interface import OCRLine
from src.validation.core import GOVERNMENT_WARNING
from src.validation.models import ApplicationReference, DetectedEvidence
from src.validation.normalization import normalize_identity


def _text(line: OCRLine) -> str:
    return line.text.strip()


def _joined(lines: Sequence[OCRLine]) -> str:
    return " ".join(_text(line) for line in lines if _text(line))


def _find_exact_normalized(expected: str, lines: Sequence[OCRLine]) -> str | None:
    target = normalize_identity(expected)
    if not target:
        return None

    # First prefer a single OCR line.
    for line in lines:
        candidate = _text(line)
        if candidate and normalize_identity(candidate) == target:
            return candidate

    # Then allow a short run of adjacent OCR lines for wrapped fields.
    for width in (2, 3):
        for index in range(0, max(0, len(lines) - width + 1)):
            candidate = _joined(lines[index : index + width])
            if candidate and normalize_identity(candidate) == target:
                return candidate
    return None


def _find_components(expected: str, lines: Sequence[OCRLine]) -> str | None:
    """Find comma-separated reference components without inventing missing text."""
    components = [part.strip() for part in expected.split(",") if part.strip()]
    if not components:
        return None

    matched: list[str] = []
    used_indexes: set[int] = set()
    for component in components:
        target = normalize_identity(component)
        found = None
        for index, line in enumerate(lines):
            if index in used_indexes:
                continue
            candidate = _text(line)
            norm = normalize_identity(candidate) if candidate else ""
            if len(target) <= 3:
                matched_component = norm == target
            else:
                matched_component = norm == target or target in norm
            if matched_component:
                found = (index, candidate)
                break
        if not found:
            return None
        used_indexes.add(found[0])
        matched.append(found[1])
    return " | ".join(matched)


def _find_abv(lines: Sequence[OCRLine]) -> str | None:
    percent = re.compile(r"(?<!\d)\d{1,3}(?:\.\d+)?\s*%")
    marker = re.compile(r"\b(?:alc(?:ohol)?|vol(?:ume)?)\b", re.IGNORECASE)

    for width in (1, 2):
        for index in range(0, max(0, len(lines) - width + 1)):
            candidate = _joined(lines[index : index + width])
            if percent.search(candidate) and marker.search(candidate):
                return candidate
    return None


def _find_net_contents(lines: Sequence[OCRLine]) -> str | None:
    pattern = re.compile(
        r"(?<!\d)\d+(?:\.\d+)?\s*(?:ml\.?|millilit(?:er|re)s?|l\.?|lit(?:er|re)s?)\b",
        re.IGNORECASE,
    )
    for line in lines:
        candidate = _text(line)
        match = pattern.search(candidate)
        if match:
            return match.group(0)
    return None


def _find_country(expected: str | None, lines: Sequence[OCRLine]) -> str | None:
    if not expected:
        return None
    target = normalize_identity(expected)
    for line in lines:
        candidate = _text(line)
        norm = normalize_identity(candidate) if candidate else ""
        if target == norm or target in norm:
            return candidate
    return None


def _find_warning(lines: Sequence[OCRLine]) -> str | None:
    start_index = None
    for index, line in enumerate(lines):
        if "government warning" in _text(line).casefold():
            start_index = index
            break
    if start_index is None:
        return None

    expected_len = len(GOVERNMENT_WARNING)
    parts: list[str] = []
    for line in lines[start_index:]:
        text = _text(line)
        if not text:
            continue
        parts.append(text)
        candidate = " ".join(parts)
        if "health problems." in candidate.casefold() or len(candidate) >= expected_len + 20:
            break
    return " ".join(parts) if parts else None


def extract_evidence(reference: ApplicationReference, lines: Iterable[OCRLine]) -> DetectedEvidence:
    ordered = list(lines)
    return DetectedEvidence(
        brand=_find_exact_normalized(reference.brand, ordered),
        class_type=_find_exact_normalized(reference.class_type, ordered),
        abv_text=_find_abv(ordered),
        net_contents=_find_net_contents(ordered),
        name_address=(
            _find_exact_normalized(reference.name_address, ordered)
            or _find_components(reference.name_address, ordered)
        ),
        country_origin=(
            _find_country(reference.country_origin, ordered) if reference.imported else None
        ),
        warning_text=_find_warning(ordered),
    )
