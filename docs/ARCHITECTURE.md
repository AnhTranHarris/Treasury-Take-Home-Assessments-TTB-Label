# TTB Label Verification Prototype — Architecture v0.4

**Status:** LOCKED DESIGN BASELINE  
**Purpose:** Prevent architecture drift and provide a single source of truth for implementation.  
**Repository:** AnhTranHarris/Treasury-Take-Home-Assessments-TTB-Label

## 1. Project Goal

Build a small, working proof-of-concept for the Treasury/TTB take-home assignment.

The prototype should support both a low-friction label-first screening workflow and an independent application/reference comparison workflow, return explainable results, and route uncertain cases to a human reviewer.

This is **not** a production COLA replacement and should not attempt production-scale federal integration.

## 2. Locked Technology Stack

The baseline stack is:

- **Streamlit** — browser-based user interface and deployment target.
- **OpenCV** — image preprocessing for difficult label photos.
- **PaddleOCR PP-OCRv5 mobile** — primary OCR/text-recognition engine.
- **RapidFuzz** — tolerant comparison for fields where capitalization/punctuation differences can still represent the same value.
- **Python deterministic validation rules** — final compliance comparison logic.
- **External generative-AI fallback** — not implemented in the submitted prototype; any future use requires federal cybersecurity/privacy/network/authorization review.

Primary open-source OCR project:
- https://github.com/PaddlePaddle/PaddleOCR

## 3. Core Design Principle

> AI extracts evidence. Python rules determine the prototype result. Ambiguous cases go to a human reviewer.

No OCR or external AI service is allowed to independently decide whether a label is compliant.

## 4A. Dual User Workflows

### Quick Label Review — default low-friction path

```text
upload / photograph label
        ↓
one local OCR pass
        ↓
spatial grouping from OCR boxes
        ↓
auto-fill TTB-oriented fields
        ↓
image preview + editable fields
        ↓
uncertain/missing field => yellow human-review notice
        ↓
human confirm/edit
        ↓
deterministic label presence/format screening
```

This workflow uses the label as the evidence source. It does **not** claim independent agreement with a COLA/application record.

### Compare to Reference — independent consistency path

The original application/reference workflow remains available separately. It compares supplied expected values against label evidence and must never silently seed expected values from the same label.

## 4. Processing Pipeline

```text
Upload label / take photo
        |
        v
     OpenCV
resize / orientation / contrast / denoise / perspective correction where useful
        |
        v
PaddleOCR PP-OCRv5 mobile
        |
        v
Field extraction + OCR confidence
        |
   +----+----+
   |         |
usable    uncertain
   |         |
   |         v
   |   unresolved evidence -> human review
   |   image -> visible text/fields only
   |         |
   |     +---+---+
   |     |       |
   |   usable  uncertain/conflict
   |     |       |
   +-----+       v
       |      HUMAN REVIEW
       v
RapidFuzz + deterministic Python rules
       |
       v
PASS / REVIEW / FAIL
```

## 5. Primary OCR Rules

PaddleOCR is the default recognition path.

OpenCV preprocessing should be used before OCR when useful, including:

- image resizing;
- rotation/orientation correction;
- contrast improvement;
- light denoising;
- thresholding when beneficial;
- moderate perspective correction for angled photographs.

The implementation must not promise recovery of text that is genuinely unreadable because of severe blur, glare, obstruction, or inadequate image resolution.

Unreadable evidence routes to **REVIEW**, not a guessed answer.

## 6. External Generative-AI Fallback — Deferred

The submitted prototype does not call Google Gemini or any other external generative-AI service.

Reason:

- the working local OCR path is sufficient for the proof of concept;
- unresolved cases can safely route to human review;
- sending label images or extracted information to an external AI service would require additional cybersecurity, privacy, network, data-handling, vendor, and authorization review in a federal environment;
- the take-home schedule did not provide enough time to validate those controls responsibly.

A future production team could evaluate an external fallback only after the permitted data boundary, approved service, authentication/secrets approach, logging, failure behavior, and authorization requirements are defined.


## 7. Field Comparison Philosophy

Different fields require different comparison strictness.

### Tolerant comparison

RapidFuzz/normalization may be used for fields such as:

- brand name;
- class/type designation where appropriate;
- harmless capitalization or punctuation differences.

Example:

```text
STONE'S THROW
Stone's Throw
```

may be treated as equivalent after normalization.

### Strict comparison

Fields with regulatory significance must not use loose fuzzy matching in a way that can hide material differences.

Examples include:

- alcohol content / ABV;
- net contents;
- required warning wording/numbering/punctuation;
- other exact statutory text requirements implemented in the prototype.

Government-warning wording/numbering/punctuation remain strictly compared within the supported automated scope.

Warning capitalization is a **manual-review advisory in the first slice**. Real PP-OCRv5 integration on 2026-09-23 read the correctly rendered all-caps word `GOVERNMENT` as `GOvERNMENT`, demonstrating that raw OCR case is not reliable enough to create a deterministic regulatory FAIL. A future targeted visual retry may promote capitalization back into automated validation only after testing demonstrates reliable behavior.

Visual requirements such as capitalization in the current first slice, bold styling, exact font size, or layout should remain **manual review** unless a separately tested implementation is added later.

## 8. User-Facing Result States

The application has three outcomes:

### PASS

All implemented automated checks have sufficient evidence and pass.

PASS means **pass within the prototype's supported automated scope**. It is not a complete legal-compliance determination.

### REVIEW

A supported automated check cannot be resolved reliably because evidence is uncertain, contradictory, unreadable, or missing.

### FAIL

A deterministic check found a clear mismatch or supported requirement failure within the prototype's automated scope.

### HUMAN REVIEW REQUIRED advisory

Requirements intentionally outside reliable MVP automation—such as physical type size, font weight, true contrast, permit-record verification, or full physical-container geometry—are displayed separately as manual-review advisories.

Standing manual-review advisories do not automatically convert an otherwise supported automated PASS into REVIEW.

Every outcome should show the reason.

## 9. Explainability Requirement

The results page should show evidence rather than a black-box score.

Conceptual example:

```text
Brand Name
Application: Stone's Throw
Detected:    STONE'S THROW
Result:      MATCH

Alcohol Content
Application: 45%
Detected:    45% Alc./Vol.
Result:      MATCH

Government Warning
Detected:    GOvERNMENT WARNING: ...
Automated:   PASS for supported wording/numbering/punctuation
Advisory:    HUMAN REVIEW REQUIRED
Reason:      Warning capitalization is not trusted from one OCR read in the first slice.
```

The UI should also show:

- which OCR path was used;
- whether external generative-AI fallback was required;
- relevant recognition confidence;
- processing time;
- reasons for PASS / REVIEW / FAIL.

## 10. UX Requirements Derived From Stakeholder Notes

The prototype should prioritize:

- obvious controls;
- minimal navigation;
- readable text;
- no hidden critical actions;
- upload or camera/photo input;
- clear status indicators;
- human-readable errors;
- processing-time visibility;
- no requirement for the reviewer to install software locally.

The hiring manager should use the deployed application entirely from a web browser.

## 11. Performance Goal

The stakeholder target is approximately **five seconds per simple label**.

The application should measure actual elapsed processing time.

Do not claim the five-second target is achieved until deployment benchmarks confirm it.

external generative-AI fallback may exceed the local-only path and should be treated as an exception path rather than the normal processing path.

## 12. MVP Scope

Build the smallest reliable submission first.

### Required MVP

- Streamlit web UI;
- manual entry of application/reference fields;
- JPG/PNG label upload;
- camera input if deployment supports it reliably;
- OpenCV preprocessing;
- PaddleOCR PP-OCRv5 mobile extraction;
- structured field extraction;
- RapidFuzz normalization where appropriate;
- deterministic comparison rules;
- PASS / REVIEW / FAIL;
- explainable results;
- processing-time measurement;
- graceful error handling;
- optional Gemini rescue path;
- sample labels;
- tests for deterministic validation behavior;
- README setup/run/deployment documentation.

### Stretch features only after the MVP works

- multiple-file/batch upload;
- CSV batch input/output;
- downloadable results;
- richer difficult-image preprocessing;
- additional beverage-specific rule sets;
- more detailed visual-format checks.

## 13. Explicit Non-Goals

Do not add these unless the design is intentionally revised:

- COLA integration;
- production federal authentication;
- database;
- user accounts;
- React frontend;
- microservices;
- vector database;
- autonomous agents;
- Gemini-first processing;
- LLM-generated compliance decisions;
- automatic guessing when text is unreadable;
- production FedRAMP/security claims.

## 14. Failure Behavior

The prototype should fail safely.

Examples:

```text
PaddleOCR succeeds
-> validate normally

Local OCR uncertain + external AI (future, not implemented)
-> validate extracted evidence, indicate fallback used

Local OCR uncertain
-> REVIEW

Conflicting automated evidence (future case)
-> REVIEW

Image unreadable
-> REVIEW and request clearer image

Unexpected internal error
-> show friendly error, do not fabricate result
```

## 15. Planned Repository Structure

```text
.
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PERFORMANCE_ARCHITECTURE.md
│   └── TTB_RULE_SCOPE.md
├── src/
│   ├── orchestration/
│   │   └── verifier.py
│   ├── imaging/
│   │   ├── quality.py
│   │   ├── preprocess.py
│   │   └── evidence_crops.py
│   ├── ocr/
│   │   ├── interface.py
│   │   ├── paddle_provider.py
│   │   └── rapid_provider.py
│   ├── extraction/
│   │   ├── fields.py
│   │   └── models.py
│   ├── validation/
│   │   ├── application_match.py
│   │   └── result.py
│   ├── rules/
│   │   └── distilled_spirits/
│   │       ├── brand.py
│   │       ├── class_type.py
│   │       ├── alcohol_content.py
│   │       ├── net_contents.py
│   │       ├── name_address.py
│   │       ├── country_origin.py
│   │       └── warning.py
│   └── fallback/
│       └── external_ai.py (future / not implemented)
├── tests/
│   ├── unit/
│   ├── regression/
│   └── synthetic/
└── sample_labels/
```

The structure separates orchestration, imaging, OCR, extraction, application matching, TTB rule packs, and external fallback logic so each concern can be tested independently.

Only the OCR provider selected by deployment benchmarking should be active in production. The second provider remains a documented contingency, not a second simultaneous OCR engine.

## 16. Change-Control Rule

This document is the current architecture baseline.

When implementation work reveals a better approach:

1. test or research the proposed change;
2. record why the existing decision is insufficient;
3. update this document;
4. then change implementation code.

Do not silently change architecture based only on remembered chat context.

## 17. Interview-Safe Summary

A concise explanation of the design:

> The prototype uses OpenCV to prepare label images and one local OCR backend selected for the deployment runtime. PaddleOCR remains the preferred path on compatible Python versions; RapidOCR with ONNX Runtime is the tested Python 3.14 deployment contingency. The application never runs both OCR engines simultaneously. Extracted fields are evaluated by deterministic Python rules, and uncertain evidence goes to human review. External generative-AI fallback is intentionally deferred; unresolved evidence routes to human review.

## 18. Accepted v0.2 Refinements

The following additions are now part of the architecture:

1. OpenCV image-quality triage before OCR.
2. Targeted evidence crops for human review.
3. RapidOCR + ONNX Runtime as the activated deployment contingency when the host runtime cannot install PaddlePaddle, including the observed Python 3.14 Community Cloud case.
4. Synthetic test labels, pytest, and GitHub Actions for regression QA.

Performance/concurrency decisions are documented in [Performance Architecture](PERFORMANCE_ARCHITECTURE.md).

The supported regulatory scope is documented in [TTB Rule Scope](TTB_RULE_SCOPE.md).

## 19. Current Decision State

**Locked for implementation v0.2:**

```text
Streamlit
+ OpenCV
+ ONE local OCR backend selected by runtime:
    Python 3.11–3.13 -> PaddleOCR PP-OCRv5 mobile
    Python 3.14      -> RapidOCR + ONNX Runtime
+ RapidFuzz / conservative normalization where appropriate
+ deterministic Python compliance rules
+ optional Gemini image-text fallback as last resort
```

The dual-provider code is a deployment compatibility strategy, not an ensemble. Exactly one local OCR provider is instantiated in a running process.

No application code should contradict this architecture unless this document is deliberately revised first.


## 20. Auto-fill field scope — v0.3

Current TTB-oriented Quick Label Review fields:

- brand name;
- class/type designation;
- alcohol content statement;
- net contents;
- name/address;
- imported yes/no;
- country/origin when applicable;
- government warning.

Conditional review fields:

- age statement;
- specified color ingredient disclosure;
- commodity statement.

TTB requires brand name, class/type designation, and alcohol content in the same field of vision. The prototype may use bounding boxes as review evidence but does not claim that a flattened image proves legal physical-container geometry.

Low OCR confidence is a routing signal for human review, not a legal/compliance probability. The initial 0.90 review threshold is provisional and must be benchmark-tuned.
