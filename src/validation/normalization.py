from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Optional

_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "`": "'"})
_DASHES = str.maketrans({"–": "-", "—": "-", "−": "-"})


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_identity(value: str) -> str:
    """Conservative normalization for human names, brands, and designations."""
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.translate(_APOSTROPHES).translate(_DASHES)
    return collapse_whitespace(normalized).casefold()


def normalize_name_address(value: str) -> str:
    """Normalize harmless address separators while preserving substantive words/numbers."""
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.translate(_APOSTROPHES).translate(_DASHES)
    normalized = re.sub(r"[,|.]", " ", normalized)
    return collapse_whitespace(normalized).casefold()


def parse_abv(value: Optional[str]) -> Optional[Decimal]:
    if not value:
        return None
    match = re.search(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%", value)
    if not match:
        return None
    try:
        return Decimal(match.group(1))
    except InvalidOperation:
        return None


def has_supported_abv_format(value: Optional[str]) -> Optional[bool]:
    if not value:
        return None
    text = collapse_whitespace(unicodedata.normalize("NFKC", value))
    if parse_abv(text) is None:
        return None

    lowered = text.casefold()
    if "abv" in lowered and not (
        "alcohol by volume" in lowered or ("alc" in lowered and "vol" in lowered)
    ):
        return False

    return (
        "alcohol by volume" in lowered
        or ("alc" in lowered and "vol" in lowered)
    )


def parse_net_contents_ml(value: Optional[str]) -> Optional[Decimal]:
    if not value:
        return None
    text = collapse_whitespace(unicodedata.normalize("NFKC", value))
    match = re.search(
        r"(?<!\d)(\d+(?:\.\d+)?)\s*(ml\.?|millilit(?:er|re)s?|l\.?|lit(?:er|re)s?)\b",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    try:
        amount = Decimal(match.group(1))
    except InvalidOperation:
        return None
    unit = match.group(2).casefold().rstrip(".")
    if unit.startswith("l") and not unit.startswith("ml"):
        return amount * Decimal("1000")
    return amount


def warning_text_for_comparison(value: str) -> str:
    """Preserve case and punctuation; tolerate OCR line breaks/repeated whitespace only."""
    return collapse_whitespace(unicodedata.normalize("NFKC", value))
