from src.extraction.fields import extract_evidence
from src.ocr.interface import OCRLine
from src.validation.core import GOVERNMENT_WARNING
from src.validation.models import ApplicationReference


def reference(imported=False):
    return ApplicationReference(
        brand="Stone's Throw",
        class_type="Kentucky Straight Bourbon Whiskey",
        abv=45.0,
        net_contents="750 mL",
        name_address="Old Tom Distillery, Louisville, KY",
        imported=imported,
        country_origin="Canada" if imported else None,
    )


def label_lines(imported=False, warning=GOVERNMENT_WARNING):
    # Split only at word boundaries so the fixture represents realistic OCR lines.
    split_points = [70, 160]
    warning_parts = []
    remaining = warning
    for target in split_points:
        if len(remaining) <= target:
            break
        cut = remaining.rfind(" ", 0, target + 1)
        if cut <= 0:
            cut = target
        warning_parts.append(remaining[:cut])
        remaining = remaining[cut:].lstrip()
    if remaining:
        warning_parts.append(remaining)

    lines = [
        OCRLine("STONE'S THROW", 0.99),
        OCRLine("Kentucky Straight Bourbon Whiskey", 0.99),
        OCRLine("45% Alc./Vol. (90 Proof)", 0.98),
        OCRLine("750 mL", 0.99),
        OCRLine("Old Tom Distillery", 0.98),
        OCRLine("Louisville", 0.98),
        OCRLine("KY", 0.98),
    ]
    if imported:
        lines.append(OCRLine("Product of Canada", 0.98))
    lines.extend(OCRLine(part, 0.97) for part in warning_parts)
    return lines


def test_extracts_core_fields_from_ordered_ocr_lines():
    ev = extract_evidence(reference(), label_lines())
    assert ev.brand == "STONE'S THROW"
    assert ev.class_type == "Kentucky Straight Bourbon Whiskey"
    assert ev.abv_text == "45% Alc./Vol. (90 Proof)"
    assert ev.net_contents == "750 mL"
    assert ev.name_address == "Old Tom Distillery | Louisville | KY"
    assert ev.warning_text == GOVERNMENT_WARNING


def test_preserves_warning_case_for_deterministic_validation():
    bad = GOVERNMENT_WARNING.replace("GOVERNMENT WARNING", "Government Warning", 1)
    ev = extract_evidence(reference(), label_lines(warning=bad))
    assert ev.warning_text.startswith("Government Warning:")


def test_missing_net_contents_is_not_invented():
    lines = [line for line in label_lines() if line.text != "750 mL"]
    ev = extract_evidence(reference(), lines)
    assert ev.net_contents is None


def test_imported_country_uses_supplied_reference_as_anchor():
    ev = extract_evidence(reference(imported=True), label_lines(imported=True))
    assert ev.country_origin == "Product of Canada"
