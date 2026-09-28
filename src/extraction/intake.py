from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

from src.ocr.interface import OCRLine
from src.validation.normalization import parse_abv, parse_net_contents_ml

REVIEW_OCR_SCORE = 0.90

_CLASS_PATTERN = re.compile(
    r"\b(?:bourbon|whisk(?:e)?y|gin|rum|vodka|brandy|liqueur|cordial|tequila|mezcal|distilled spirits?)\b",
    re.IGNORECASE,
)
_ABV_VALUE_PATTERN = re.compile(
    r"(?<!\d)\d{1,3}(?:\.\d+)?\s*%\s*(?:alc(?:ohol)?\.?\s*/?\s*vol(?:ume)?\.?|alcohol\s+by\s+volume)",
    re.IGNORECASE,
)
_NET_PATTERN = re.compile(
    r"(?<!\d)\d+(?:\.\d+)?\s*(?:ml\.?|millilit(?:er|re)s?|l\.?|lit(?:er|re)s?)\b",
    re.IGNORECASE,
)
_ADDRESS_PREFIX = re.compile(
    r"\b(?:imported by|bottled by|produced and bottled by|distilled and bottled by|"
    r"distilled by|produced by|bottled for|packed by)\s*:?",
    re.IGNORECASE,
)
_ORIGIN_KEY = re.compile(r"^\s*origin\s*:\s*(.*)$", re.IGNORECASE)
_SPIRIT_TYPE_KEY = re.compile(r"^\s*spirit\s*type\s*:\s*(.*)$", re.IGNORECASE)
_COUNTRY_PREFIXES: tuple[tuple[int, re.Pattern[str]], ...] = (
    (30, re.compile(r"\bproduct\s+of\s+(.+)$", re.IGNORECASE)),
    (20, re.compile(r"\bproduced\s+in\s+(.+)$", re.IGNORECASE)),
    (20, re.compile(r"\bdistilled(?:\s+and\s+bottled)?\s+in\s+(.+)$", re.IGNORECASE)),
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
    r"product of|origin\s*:|enjoy responsibly|consume responsibly|"
    r"small batch|cask strength|imperial strength|limited export|reserve edition",
    re.IGNORECASE,
)
_SECTION_STOP_PATTERN = re.compile(
    r"^(?:government warning|product details|consume responsibly|enjoy responsibly|"
    r"perfect serve|botanicals|ingredients\s*:|allergens\s*:|batch no\s*:|lot (?:no|code)\s*:|"
    r"spirit type\s*:|proof\s*:|bottle size\s*:|origin\s*:|please recycle|follow us\b)",
    re.IGNORECASE,
)
_URL_PATTERN = re.compile(r"(?:https?://|www\.|\.(?:com|org|net)\b)", re.IGNORECASE)
_STREET_PATTERN = re.compile(
    r"\b\d{1,6}\s+[A-Z0-9.' -]+\s(?:ST(?:REET)?|AVE(?:NUE)?|RD|ROAD|LN|LANE|"
    r"BLVD|BOULEVARD|DR|DRIVE|WAY|ROW|CT|COURT|PKWY|PARKWAY)\b",
    re.IGNORECASE,
)
_US_LOCATION_PATTERN = re.compile(
    r"(?:\b(?:USA|U\.S\.A\.|UNITED STATES)\b|,\s*(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|"
    r"ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b)",
    re.IGNORECASE,
)
_NON_LATIN_ONLY = re.compile(r"^[^A-Za-z0-9]+$")


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


def _y_center(line: OCRLine) -> float | None:
    if not line.box:
        return None
    return (line.box[1] + line.box[3]) / 2


def _page_extent(lines: Sequence[OCRLine]) -> tuple[float, float]:
    boxes = [line.box for line in lines if line.box]
    if not boxes:
        return 1.0, 1.0
    return max(float(box[2]) for box in boxes), max(float(box[3]) for box in boxes)


def _horizontal_overlap(a: OCRLine, b: OCRLine) -> float:
    if not a.box or not b.box:
        return 0.0
    left = max(a.box[0], b.box[0])
    right = min(a.box[2], b.box[2])
    intersection = max(0.0, right - left)
    smaller = max(1.0, min(_width(a), _width(b)))
    return intersection / smaller


def _vertical_overlap(a: OCRLine, b: OCRLine) -> float:
    if not a.box or not b.box:
        return 0.0
    top = max(a.box[1], b.box[1])
    bottom = min(a.box[3], b.box[3])
    intersection = max(0.0, bottom - top)
    smaller = max(1.0, min(_height(a), _height(b)))
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
    review_required: bool | None = None,
    missing_reason: str = "Not detected automatically.",
    reason: str | None = None,
) -> FieldDraft:
    conf = _confidence(lines)
    if not value:
        review = True if review_required is None else review_required
        return FieldDraft(None, conf, review, missing_reason, tuple(lines))
    review = ambiguous or conf is None or conf < REVIEW_OCR_SCORE
    if review_required is not None:
        review = review_required
    if reason is None:
        if ambiguous:
            reason = "Multiple plausible OCR candidates were found."
        elif conf is not None and conf < REVIEW_OCR_SCORE:
            reason = f"Lowest supporting OCR confidence is {conf:.2f}."
        else:
            reason = "Extraction evidence is clear enough for initial auto-fill."
    return FieldDraft(value, conf, review, reason, tuple(lines))


def _same_column(a: OCRLine, b: OCRLine, page_width: float) -> bool:
    if not a.box or not b.box:
        return False
    center_distance = abs((_x_center(a) or 0) - (_x_center(b) or 0)) / max(1.0, page_width)
    return _horizontal_overlap(a, b) >= 0.25 or center_distance <= 0.08


def _nearby_vertical(a: OCRLine, b: OCRLine, page_height: float) -> bool:
    return _vertical_gap(a, b) / max(1.0, page_height) <= 0.055


def _spatial_cluster(lines: Sequence[OCRLine], anchor: OCRLine, page_width: float, page_height: float) -> list[OCRLine]:
    if not anchor.box:
        return [anchor]
    selected = [anchor]
    for line in lines:
        if line is anchor or not line.box:
            continue
        if not _same_column(anchor, line, page_width):
            continue
        if not _nearby_vertical(anchor, line, page_height):
            continue
        selected.append(line)
    return sorted(set(selected), key=lambda item: (item.box[1] if item.box else 10**9, item.box[0] if item.box else 10**9))


def _latin_content_ratio(text: str) -> float:
    visible = [char for char in text if not char.isspace()]
    if not visible:
        return 0.0
    latin = sum(char.isascii() and (char.isalnum() or char in ".,&'-/") for char in visible)
    return latin / len(visible)


def _extract_brand(lines: Sequence[OCRLine]) -> FieldDraft:
    page_width, page_height = _page_extent(lines)
    candidates = [
        line for line in lines
        if _text(line)
        and line.box
        and not _CLASS_PATTERN.search(_text(line))
        and not _NON_BRAND_PATTERN.search(_text(line))
        and len(_text(line)) >= 3
        and _latin_content_ratio(_text(line)) >= 0.55
        and not _NON_LATIN_ONLY.match(_text(line))
    ]
    if not candidates:
        return _draft(None, missing_reason="Brand name was not detected automatically.")

    anchor = max(candidates, key=lambda line: (_height(line), _width(line)))
    anchor_height = max(1.0, _height(anchor))
    cluster = [
        line for line in _spatial_cluster(candidates, anchor, page_width, page_height)
        if _height(line) >= anchor_height * 0.20
    ]
    if not cluster:
        cluster = [anchor]

    value = " ".join(_text(line) for line in cluster)
    return _draft(value, cluster)


def _same_row_value(anchor: OCRLine, candidate: OCRLine, page_width: float, page_height: float) -> float | None:
    if not anchor.box or not candidate.box or candidate is anchor:
        return None
    dx = (candidate.box[0] - anchor.box[2]) / max(1.0, page_width)
    dy = abs((_y_center(candidate) or 0) - (_y_center(anchor) or 0)) / max(1.0, page_height)
    if dx < -0.02 or dx > 0.45 or dy > 0.045:
        return None
    return 100.0 - (dx * 70.0) - (dy * 500.0) + (20.0 * _vertical_overlap(anchor, candidate))


def _value_for_key(
    lines: Sequence[OCRLine],
    key_pattern: re.Pattern[str],
    value_accept: callable,
) -> tuple[str, OCRLine] | None:
    page_width, page_height = _page_extent(lines)
    for anchor in lines:
        match = key_pattern.match(_text(anchor))
        if not match:
            continue
        inline = match.group(1).strip(" .,:;-") if match.lastindex else ""
        if inline and value_accept(inline):
            return inline, anchor

        ranked: list[tuple[float, OCRLine]] = []
        for candidate in lines:
            if not value_accept(_text(candidate)):
                continue
            score = _same_row_value(anchor, candidate, page_width, page_height)
            if score is not None:
                ranked.append((score, candidate))

        if ranked:
            _, chosen = max(ranked, key=lambda item: item[0])
            return _text(chosen), chosen

        below = [
            candidate for candidate in lines
            if candidate.box and anchor.box
            and candidate.box[1] >= anchor.box[3]
            and _same_column(anchor, candidate, page_width)
            and (candidate.box[1] - anchor.box[3]) / max(1.0, page_height) <= 0.04
            and value_accept(_text(candidate))
        ]
        if below:
            chosen = min(below, key=lambda item: item.box[1] if item.box else 10**9)
            return _text(chosen), chosen
    return None


def _class_candidate_score(line: OCRLine) -> float:
    text = _text(line)
    words = text.split()
    area = max(1.0, _height(line) * _width(line))
    penalty = 1.0
    if len(words) > 7:
        penalty *= 0.12
    if re.search(r"[.!?]", text) and len(words) > 4:
        penalty *= 0.2
    if len(text) > 80:
        penalty *= 0.25
    return area * penalty


def _extract_class_type(lines: Sequence[OCRLine]) -> FieldDraft:
    anchored = _value_for_key(
        lines,
        _SPIRIT_TYPE_KEY,
        lambda value: bool(_CLASS_PATTERN.search(value)) and len(value.split()) <= 8,
    )
    if anchored:
        value, line = anchored
        return _draft(value, [line])

    candidates = [line for line in lines if _CLASS_PATTERN.search(_text(line))]
    if not candidates:
        return _draft(None, missing_reason="Class/type designation was not detected automatically.")

    chosen = max(candidates, key=_class_candidate_score)
    ranked_scores = sorted((_class_candidate_score(line), line) for line in candidates)
    second_score = ranked_scores[-2][0] if len(ranked_scores) > 1 else 0.0
    chosen_score = _class_candidate_score(chosen)
    ambiguous = second_score >= 0.80 * chosen_score and _text(ranked_scores[-2][1]).casefold() != _text(chosen).casefold()
    return _draft(_text(chosen), [chosen], ambiguous=ambiguous)


def _extract_abv(lines: Sequence[OCRLine]) -> FieldDraft:
    matches: list[tuple[OCRLine, str, float | None]] = []
    for line in lines:
        match = _ABV_VALUE_PATTERN.search(_text(line))
        if match:
            value = match.group(0).strip()
            matches.append((line, value, parse_abv(value)))
    if not matches:
        return _draft(None, missing_reason="Alcohol content statement was not detected automatically.")

    values = {parsed for _, _, parsed in matches if parsed is not None}
    chosen_line, chosen_value, _ = max(matches, key=lambda item: item[0].score)
    return _draft(chosen_value, [chosen_line], ambiguous=len(values) > 1)


def _extract_net(lines: Sequence[OCRLine]) -> FieldDraft:
    matches: list[tuple[OCRLine, str, float | None]] = []
    for line in lines:
        for match in _NET_PATTERN.finditer(_text(line)):
            value = match.group(0).strip()
            matches.append((line, value, parse_net_contents_ml(value)))
    if not matches:
        return _draft(None, missing_reason="Net contents were not detected automatically.")

    values = {parsed for _, _, parsed in matches if parsed is not None}
    chosen_line, chosen_value, _ = max(matches, key=lambda item: item[0].score)
    return _draft(chosen_value, [chosen_line], ambiguous=len(values) > 1)


def _is_section_stop(text: str) -> bool:
    stripped = text.strip()
    return bool(_SECTION_STOP_PATTERN.search(stripped) or _URL_PATTERN.search(stripped))


def _collect_address_after_prefix(lines: Sequence[OCRLine], anchor_index: int, limit: int = 3) -> list[OCRLine]:
    page_width, page_height = _page_extent(lines)
    anchor = lines[anchor_index]
    selected = [anchor]
    if not anchor.box:
        return selected

    for line in lines[anchor_index + 1 :]:
        if not line.box or line.box[1] < anchor.box[1]:
            continue
        if _is_section_stop(_text(line)):
            if line.box[1] >= anchor.box[3]:
                break
            continue
        if not _same_column(anchor, line, page_width):
            continue
        if (line.box[1] - anchor.box[3]) / max(1.0, page_height) > 0.075:
            continue
        selected.append(line)
        if len(selected) >= limit:
            break
    return selected


def _company_line(line: OCRLine) -> bool:
    return bool(re.search(r"\b(?:distillery|distilling co\.?|spirits|merchants|imports)\b", _text(line), re.IGNORECASE))


def _extract_street_address(lines: Sequence[OCRLine]) -> FieldDraft | None:
    page_width, page_height = _page_extent(lines)
    for street in lines:
        if not _STREET_PATTERN.search(_text(street)) or not street.box:
            continue

        city_candidates = [
            line for line in lines
            if line.box
            and line.box[1] >= street.box[3]
            and (line.box[1] - street.box[3]) / max(1.0, page_height) <= 0.055
            and _same_column(street, line, page_width)
            and _US_LOCATION_PATTERN.search(_text(line))
        ]
        city = min(city_candidates, key=lambda line: line.box[1] if line.box else 10**9) if city_candidates else None

        companies = [
            line for line in lines
            if line.box
            and line.box[3] <= street.box[1]
            and (street.box[1] - line.box[3]) / max(1.0, page_height) <= 0.14
            and _same_column(street, line, page_width)
            and _company_line(line)
        ]
        companies = sorted(companies, key=lambda line: line.box[1] if line.box else 10**9)[-2:]

        selected = companies + [street] + ([city] if city else [])
        value = " ".join(_text(line) for line in selected)
        return _draft(
            value,
            selected,
            ambiguous=not bool(companies and city),
            reason="Address assembled from spatially associated company, street, and locality evidence.",
        )
    return None


def _extract_name_address(lines: Sequence[OCRLine]) -> FieldDraft:
    for index, line in enumerate(lines):
        if _ADDRESS_PREFIX.search(_text(line)):
            selected = _collect_address_after_prefix(lines, index, limit=3)
            value = " ".join(_text(item) for item in selected)
            contaminated = any(_is_section_stop(_text(item)) for item in selected[1:])
            return _draft(
                value,
                selected,
                ambiguous=contaminated,
                reason="Address extracted from an explicit TTB-style name/address prefix.",
            )

    street_result = _extract_street_address(lines)
    if street_result is not None:
        return street_result

    return _draft(None, missing_reason="Name/address statement was not detected automatically.")


def _extract_country(lines: Sequence[OCRLine]) -> FieldDraft:
    anchored = _value_for_key(
        lines,
        _ORIGIN_KEY,
        lambda value: bool(value.strip()) and not _SECTION_STOP_PATTERN.search(value),
    )
    if anchored:
        value, line = anchored
        return _draft(value.strip(" .,:;-"), [line])

    matches: list[tuple[int, str, OCRLine]] = []
    for line in lines:
        for priority, pattern in _COUNTRY_PREFIXES:
            match = pattern.search(_text(line))
            if match:
                value = match.group(1).strip(" .,:;-")
                if value:
                    matches.append((priority, value, line))
    if not matches:
        return _draft(None, missing_reason="Country/origin phrase was not detected automatically.", review_required=False)

    best_priority = max(priority for priority, _, _ in matches)
    best = [(value, line) for priority, value, line in matches if priority == best_priority]
    unique = {value.casefold() for value, _ in best}
    value, line = max(best, key=lambda pair: pair[1].score)
    return _draft(value, [line], ambiguous=len(unique) > 1)


def _extract_imported(lines: Sequence[OCRLine], country: FieldDraft) -> FieldDraft:
    imported_lines = [line for line in lines if re.search(r"\bimported(?:\s+by)?\b", _text(line), re.IGNORECASE)]
    domestic_country = bool(country.value and _US_LOCATION_PATTERN.search(country.value))
    domestic_location_lines = [line for line in lines if _US_LOCATION_PATTERN.search(_text(line))]

    if imported_lines and (domestic_country or any(re.search(r"distilled.*\bUSA\b|product of.*\bUSA\b", _text(line), re.IGNORECASE) for line in lines)):
        return _draft(
            "Yes",
            imported_lines + ([country.source_lines[0]] if country.source_lines else []),
            ambiguous=True,
            reason="Import language conflicts with U.S. origin evidence; verify manually.",
        )
    if imported_lines:
        return _draft("Yes", imported_lines)
    if country.value and not domestic_country:
        return _draft("Yes", country.source_lines, reason="Non-U.S. origin phrase detected; verify import status.", ambiguous=True)
    if domestic_country:
        return _draft("No", country.source_lines, review_required=False, reason="U.S. origin evidence detected and no import language found.")
    if domestic_location_lines:
        best = max(domestic_location_lines, key=lambda line: line.score)
        return _draft("No", [best], review_required=False, reason="U.S. locality evidence detected and no import language found.")
    return _draft("No", (), review_required=True, reason="No explicit import or U.S. origin/locality evidence was detected.")


def _extract_warning(lines: Sequence[OCRLine]) -> FieldDraft:
    heading_index = next((i for i, line in enumerate(lines) if "government warning" in _text(line).casefold()), None)
    if heading_index is None:
        return _draft(None, missing_reason="Government warning was not detected automatically.")

    heading = lines[heading_index]
    page_width, page_height = _page_extent(lines)
    selected = [heading]
    for line in lines[heading_index + 1 :]:
        text = _text(line)
        if not text:
            continue
        if heading.box and line.box:
            center_distance = abs((_x_center(line) or 0) - (_x_center(heading) or 0)) / max(1.0, page_width)
            if center_distance > 0.22:
                continue
            if line.box[1] < heading.box[1]:
                continue
            if (line.box[1] - heading.box[3]) / max(1.0, page_height) > 0.32:
                break
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
        return _draft(
            None,
            missing_reason=f"{label} not detected. This disclosure is conditional and may not be required.",
            review_required=False,
        )
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
