# TTB Label Verification Prototype — Architecture v0.1

**Status:** LOCKED DESIGN BASELINE  
**Purpose:** Prevent architecture drift and provide a single source of truth for implementation.  
**Repository:** AnhTranHarris/Treasury-Take-Home-Assessments-TTB-Label

## 1. Project Goal

Build a small, working proof-of-concept for the Treasury/TTB take-home assignment.

The prototype should help a compliance reviewer compare information visible on an alcohol label against application data, return an explainable result, and route uncertain cases to a human reviewer.

This is **not** a production COLA replacement and should not attempt production-scale federal integration.

## 2. Locked Technology Stack

The baseline stack is:

- **Streamlit** — browser-based user interface and deployment target.
- **OpenCV** — image preprocessing for difficult label photos.
- **PaddleOCR PP-OCRv5 mobile** — primary OCR/text-recognition engine.
- **RapidFuzz** — tolerant comparison for fields where capitalization/punctuation differences can still represent the same value.
- **Python deterministic validation rules** — final compliance comparison logic.
- **Google Gemini image API** — optional last-resort text-extraction fallback only.

Primary open-source OCR project:
- https://github.com/PaddlePaddle/PaddleOCR

## 3. Core Design Principle

> AI extracts evidence. Python rules determine the prototype result. Ambiguous cases go to a human reviewer.

Neither PaddleOCR nor Gemini is allowed to independently decide whether a label is compliant.

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
   |   optional Gemini fallback
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

## 6. Gemini Fallback Rules

Gemini is optional and must never be a hard dependency.

Gemini may be invoked only when the local pipeline cannot produce sufficiently trustworthy evidence, for example:

- a required field is missing after local OCR;
- OCR confidence for an important field falls below the configured threshold;
- the government-warning text is incomplete or unreadable;
- image quality remains difficult after preprocessing.

The final numerical confidence threshold is **TBD and must be chosen from testing**, not invented in advance.

Gemini's job is limited to extracting visible text/structured fields. A conceptual request is:

```text
Extract only text visibly present on this alcohol label.

Return these fields when visible:
- brand_name
- class_type
- alcohol_content
- net_contents
- producer
- country_of_origin
- government_warning

Do not infer missing information.
Return null when a field cannot be read.
Do not determine regulatory compliance.
```

### Fallback safety rules

1. Gemini does not approve or reject labels.
2. Gemini does not replace deterministic validation.
3. If PaddleOCR and Gemini materially disagree on an important field, result = **REVIEW**.
4. If Gemini is unavailable, times out, reaches quota, or is not configured, the application must continue functioning.
5. If both recognition paths remain uncertain, result = **REVIEW**.
6. The API key must never be committed to GitHub.
7. Prototype images sent through the optional external service must be non-sensitive demonstration data only.
8. Production federal use would require separate security, privacy, retention, network, and approved-service review.

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
- required warning wording;
- warning heading capitalization;
- other exact statutory text requirements implemented in the prototype.

Government-warning text should use strict text/case validation where the requirement is machine-verifiable.

Visual requirements such as bold styling, exact font size, or layout should remain **manual review** in the MVP unless a separately tested implementation is added later.

## 8. User-Facing Result States

The application has three outcomes:

### PASS

The prototype found the required evidence and deterministic checks matched.

### REVIEW

The system encountered uncertainty, disagreement, unreadable evidence, unsupported visual-format checks, or another condition requiring human judgment.

### FAIL

A deterministic check found a clear mismatch or missing required element within the prototype's supported scope.

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
Detected:    Government Warning:
Result:      FAIL / REVIEW
Reason:      Required heading capitalization did not match the configured rule.
```

The UI should also show:

- which OCR path was used;
- whether Gemini fallback was required;
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

Gemini fallback may exceed the local-only path and should be treated as an exception path rather than the normal processing path.

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

PaddleOCR uncertain + Gemini succeeds
-> validate extracted evidence, indicate fallback used

PaddleOCR uncertain + Gemini unavailable
-> REVIEW

PaddleOCR and Gemini disagree materially
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
├── packages.txt
├── README.md
├── docs/
│   └── ARCHITECTURE.md
├── src/
│   ├── image_processing.py
│   ├── ocr.py
│   ├── extraction.py
│   ├── normalization.py
│   ├── validation.py
│   └── gemini_fallback.py
├── tests/
│   ├── test_normalization.py
│   └── test_validation.py
└── sample_labels/
```

This structure is a starting point, not a requirement to create unused files.

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

> The prototype uses OpenCV to improve label images and PaddleOCR as the primary local text-recognition engine. The extracted fields are compared with application data using ordinary Python validation rules, with RapidFuzz only where harmless formatting differences should be tolerated. If the local OCR cannot reliably read a difficult image, Gemini can be used as an optional last-resort text-extraction fallback. Gemini never determines compliance, and if the systems disagree or remain uncertain, the case is routed to human review.

## 18. Current Decision State

**Locked for implementation v0.1:**

```text
Streamlit
+ OpenCV
+ PaddleOCR PP-OCRv5 mobile
+ RapidFuzz
+ deterministic Python compliance rules
+ optional Gemini image-text fallback as last resort
```

No application code should contradict this architecture unless this document is deliberately revised first.
