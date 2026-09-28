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



def test_unconfirmed_highlighted_core_field_returns_review_not_pass():
    result = screen_label(valid_input(unresolved_review_fields=("brand",)))
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-BRAND-PRESENCE"].status == Status.REVIEW
    assert result.overall_status == Status.REVIEW


def test_confirmed_highlighted_field_can_pass_normal_rules():
    result = screen_label(valid_input(unresolved_review_fields=()))
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-BRAND-PRESENCE"].status == Status.PASS


def test_unconfirmed_warning_stays_review_instead_of_false_fail():
    result = screen_label(
        valid_input(
            government_warning="GOVERNMENT WARNING: incomplete",
            unresolved_review_fields=("government_warning",),
        )
    )
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-WARN-TEXT"].status == Status.REVIEW


def test_unconfirmed_import_origin_stays_review():
    result = screen_label(
        valid_input(
            imported=True,
            country_origin="England",
            unresolved_review_fields=("country_origin",),
        )
    )
    by_rule = {item.rule_id: item for item in result.field_results}
    assert by_rule["DS-IMPORT-PRESENCE"].status == Status.REVIEW
