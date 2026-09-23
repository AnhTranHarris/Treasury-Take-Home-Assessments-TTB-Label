from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Status(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class ApplicationReference:
    brand: str
    class_type: str
    abv: float
    net_contents: str
    name_address: str
    imported: bool = False
    country_origin: Optional[str] = None


@dataclass(frozen=True)
class DetectedEvidence:
    brand: Optional[str] = None
    class_type: Optional[str] = None
    abv_text: Optional[str] = None
    net_contents: Optional[str] = None
    name_address: Optional[str] = None
    country_origin: Optional[str] = None
    warning_text: Optional[str] = None


@dataclass(frozen=True)
class FieldResult:
    rule_id: str
    field: str
    status: Status
    expected: Optional[str]
    detected: Optional[str]
    reason: str


@dataclass
class VerificationResult:
    field_results: list[FieldResult] = field(default_factory=list)
    manual_review_advisories: list[str] = field(default_factory=list)

    @property
    def overall_status(self) -> Status:
        statuses = {item.status for item in self.field_results}
        if Status.FAIL in statuses:
            return Status.FAIL
        if Status.REVIEW in statuses:
            return Status.REVIEW
        return Status.PASS
