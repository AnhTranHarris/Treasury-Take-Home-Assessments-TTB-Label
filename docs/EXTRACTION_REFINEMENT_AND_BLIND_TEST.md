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

## Blind-test results — completed

The two holdout labels were run on the frozen build before further extraction tuning.

### Blind label 1 — Liberty Creek

Observed deployed result:

- processing time: 5.51 seconds;
- brand auto-fill: `LIBERTY CEK` — incorrect/partial, correctly routed to REVIEW because OCR confidence was 0.61;
- class/type: `AMERICAN WHITE WHISKEY` — correct;
- alcohol content: `50% ALC/VOL` — correct;
- net contents: `750 mL` — correct candidate but routed to REVIEW because decoy values in a separate stress-test panel created multiple plausible candidates;
- name/address: correct;
- domestic/origin context: reasonable;
- government warning: correct;
- overall result: REVIEW.

Important evidence: OCR also detected a separate `LIBERTY CREEK` instance at 0.888 confidence, showing that brand candidate selection favored a visually larger but lower-confidence damaged rendering.

### Blind label 2 — Raven Creek

Observed deployed result:

- processing time: 3.49 seconds;
- brand auto-fill: `RAVEN CREK` — incorrect/partial, correctly routed to REVIEW at 0.889 confidence;
- class/type: `DISTILLED SPIRIT` — incorrect and incorrectly passed;
- alcohol content: `50% ALC/VOL` — correct;
- net contents: `750 mL` — correct candidate but routed to REVIEW because decoy values in a separate stress-test panel created multiple plausible candidates;
- name/address: correct;
- domestic/origin context: correct;
- government warning: correct;
- overall result: REVIEW.

Critical evidence: OCR detected the structured pair `SPIRIT TYPE:` / `MOONSHINE` at 1.000 confidence. The current class extractor nevertheless ignored that structured value because its controlled class vocabulary did not include `moonshine`, then selected `DISTILLED SPIRIT`. This is a generalizable extraction defect, not an OCR failure.

### New generalizable failure modes

1. **Structured-key vocabulary rejection**
   - An explicit key such as `SPIRIT TYPE:` should not discard a bounded, high-confidence value merely because that value is absent from a local class keyword list.
   - Structured key/value evidence should outrank the fallback vocabulary heuristic.

2. **Explicit non-product-region contamination**
   - Both holdouts contain a separate panel explicitly labeled `NOT PART OF PRODUCT LABEL`.
   - Decoy quantities in that panel caused false net-content ambiguity.
   - Extraction should exclude OCR evidence spatially associated with an explicit non-product marker while retaining it in raw OCR evidence for auditability.

3. **Brand salience versus OCR reliability**
   - The current brand heuristic can prefer the physically largest text even when that OCR candidate is materially less reliable than a smaller duplicate/corroborating brand rendering.
   - A future refinement should combine salience, OCR confidence, and corroborating candidates rather than selecting primarily by text-box size.
   - On severely damaged brand artwork, REVIEW remains an acceptable outcome; the system must not guess merely to avoid human review.

4. **Conditional commodity over-capture**
   - Liberty auto-filled an incomplete marketing fragment ending in `distilled from` as a commodity statement.
   - Conditional commodity extraction should require an actual commodity/object, not merely the trigger phrase.

### Blind-test interpretation

The blind test did **not** justify replacing the OCR engine or adding a large layout/VLM stack.

The strongest new defects are deterministic extraction-policy issues:

- trust explicit structured values more appropriately;
- exclude explicitly marked non-product regions from regulatory field candidate generation;
- improve brand candidate ranking without forcing uncertain damaged text to PASS;
- tighten the optional commodity extractor.

The human-review design performed as intended for damaged brand text and ambiguous net contents: uncertain fields stayed REVIEW rather than silently passing.

### Post-blind change-control gate

The holdout restriction is now satisfied. Further code changes are permitted, but each change must address one of the generalizable failure modes above and must be protected by regression tests representing the behavior rather than the label filename.
