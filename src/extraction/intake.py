from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

from src.ocr.interface import OCRLine
from src.validation.core import GOVERNMENT_WARNING
from src.validation.normalization import parse_abv, parse_net_contents_ml

REVIEW_OCR_SCORE = 0.90

_CLASS_PATTERN = re.compile(
    r"\b(?:bourbon|whisk(?:e)?y|gin|rum|vodka|brandy|liqueur|cordial|tequila|mezcal|distilled spirits?)\b",
    re.IGNORECASE,
)
_ABV_PATTERN = re.compile(r"(?<!\d)\d{1,3}(?:\.\d+)?\s*%.*?(?:alc(?:ohol)?|vol(?:ume)?)", re.IGNORECASE)
_NET_PATTERN = re.compile(
    r"(?<!\d)\d+(?:\.\d+)?\s*(?:ml\.?|millilit(?:er|re)s?|l\.?|lit(?:er|re)s?)\b",
    re.IGNORECASE,
)
_ADDRESS_PREFIX = re.compile(
    r"\b(?:imported by|bottled by|produced and bottled by|distilled and bottled by|"
    r"distilled by|produced by|bottled for|packed by)\s*:?",
    re.IGNORECASE,
)
_COUNTRY_PREFIX = re.compile(
    r"\b(?:product of|produced in|distilled(?: and bottled)? in|origin\s*:?)\s+(.+)$",
    re.IGNORECASE,
)
_AGE_PATTERN = re.compile(
    r"\b(?:aged\s+(?:at least\s+|a minimum of\s+)?\d+\s+(?:days?|months?|years?)|"
    r"\d+\s+(?:days?|months?|years?)\s+old)\b",
    re.IGNORECASE,
)
_COLOR_PATTERN = re.compile(r"\b(?:FD&C\s+Yellow\s+(?:No\.?\s*)?5|carmine|cochineal extract)\b", re.IGNORECASE)
_COMMODITY_PATTERN = re.compile(r"\b(?:neutral spirits?|distilled from|distilled from grain|grain neutral spirits?)\b", re.IGNORECASE)

_NON_BRAND_PATTERN = re.compile(
    r"government warning|alc\.?\s*/?\s*vol|alcohol by volume|\b\d+\s*ml\b|"
    r"\bproof\b|bottle size|product details|imported by|distilled and bottled|"
    r"product of|origin\s*:|enjoy responsibly|consume responsibly",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FieldDraft:
    value: str | None
    confidence: float | None
    review_required: bool
    reason: str
    source_lines: tuple[OCRLine, ...] = ()


@dataclass(frozen=True)
class LabelIntakeDraft:
    brand: FieldDraft
    class_type: FieldDraft
    alcohol_content: FieldDraft
    net_contents: FieldDraft
    name_address: FieldDraft
    imported: FieldDraft
    country_origin: FieldDraft
    government_warning: FieldDraft
    age_statement: FieldDraft
    color_disclosure: FieldDraft
    commodity_statement: FieldDraft


def _text(line: OCRLine) -> str:
    return line.text.strip()


def _height(line: OCRLine) -> float:
    if not line.box:
        return 0.0
    return max(0.0, float(line.box[3] - line.box[1]))


def _width(line: OCRLine) -> float:
    if not line.box:
        return 0.0
    return max(0.0, float(line.box[2] - line.box[0]))


def _x_center(line: OCRLine) -> float | None:
    if not line.box:
        return None
    return (line.box[0] + line.box[2]) / 2


def _horizontal_overlap(a: OCRLine, b: OCRLine) -> float:
    if not a.box or not b.box:
        return 0.0
    left = max(a.box[0], b.box[0])
    right = min(a.box[2], b.box[2])
    intersection = max(0.0, right - left)
    smaller = max(1.0, min(_width(a), _width(b)))
    return intersection / smaller


def _vertical_gap(a: OCRLine, b: OCRLine) -> float:
    if not a.box or not b.box:
        return float("inf")
    if a.box[3] <= b.box[1]:
        return float(b.box[1] - a.box[3])
    if b.box[3] <= a.box[1]:
        return float(a.box[1] - b.box[3])
    return 0.0


def _confidence(lines: Sequence[OCRLine]) -> float | None:
    if not lines:
        return None
    return min(float(line.score) for line in lines)


def _draft(
    value: str | None,
    lines: Sequence[OCRLine] = (),
    *,
    ambiguous: bool = False,
    missing_reason: str = "Not detected automatically.",
    reason: str | None = None,
) -> FieldDraft:
    conf = _confidence(lines)
    if not value:
        return FieldDraft(None, conf, True, missing_reason, tuple(lines))
    review = ambiguous or conf is None or conf < REVIEW_OCR_SCORE
    if reason is None:
        if ambiguous:
            reason = "Multiple plausible OCR candidates were found."
        elif conf is not None and conf < REVIEW_OCR_SCORE:
            reason = f"Lowest supporting OCR confidence is {conf:.2f}."
        else:
            reason = "Extraction evidence is clear enough for initial auto-fill."
    return FieldDraft(value, conf, review, reason, tuple(lines))


def _same_column(a: OCRLine, b: OCRLine) -> bool:
    if not a.box or not b.box:
        return False
    return _horizontal_overlap(a, b) >= 0.25 or abs((_x_center(a) or 0) - (_x_center(b) or 0)) <= max(40.0, min(_width(a), _width(b)) * 0.45)


def _spatial_cluster(lines: Sequence[OCRLine], anchor: OCRLine) -> list[OCRLine]:
    if not anchor.box:
        return [anchor]
    selected = [anchor]
    for line in lines:
        if line is anchor or not line.box:
            continue
        if not _same_column(anchor, line):
            continue
        gap = _vertical_gap(anchor, line)
        if gap <= max(36.0, 1.8 * max(_height(anchor), _height(line))):
            selected.append(line)
    return sorted(set(selected), key=lambda item: (item.box[1] if item.box else 10**9, item.box[0] if item.box else 10**9))


def _extract_brand(lines: Sequence[OCRLine]) -> FieldDraft:
    candidates = [
        line for line in lines
        if _text(line)
        and line.box
        and not _CLASS_PATTERN.search(_text(line))
        and not _NON_BRAND_PATTERN.search(_text(line))
        and len(_text(line)) >= 3
    ]
    if not candidates:
        return _draft(None, missing_reason="Brand name was not detected automatically.")

    anchor = max(candidates, key=lambda line: (_height(line), _width(line)))
    anchor_height = max(1.0, _height(anchor))
    cluster = [
        line for line in _spatial_cluster(candidates, anchor)
        if _height(line) >= anchor_height * 0.48
    ]
    if not cluster:
        cluster = [anchor]
    value = " ".join(_text(line) for line in cluster)
    return _draft(value, cluster)


def _group_candidates(lines: Sequence[OCRLine]) -> list[list[OCRLine]]:
    remaining = list(lines)
    groups: list[list[OCRLine]] = []
    while remaining:
        anchor = remaining.pop(0)
        group = [anchor]
        changed = True
        while changed:
            changed = False
            for line in list(remaining):
                if any(_same_column(existing, line) and _vertical_gap(existing, line) <= max(36.0, 1.8 * max(_height(existing), _height(line))) for existing in group):
                    group.append(line)
                    remaining.remove(line)
                    changed = True
        groups.append(sorted(group, key=lambda item: (item.box[1] if item.box else 10**9, item.box[0] if item.box else 10**9)))
    return groups


def _extract_class_type(lines: Sequence[OCRLine]) -> FieldDraft:
    candidates = [line for line in lines if _CLASS_PATTERN.search(_text(line))]
    if not candidates:
        return _draft(None, missing_reason="Class/type designation was not detected automatically.")

    groups = _group_candidates(candidates)
    ranked = sorted(
        groups,
        key=lambda group: sum(max(1.0, _height(line)) * max(1.0, _width(line)) for line in group),
        reverse=True,
    )
    chosen = ranked[0]
    ambiguous = len(ranked) > 1 and sum(_height(line) * _width(line) for line in ranked[1]) >= 0.65 * sum(_height(line) * _width(line) for line in chosen)
    return _draft(" ".join(_text(line) for line in chosen), chosen, ambiguous=ambiguous)


def _extract_abv(lines: Sequence[OCRLine]) -> FieldDraft:
    candidates = [line for line in lines if _ABV_PATTERN.search(_text(line))]
    if not candidates:
        return _draft(None, missing_reason="Alcohol content statement was not detected automatically.")
    parsed = [(line, parse_abv(_text(line))) for line in candidates]
    values = {value for _, value in parsed if value is not None}
    chosen = max(candidates, key=lambda line: line.score)
    return _draft(_text(chosen), [chosen], ambiguous=len(values) > 1)


def _extract_net(lines: Sequence[OCRLine]) -> FieldDraft:
    candidates = [line for line in lines if _NET_PATTERN.search(_text(line))]
    if not candidates:
        return _draft(None, missing_reason="Net contents were not detected automatically.")
    parsed = [(line, parse_net_contents_ml(_text(line))) for line in candidates]
    values = {value for _, value in parsed if value is not None}
    chosen = max(candidates, key=lambda line: line.score)
    match = _NET_PATTERN.search(_text(chosen))
    value = match.group(0) if match else _text(chosen)
    return _draft(value, [chosen], ambiguous=len(values) > 1)


def _collect_following(lines: Sequence[OCRLine], anchor_index: int, limit: int = 3) -> list[OCRLine]:
    anchor = lines[anchor_index]
    selected = [anchor]
    if not anchor.box:
        return selected
    for line in lines[anchor_index + 1 :]:
        if not line.box or line.box[1] < anchor.box[1]:
            continue
        if not _same_column(anchor, line):
            continue
        if line.box[1] - anchor.box[3] > 95:
            continue
        selected.append(line)
        if len(selected) >= limit:
            break
    return selected


def _extract_name_address(lines: Sequence[OCRLine]) -> FieldDraft:
    for index, line in enumerate(lines):
        if _ADDRESS_PREFIX.search(_text(line)):
            selected = _collect_following(lines, index, limit=3)
            value = " ".join(_text(item) for item in selected)
            return _draft(value, selected)

    company_candidates = [
        (index, line) for index, line in enumerate(lines)
        if re.search(r"\b(?:distillery|distilling co\.?|spirits|merchants)\b", _text(line), re.IGNORECASE)
    ]
    for index, line in company_candidates:
        selected = _collect_following(lines, index, limit=3)
        if len(selected) >= 2 and any(re.search(r"\b[A-Z]{2}\b|\b\d{5}(?:-\d{4})?\b", _text(item), re.IGNORECASE) for item in selected[1:]):
            return _draft(" ".join(_text(item) for item in selected), selected, reason="Address inferred from company/location lines; human confirmation recommended.", ambiguous=True)

    return _draft(None, missing_reason="Name/address statement was not detected automatically.")


def _extract_country(lines: Sequence[OCRLine]) -> FieldDraft:
    matches: list[tuple[str, OCRLine]] = []
    for line in lines:
        match = _COUNTRY_PREFIX.search(_text(line))
        if match:
            value = match.group(1).strip(" .,:;-")
            if value:
                matches.append((value, line))
    if not matches:
        return _draft(None, missing_reason="Country/origin phrase was not detected automatically.")
    unique = {value.casefold() for value, _ in matches}
    value, line = max(matches, key=lambda pair: pair[1].score)
    return _draft(value, [line], ambiguous=len(unique) > 1)


def _extract_imported(lines: Sequence[OCRLine], country: FieldDraft) -> FieldDraft:
    imported_lines = [line for line in lines if re.search(r"\bimported(?:\s+by)?\b", _text(line), re.IGNORECASE)]
    domestic_country = bool(country.value and re.search(r"\b(?:usa|u\.s\.a\.|united states)\b", country.value, re.IGNORECASE))
    if imported_lines and domestic_country:
        return _draft("Yes", imported_lines, ambiguous=True, reason="Import language and a U.S. origin phrase both appear; verify manually.")
    if imported_lines:
        return _draft("Yes", imported_lines)
    if country.value and not domestic_country:
        return _draft("Yes", country.source_lines, reason="Non-U.S. origin phrase detected; verify import status.")
    if domestic_country:
        return _draft("No", country.source_lines)
    return _draft("No", (), reason="No explicit import language was detected; verify if product context is unclear.")


def _extract_warning(lines: Sequence[OCRLine]) -> FieldDraft:
    heading_index = next((i for i, line in enumerate(lines) if "government warning" in _text(line).casefold()), None)
    if heading_index is None:
        return _draft(None, missing_reason="Government warning was not detected automatically.")

    heading = lines[heading_index]
    selected = [heading]
    for line in lines[heading_index + 1 :]:
        text = _text(line)
        if not text:
            continue
        if heading.box and line.box:
            heading_center = _x_center(heading) or 0.0
            line_center = _x_center(line) or 0.0
            allowed = max(120.0, _width(heading) * 1.15)
            if abs(line_center - heading_center) > allowed:
                continue
            if line.box[1] < heading.box[1]:
                continue
        selected.append(line)
        if "health problems." in text.casefold():
            break
        if len(selected) >= 16:
            break

    value = " ".join(_text(line) for line in selected)
    complete = "health problems." in value.casefold()
    return _draft(
        value,
        selected,
        ambiguous=not complete,
        reason=None if complete else "Warning heading was found, but the full warning could not be isolated confidently.",
    )


def _find_optional(lines: Sequence[OCRLine], pattern: re.Pattern[str], label: str) -> FieldDraft:
    candidates = [line for line in lines if pattern.search(_text(line))]
    if not candidates:
        return _draft(None, missing_reason=f"{label} not detected. This is conditional and may not be required.")
    chosen = max(candidates, key=lambda line: line.score)
    return _draft(_text(chosen), [chosen])


def extract_label_intake(lines: Iterable[OCRLine]) -> LabelIntakeDraft:
    ordered = list(lines)
    country = _extract_country(ordered)
    return LabelIntakeDraft(
        brand=_extract_brand(ordered),
        class_type=_extract_class_type(ordered),
        alcohol_content=_extract_abv(ordered),
        net_contents=_extract_net(ordered),
        name_address=_extract_name_address(ordered),
        imported=_extract_imported(ordered, country),
        country_origin=country,
        government_warning=_extract_warning(ordered),
        age_statement=_find_optional(ordered, _AGE_PATTERN, "Age statement"),
        color_disclosure=_find_optional(ordered, _COLOR_PATTERN, "Color ingredient disclosure"),
        commodity_statement=_find_optional(ordered, _COMMODITY_PATTERN, "Commodity statement"),
    )
