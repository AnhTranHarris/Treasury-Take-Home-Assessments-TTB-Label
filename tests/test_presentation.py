from src.presentation import overall_message, result_rows
from src.validation.core import verify
from src.validation.models import ApplicationReference, DetectedEvidence, Status


def test_result_rows_preserve_field_level_explanation():
    result = verify(
        ApplicationReference("Brand", "Whiskey", 45.0, "750 mL", "Distiller, City, MO"),
        DetectedEvidence(
            brand="Brand",
            class_type="Whiskey",
            abv_text="45% Alc./Vol.",
            net_contents="750 mL",
            name_address="Distiller | City | MO",
            warning_text=None,
        ),
    )
    rows = result_rows(result)
    warning = next(row for row in rows if row["Rule"] == "DS-WARN-001")
    assert warning["Status"] == "REVIEW"
    assert "not reliably detected" in warning["Reason"]


def test_overall_messages_do_not_claim_full_legal_compliance():
    assert "Supported automated checks" in overall_message(Status.PASS)
    assert "deterministic" in overall_message(Status.FAIL)
    assert "human review" in overall_message(Status.REVIEW)
