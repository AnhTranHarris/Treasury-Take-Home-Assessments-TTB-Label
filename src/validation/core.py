from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .models import (
    ApplicationReference,
    DetectedEvidence,
    FieldResult,
    Status,
    VerificationResult,
)
from .normalization import (
    has_supported_abv_format,
    normalize_identity,
    parse_abv,
    parse_net_contents_ml,
    warning_text_for_comparison,
)

GOVERNMENT_WARNING = (
    "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink "
    "alcoholic beverages during pregnancy because of the risk of birth defects. "
    "(2) Consumption of alcoholic beverages impairs your ability to drive a car or operate "
    "machinery, and may cause health problems."
)

MANUAL_REVIEW_ADVISORIES = [
    "Government warning boldness is not automatically verified.",
    "Government warning physical type size, characters per inch, and true contrast require human review.",
    "Same-field-of-vision physical container geometry requires human review.",
]


def _review(rule_id: str, field: str, expected: Optional[str], detected: Optional[str], reason: str) -> FieldResult:
    return FieldResult(rule_id, field, Status.REVIEW, expected, detected, reason)


def _compare_identity(rule_id: str, field: str, expected: str, detected: Optional[str]) -> FieldResult:
    if not detected or not detected.strip():
        return _review(rule_id, field, expected, detected, "Required evidence was not reliably detected.")
    if normalize_identity(expected) == normalize_identity(detected):
        return FieldResult(rule_id, field, Status.PASS, expected, detected, "Detected value matches after conservative normalization.")
    return FieldResult(rule_id, field, Status.FAIL, expected, detected, "Detected value does not match the application/reference value.")


def verify(reference: ApplicationReference, evidence: DetectedEvidence) -> VerificationResult:
    results: list[FieldResult] = []

    results.append(_compare_identity("DS-BRAND-001", "Brand name", reference.brand, evidence.brand))
    results.append(_compare_identity("DS-CLASS-001", "Class/type", reference.class_type, evidence.class_type))

    detected_abv = parse_abv(evidence.abv_text)
    expected_abv = Decimal(str(reference.abv))
    if detected_abv is None:
        results.append(_review("DS-ABV-001", "Alcohol content", str(reference.abv), evidence.abv_text, "A reliable percent alcohol-by-volume value was not detected."))
    elif detected_abv == expected_abv:
        results.append(FieldResult("DS-ABV-001", "Alcohol content", Status.PASS, str(reference.abv), str(detected_abv), "Detected ABV matches the application/reference value."))
    else:
        results.append(FieldResult("DS-ABV-001", "Alcohol content", Status.FAIL, str(reference.abv), str(detected_abv), "Detected ABV differs from the application/reference value."))

    abv_format = has_supported_abv_format(evidence.abv_text)
    if abv_format is None:
        results.append(_review("DS-ABV-002", "Alcohol statement format", "% alcohol by volume", evidence.abv_text, "Alcohol statement format could not be reliably evaluated."))
    elif abv_format:
        results.append(FieldResult("DS-ABV-002", "Alcohol statement format", Status.PASS, "% alcohol by volume", evidence.abv_text, "Visible alcohol statement uses a supported alcohol-by-volume form."))
    else:
        results.append(FieldResult("DS-ABV-002", "Alcohol statement format", Status.FAIL, "% alcohol by volume", evidence.abv_text, "Visible alcohol statement does not use a supported mandatory alcohol-by-volume form."))

    expected_net = parse_net_contents_ml(reference.net_contents)
    detected_net = parse_net_contents_ml(evidence.net_contents)
    if expected_net is None:
        results.append(_review("DS-NET-001", "Net contents", reference.net_contents, evidence.net_contents, "Reference net contents could not be parsed."))
    elif detected_net is None:
        results.append(_review("DS-NET-001", "Net contents", reference.net_contents, evidence.net_contents, "Net contents were not reliably found in the submitted image; the statement may be elsewhere on the physical container."))
    elif expected_net == detected_net:
        results.append(FieldResult("DS-NET-001", "Net contents", Status.PASS, reference.net_contents, evidence.net_contents, "Detected net contents match after unit normalization."))
    else:
        results.append(FieldResult("DS-NET-001", "Net contents", Status.FAIL, reference.net_contents, evidence.net_contents, "Detected net contents differ from the application/reference value."))

    if detected_net is not None:
        results.append(FieldResult("DS-NET-002", "Net contents format", Status.PASS, "Metric L/mL form", evidence.net_contents, "Visible net contents use a supported metric quantity/unit form."))
    else:
        results.append(_review("DS-NET-002", "Net contents format", "Metric L/mL form", evidence.net_contents, "Net-contents format could not be evaluated from reliable visible evidence."))

    results.append(_compare_identity("DS-NAME-001", "Name/address", reference.name_address, evidence.name_address))

    if not reference.imported:
        results.append(FieldResult("DS-IMPORT-001", "Country of origin", Status.NOT_APPLICABLE, None, evidence.country_origin, "Application indicates a domestic product."))
    elif not reference.country_origin:
        results.append(_review("DS-IMPORT-001", "Country of origin", None, evidence.country_origin, "Imported product is missing an expected country-of-origin reference value."))
    elif not evidence.country_origin:
        results.append(_review("DS-IMPORT-001", "Country of origin", reference.country_origin, None, "Country-of-origin evidence was not reliably detected."))
    elif normalize_identity(reference.country_origin) == normalize_identity(evidence.country_origin):
        results.append(FieldResult("DS-IMPORT-001", "Country of origin", Status.PASS, reference.country_origin, evidence.country_origin, "Detected country of origin matches the application/reference value."))
    else:
        results.append(FieldResult("DS-IMPORT-001", "Country of origin", Status.FAIL, reference.country_origin, evidence.country_origin, "Detected country of origin differs from the application/reference value."))

    if not evidence.warning_text:
        results.append(_review("DS-WARN-001", "Government warning", GOVERNMENT_WARNING, evidence.warning_text, "Government warning text was not reliably detected."))
    elif warning_text_for_comparison(evidence.warning_text) == warning_text_for_comparison(GOVERNMENT_WARNING):
        results.append(FieldResult("DS-WARN-001", "Government warning", Status.PASS, GOVERNMENT_WARNING, evidence.warning_text, "Warning wording, capitalization, numbering, and punctuation match the configured TTB text after whitespace normalization."))
    else:
        results.append(FieldResult("DS-WARN-001", "Government warning", Status.FAIL, GOVERNMENT_WARNING, evidence.warning_text, "Warning text does not exactly match the configured TTB wording/case/punctuation after whitespace normalization."))

    return VerificationResult(
        field_results=results,
        manual_review_advisories=list(MANUAL_REVIEW_ADVISORIES),
    )
