from __future__ import annotations

from src.validation.models import Status, VerificationResult


def result_rows(result: VerificationResult) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in result.field_results:
        rows.append(
            {
                "Rule": item.rule_id,
                "Field": item.field,
                "Status": item.status.value,
                "Expected": item.expected or "—",
                "Detected": item.detected or "—",
                "Reason": item.reason,
            }
        )
    return rows


def overall_message(status: Status) -> str:
    if status == Status.PASS:
        return "Supported automated checks passed. Manual-review advisories may still apply."
    if status == Status.FAIL:
        return "At least one supported deterministic check failed."
    return "One or more supported automated checks need human review before a decision can be made."
