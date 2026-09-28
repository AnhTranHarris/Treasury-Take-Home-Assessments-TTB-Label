from src.validation.core import GOVERNMENT_WARNING
from src.validation.label_screening import LabelScreeningInput, screen_label
from src.validation.models import Status


def valid_input(**overrides):
    values = dict(
        brand="Example Distillery",
        class_type="Bourbon",
        alcohol_content="45% Alc./Vol.",
        net_contents="750 mL",
        name_address="Example Distillery, Louisville, KY",
        imported=False,
        country_origin="",
        government_warning=GOVERNMENT_WARNING,
    )
    values.update(overrides)
    return LabelScreeningInput(**values)


def test_quick_screen_passes_core_present_and_formatted_fields():
    result = screen_label(valid_input())
    assert result.overall_status == Status.PASS


def test_imported_label_requires_country():
    result = screen_label(valid_input(imported=True, country_origin=""))
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-IMPORT-PRESENCE"].status == Status.FAIL


def test_invalid_abv_format_fails_after_human_confirmation():
    result = screen_label(valid_input(alcohol_content="45% ABV"))
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-ABV-FORMAT"].status == Status.FAIL


def test_warning_text_mismatch_fails_after_human_confirmation():
    result = screen_label(valid_input(government_warning="GOVERNMENT WARNING: incomplete"))
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-WARN-TEXT"].status == Status.FAIL
