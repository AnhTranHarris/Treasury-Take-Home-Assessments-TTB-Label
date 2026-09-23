from src.validation.core import GOVERNMENT_WARNING, verify
from src.validation.models import ApplicationReference, DetectedEvidence, Status


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


def happy_evidence(imported=False):
    return DetectedEvidence(
        brand="STONE'S THROW",
        class_type="Kentucky Straight Bourbon Whiskey",
        abv_text="45% Alc./Vol.",
        net_contents="750 ml",
        name_address="Old Tom Distillery, Louisville, KY",
        country_origin="CANADA" if imported else None,
        warning_text=GOVERNMENT_WARNING,
    )


def by_rule(result, rule_id):
    return next(item for item in result.field_results if item.rule_id == rule_id)


def test_happy_path_passes_supported_automated_scope():
    result = verify(reference(), happy_evidence())
    assert result.overall_status == Status.PASS
    assert by_rule(result, "DS-BRAND-001").status == Status.PASS
    assert by_rule(result, "DS-IMPORT-001").status == Status.NOT_APPLICABLE
    assert result.manual_review_advisories


def test_abv_mismatch_fails():
    ev = happy_evidence()
    ev = DetectedEvidence(**{**ev.__dict__, "abv_text": "46% Alc./Vol."})
    result = verify(reference(), ev)
    assert result.overall_status == Status.FAIL
    assert by_rule(result, "DS-ABV-001").status == Status.FAIL


def test_abv_abbreviation_only_is_not_supported_mandatory_format():
    ev = happy_evidence()
    ev = DetectedEvidence(**{**ev.__dict__, "abv_text": "45% ABV"})
    result = verify(reference(), ev)
    assert by_rule(result, "DS-ABV-002").status == Status.FAIL


def test_warning_heading_case_is_advisory_in_first_slice():
    ev = happy_evidence()
    bad_case = GOVERNMENT_WARNING.replace("GOVERNMENT WARNING", "Government Warning", 1)
    ev = DetectedEvidence(**{**ev.__dict__, "warning_text": bad_case})
    result = verify(reference(), ev)
    assert result.overall_status == Status.PASS
    assert by_rule(result, "DS-WARN-001").status == Status.PASS
    assert any("capitalization" in item.lower() for item in result.manual_review_advisories)


def test_warning_wording_mismatch_routes_to_review_until_targeted_retry_exists():
    ev = happy_evidence()
    bad_text = GOVERNMENT_WARNING.replace("birth defects", "birth injuries", 1)
    ev = DetectedEvidence(**{**ev.__dict__, "warning_text": bad_text})
    result = verify(reference(), ev)
    assert result.overall_status == Status.REVIEW
    assert by_rule(result, "DS-WARN-001").status == Status.REVIEW


def test_warning_line_breaks_are_tolerated():
    ev = happy_evidence()
    wrapped = GOVERNMENT_WARNING.replace(" women should", "\nwomen should").replace(" (2)", "\n(2)")
    ev = DetectedEvidence(**{**ev.__dict__, "warning_text": wrapped})
    result = verify(reference(), ev)
    assert by_rule(result, "DS-WARN-001").status == Status.PASS


def test_missing_net_contents_routes_to_review_not_fail():
    ev = happy_evidence()
    ev = DetectedEvidence(**{**ev.__dict__, "net_contents": None})
    result = verify(reference(), ev)
    assert result.overall_status == Status.REVIEW
    assert by_rule(result, "DS-NET-001").status == Status.REVIEW


def test_imported_country_match_passes():
    result = verify(reference(imported=True), happy_evidence(imported=True))
    assert by_rule(result, "DS-IMPORT-001").status == Status.PASS
    assert result.overall_status == Status.PASS


def test_imported_missing_country_routes_to_review():
    ev = happy_evidence(imported=True)
    ev = DetectedEvidence(**{**ev.__dict__, "country_origin": None})
    result = verify(reference(imported=True), ev)
    assert by_rule(result, "DS-IMPORT-001").status == Status.REVIEW
    assert result.overall_status == Status.REVIEW


def test_name_address_allows_line_separator_reconstruction():
    ev = happy_evidence()
    ev = DetectedEvidence(**{**ev.__dict__, "name_address": "Old Tom Distillery | Louisville | KY"})
    result = verify(reference(), ev)
    assert by_rule(result, "DS-NAME-001").status == Status.PASS
