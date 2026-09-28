# Extraction Refinement and Blind-Test Protocol

**Date:** 2026-09-27

## Purpose

Record the evidence-driven extraction refinement performed after the five-label deployed benchmark and preserve two future labels as a genuine blind holdout set.

## Observed problem

The deployed OCR generally recognized visible text well, but field extraction showed semantic and layout defects: brand/class over-capture, address contamination by later headings, origin ambiguity, mixed ABV/net-content lines, missed street addresses, and uncertain fields that could pass merely because they were non-empty.

The primary problem was therefore mapping OCR text and bounding boxes to the correct regulatory field, not basic text recognition.

## Community research used

Community material is engineering input, not regulatory authority.

- Reddit: separate OCR from key-information extraction rather than expecting OCR alone to solve document understanding: https://www.reddit.com/r/MachineLearning/comments/10ht9ua
- Reddit: normalize page coordinates / relative geometry so spatial features are less dependent on image resolution: https://www.reddit.com/r/MachineLearning/comments/x1ghor
- Reddit: associate form fields using bounding-box distance and geometry rather than reading order alone: https://www.reddit.com/r/MachineLearning/comments/1jd1xxp
- Reddit: use specialized OCR/bounding-box tools when precise text location matters: https://www.reddit.com/r/LocalLLaMA/comments/1johxka
- PaddleOCR GitHub: PP-Structure can require task-specific fine-tuning on layouts not represented in its training data: https://github.com/PaddlePaddle/PaddleOCR/issues/12036
- PaddleOCR GitHub: layout recovery can merge separate logical regions: https://github.com/PaddlePaddle/PaddleOCR/discussions/14176
- RapidOCR GitHub: word-box behavior is not a ready-made English word-level layout solution, so line boxes remain the stable evidence source here: https://github.com/RapidAI/RapidOCR/discussions/412

## Decision

Do not add PP-Structure, LayoutLM, a VLM, Gemini, or a second OCR pass for this refinement.

Reasons:

1. Current OCR already recognizes most benchmark text well.
2. The defect is primarily field association and section boundaries.
3. Heavier layout models add memory/runtime/deployment risk.
4. Community reports show layout recovery is not automatically reliable on novel layouts.
5. A small deterministic improvement is easier to regression-test under the project deadline.

## Accepted extraction strategy

### Anchor-first extraction

Explicit structured labels take priority when present. SPIRIT TYPE is associated with its nearby class/type value, and ORIGIN is associated with its nearby origin value. Nearby values are selected using same-row / same-column geometry rather than raw OCR order.

### Resolution-independent spatial reasoning

Bounding-box relationships are scaled relative to observed page width and height where practical, reducing sensitivity to upload resolution.

### Section-boundary stops

Address collection stops when unrelated sections begin, including GOVERNMENT WARNING, PRODUCT DETAILS, batch/lot/product-detail keys, and URLs.

### Exact sub-value extraction

ABV and net-contents extraction returns the matched regulatory value instead of the entire OCR line. For example, a line containing '90% ALC/VOL | 550 ML' yields alcohol content '90% ALC/VOL' and net contents '550 ML'.

### Street-address fallback

When no explicit importer/producer prefix is detected, the extractor can associate a nearby company name, street-address pattern, and city/state evidence.

### Brand/class contamination controls

Brand grouping excludes obvious strength/tagline text and non-Latin-only subtitle text when a stronger Latin brand candidate exists. Class/type extraction prefers explicit SPIRIT TYPE values, otherwise groups nearby class-bearing lines and penalizes long sentence-like marketing prose.

### Human-review propagation

A yellow core field no longer becomes PASS merely because it contains text. If a highlighted core field has not been explicitly reviewed, the downstream supported rule remains REVIEW.

### Conditional-field noise reduction

Age, specified color, and commodity disclosures are conditional. If merely not detected, they stay neutral rather than automatically generating a yellow warning.

## Regression evidence

The fast suite now includes targeted regression cases derived from the known development labels:

- Kuroyama: exact ABV isolation and exclusion of Japanese subtitle from brand.
- Blackhaven: explicit ORIGIN precedence and address stop before warning.
- Iron Harbor: strength descriptor excluded from brand and contradictory import/U.S. origin routed to review.
- Copper Fox: spatial street-address recovery and domestic inference.
- Ember Coast: explicit SPIRIT TYPE precedence and website exclusion from address.
- Real TTB two-panel fixture: multiline class grouping without cross-column contamination.
- Unresolved highlighted fields propagate to REVIEW.

Current post-refinement QC:

- 52 fast tests pass.
- Python 3.11 + PaddleOCR integration passes.
- Python 3.14 + RapidOCR/ONNX integration passes.

## Blind-test holdout rule

The human has reserved two additional labels for blind testing.

Until the first blind run is complete, ChatGPT must not inspect those labels for tuning, manually encode their expected OCR text into tests, create label-specific rules from their artwork, tune thresholds based on them, or use their layout to change anchor/geometry logic.

Blind-test sequence:

1. Freeze the current green code.
2. Upload blind label 1 and capture the untouched first-run output.
3. Upload blind label 2 and capture the untouched first-run output.
4. Score both results.
5. Only then analyze any new failure modes.

The first-run blind outputs must be preserved before any further code changes.

## Blind-test scoring

For each blind label, record processing time; each core field as correct, partial, wrong, or review; whether yellow review was appropriate; whether any field silently passed despite bad extraction; and the overall supported result.

A correct REVIEW is preferable to a confident wrong extraction.

## Acceptance principle

A blind-test defect should produce a new code change only if it represents a generalizable failure mode.

> Generalize from the failure, not from the filename.