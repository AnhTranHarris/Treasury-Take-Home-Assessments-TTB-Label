from __future__ import annotations

from dataclasses import dataclass

from src.validation.core import GOVERNMENT_WARNING
from src.validation.models import FieldResult, Status, VerificationResult
from src.validation.normalization import (
    has_supported_abv_format,
    parse_net_contents_ml,
    warning_text_for_comparison,
)


@dataclass(frozen=True)
class LabelScreeningInput:
    brand: str
    class_type: str
    alcohol_content: str
    net_contents: str
    name_address: str
    imported: bool
    country_origin: str
    government_warning: str
    age_statement: str = ""
    color_disclosure: str = ""
    commodity_statement: str = ""
    unresolved_review_fields: tuple[str, ...] = ()


def _needs_review(data: LabelScreeningInput, field_key: str) -> bool:
    return field_key in set(data.unresolved_review_fields)


def _presence(rule_id: str, field: str, field_key: str, value: str, data: LabelScreeningInput) -> FieldResult:
    if _needs_review(data, field_key):
        return FieldResult(
            rule_id,
            field,
            Status.REVIEW,
            "Required on label",
            value.strip() or None,
            "OCR/extraction for this field still requires human confirmation.",
        )
    if value.strip():
        return FieldResult(
            rule_id,
            field,
            Status.PASS,
            "Required on label",
            value.strip(),
            "Required label information is present. Content identity is not compared to a COLA in Quick Label Review.",
        )
    return FieldResult(
        rule_id,
        field,
        Status.FAIL,
        "Required on label",
        None,
        "Required label information is missing after human review.",
    )


def screen_label(data: LabelScreeningInput) -> VerificationResult:
    results: list[FieldResult] = [
        _presence("DS-BRAND-PRESENCE", "Brand name", "brand", data.brand, data),
        _presence("DS-CLASS-PRESENCE", "Class/type", "class_type", data.class_type, data),
        _presence("DS-NAME-PRESENCE", "Name/address", "name_address", data.name_address, data),
    ]

    if _needs_review(data, "alcohol_content"):
        results.append(
            FieldResult(
                "DS-ABV-FORMAT",
                "Alcohol content",
                Status.REVIEW,
                "% alcohol by volume",
                data.alcohol_content.strip() or None,
                "OCR/extraction for alcohol content still requires human confirmation.",
            )
        )
    elif not data.alcohol_content.strip():
        results.append(
            FieldResult(
                "DS-ABV-PRESENCE",
                "Alcohol content",
                Status.FAIL,
                "% alcohol by volume",
                None,
                "Required alcohol content statement is missing after human review.",
            )
        )
    else:
        supported = has_supported_abv_format(data.alcohol_content)
        results.append(
            FieldResult(
                "DS-ABV-FORMAT",
                "Alcohol content",
                Status.PASS if supported else Status.FAIL,
                "% alcohol by volume",
                data.alcohol_content,
                "Alcohol statement uses a supported percent-alcohol-by-volume form."
                if supported
                else "Alcohol statement does not use a supported mandatory percent-alcohol-by-volume form.",
            )
        )

    if _needs_review(data, "net_contents"):
        results.append(
            FieldResult(
                "DS-NET-FORMAT",
                "Net contents",
                Status.REVIEW,
                "Metric L/mL statement",
                data.net_contents.strip() or None,
                "OCR/extraction for net contents still requires human confirmation.",
            )
        )
    elif not data.net_contents.strip():
        results.append(
            FieldResult(
                "DS-NET-PRESENCE",
                "Net contents",
                Status.FAIL,
                "Metric L/mL statement",
                None,
                "Required net contents are missing after human review.",
            )
        )
    else:
        parsed = parse_net_contents_ml(data.net_contents)
        results.append(
            FieldResult(
                "DS-NET-FORMAT",
                "Net contents",
                Status.PASS if parsed is not None else Status.FAIL,
                "Metric L/mL statement",
                data.net_contents,
                "Net contents use a supported metric quantity/unit form."
                if parsed is not None
                else "Net contents could not be parsed as a supported metric quantity/unit form.",
            )
        )

    if _needs_review(data, "imported") or (data.imported and _needs_review(data, "country_origin")):
        results.append(
            FieldResult(
                "DS-IMPORT-PRESENCE",
                "Country of origin",
                Status.REVIEW,
                "Country of origin for imports",
                data.country_origin.strip() or None,
                "Import/origin extraction still requires human confirmation.",
            )
        )
    elif data.imported:
        results.append(
            FieldResult(
                "DS-IMPORT-PRESENCE",
                "Country of origin",
                Status.PASS if data.country_origin.strip() else Status.FAIL,
                "Country of origin for imports",
                data.country_origin.strip() or None,
                "Country/origin information is present for an imported product."
                if data.country_origin.strip()
                else "Imported product is missing country/origin information after human review.",
            )
        )
    else:
        results.append(
            FieldResult(
                "DS-IMPORT-PRESENCE",
                "Country of origin",
                Status.NOT_APPLICABLE,
                None,
                data.country_origin.strip() or None,
                "Product is not marked as imported in the confirmed intake fields.",
            )
        )

    if _needs_review(data, "government_warning"):
        results.append(
            FieldResult(
                "DS-WARN-TEXT",
                "Government warning",
                Status.REVIEW,
                GOVERNMENT_WARNING,
                data.government_warning.strip() or None,
                "Government-warning extraction still requires human confirmation.",
            )
        )
    elif not data.government_warning.strip():
        results.append(
            FieldResult(
                "DS-WARN-TEXT",
                "Government warning",
                Status.FAIL,
                GOVERNMENT_WARNING,
                None,
                "Government warning is missing after human review.",
            )
        )
    else:
        expected = warning_text_for_comparison(GOVERNMENT_WARNING).casefold()
        detected = warning_text_for_comparison(data.government_warning).casefold()
        status = Status.PASS if detected == expected else Status.FAIL
        results.append(
            FieldResult(
                "DS-WARN-TEXT",
                "Government warning",
                status,
                GOVERNMENT_WARNING,
                data.government_warning,
                "Warning wording, numbering, and punctuation match after whitespace normalization."
                if status == Status.PASS
                else "Confirmed warning text differs from the configured TTB wording/numbering/punctuation.",
            )
        )

    advisories = [
        "Brand name, class/type, and alcohol content must appear in the same field of vision; uploaded artwork can support review but does not prove physical container geometry.",
        "Government warning capitalization, boldness, physical type size, characters per inch, and true contrast require visual/human review in this prototype.",
        "Age statements are conditional. For whisky under four years, TTB requires an age statement; the uploaded label alone may not reveal the product's actual age.",
        "Color ingredient disclosures and commodity statements are conditional and depend on product composition; absence from OCR does not establish that they are not required.",
    ]

    return VerificationResult(field_results=results, manual_review_advisories=advisories)
