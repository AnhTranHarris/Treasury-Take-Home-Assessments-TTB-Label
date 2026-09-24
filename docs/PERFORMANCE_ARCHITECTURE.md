# Performance Architecture — v0.2

**Status:** DESIGN BASELINE  
**Goal:** Keep the simple-label path fast, memory-bounded, explainable, and deployable on free Streamlit Community Cloud.

## 1. Performance Principle

The objective is **maximum useful concurrency**, not maximum simultaneous work.

Memory-heavy OCR inference must not be duplicated merely to create parallelism. The design should instead use a bounded pipeline:

1. lightweight input normalization;
2. lightweight image-quality analysis and application-field normalization;
3. one warm OCR engine;
4. lightweight extraction and deterministic validation;
5. Gemini only when the local result is unresolved;
6. human review when evidence remains uncertain.

## 2. Deployment Constraint

Streamlit Community Cloud currently documents approximate resource ceilings of:

- up to 2 CPU cores;
- up to 2.7 GB RAM;
- up to 50 GB storage.

PaddleOCR's published PP-OCRv5 mobile CPU benchmark shows substantial peak RAM usage, so the deployment must not create multiple PaddleOCR model instances or multiprocessing workers that duplicate model memory.

Exact performance on Streamlit must be measured. Published upstream benchmarks are not promises for this deployment.

## 3. Single Shared OCR Model

Load the OCR engine once with `st.cache_resource`.

Conceptual structure:

```python
@st.cache_resource
def get_ocr_engine():
    return build_ocr_engine()
```

Because Streamlit global cached resources are shared between sessions, inference must be thread-safe. If the selected OCR runtime cannot safely accept concurrent calls, protect inference with one process-wide `threading.Lock`.

Do not create one OCR model per request or per browser session.

## 4. Safe Concurrency

### Good candidates for parallel or overlapped work

Before OCR:

- application/reference-field normalization;
- image metadata inspection;
- blur estimate;
- brightness/contrast estimate;
- glare estimate;
- orientation estimate;
- image hashing.

After OCR:

- field parsing;
- evidence-crop creation;
- independent deterministic validation checks;
- result formatting.

External fallback:

- Gemini is network I/O and may be executed asynchronously or in a worker only after the local confidence gate requests it.

### Work that should remain serialized by default

- local OCR inference;
- model initialization;
- high-resolution image enhancement variants;
- full-image retries;
- any operation that creates another large model instance.

## 5. No Multiprocessing in the MVP

Python multiprocessing can duplicate model memory. Under the free-hosting memory ceiling, this is an unacceptable default.

The MVP should prefer:

- one Python process;
- one cached OCR engine;
- bounded threads only for lightweight or I/O-bound work;
- no worker process pool.

If future benchmarking proves another model/runtime can support safe process-level parallelism within the memory budget, that can be revisited as a documented architecture change.

## 6. Adaptive Image Strategy

Do not generate many full-size preprocessing variants in parallel.

Use an adaptive decision tree:

```text
Decode image
   |
   v
Create small quality-analysis copy
   |
   v
Measure blur / brightness / glare / orientation
   |
   v
Choose only the corrections that are needed
   |
   v
Create one OCR-ready image
   |
   v
OCR
```

Suggested starting strategy for benchmarking:

- quality-analysis thumbnail: small/cheap representation;
- OCR image: capped maximum dimension rather than unrestricted original resolution;
- first pass: moderate resolution;
- if specific fields are uncertain: retry only the relevant crop or use Gemini, rather than rerunning the entire high-resolution image repeatedly.

The final pixel limits must be selected by benchmark, not guessed.

## 7. Evidence Crops

After OCR provides text locations, create small evidence crops for:

- brand;
- class/type;
- alcohol content;
- net contents;
- name/address;
- country of origin when relevant;
- government warning.

These small crops are inexpensive and help the human reviewer inspect exactly what the system used.

The government-warning crop is especially important because visual properties such as bold type and exact physical type size are not automatically trusted by the MVP.

## 8. Image-Quality Triage

The OpenCV layer should measure and report, where practical:

- blur/sharpness;
- brightness;
- contrast;
- glare/highlight saturation;
- orientation/skew;
- image dimensions.

The quality score is **not a compliance score**.

It is used only to decide whether preprocessing or fallback is required.

## 9. OCR Confidence vs. Compliance Result

Keep these concepts separate.

```text
OCR confidence
= how confident the recognition system is about extracted text.

Compliance result
= PASS / REVIEW / FAIL produced by deterministic rules.
```

Never display a fabricated percentage such as "94% compliant."

## 10. Gemini Fallback

Gemini remains a last-resort extraction service.

Trigger examples:

- important field missing;
- field below tested OCR-confidence threshold;
- health warning incomplete;
- locally extracted evidence internally inconsistent.

Gemini receives only the image/crop and a constrained extraction schema.

Gemini never determines PASS/FAIL.

If Gemini conflicts materially with local OCR, result = REVIEW.

If Gemini is unavailable, result = REVIEW rather than application failure.

## 11. Caching

Use caching selectively.

### Cache resource

- OCR model/runtime loaded once.

### Cache data

Potentially cache short-lived OCR/extraction results keyed by:

- SHA-256 of image bytes;
- OCR engine/model version;
- preprocessing configuration version.

Use bounded entries/TTL. Do not create a permanent document store.

Uploaded images should not be retained beyond what the prototype requires.

## 12. Batch Processing

Batch mode is a pipeline, not "N OCR engines at once."

Conceptual design:

```text
uploaded items
     |
     v
bounded preprocessing queue
     |
     v
ONE local OCR worker
     |
     v
postprocess + validation
     |
     +--> optional Gemini rescue queue
     |
     v
results table / CSV
```

The exact queue size and thread count are benchmark parameters.

Initial implementation should prioritize single-label latency. Batch throughput comes second.

## 13. Benchmark Gates

Before claiming the stakeholder five-second goal, benchmark the deployed application.

Record at minimum:

- cold start;
- warm simple-label latency;
- warm difficult-label latency;
- OCR-only time;
- preprocessing time;
- Gemini fallback time;
- peak memory;
- behavior with 5-label and 10-label batches.

Pass/fail thresholds should be documented from measured results.

## 14. OCR Runtime Contingency

Preferred baseline:

- PaddleOCR PP-OCRv5 mobile.

### Current CPU runtime compatibility control

The pinned prototype currently uses PaddleOCR 3.7.0 with PaddlePaddle 3.3.1 on CPU.

A real GitHub Actions integration run on 2026-09-23 successfully installed the pinned runtime and downloaded both PP-OCRv5 mobile models, but inference failed inside PaddlePaddle's oneDNN/PIR executor with:

```text
ConvertPirAttribute2RuntimeAttribute not support
[pir::ArrayAttribute<pir::DoubleAttribute>]
```

Upstream PaddleOCR/PaddlePaddle reports identify this as a PaddlePaddle 3.3.x CPU oneDNN regression. Current PaddleOCR documentation exposes `enable_mkldnn` as a supported inference parameter.

For the current prototype, **disable MKL-DNN/oneDNN acceleration** with:

```python
PaddleOCR(
    ...,
    enable_mkldnn=False,
)
```

Reasoning:

1. correctness and runnable compatibility outrank acceleration;
2. this is a narrowly targeted workaround for an observed upstream runtime defect;
3. current package versions remain pinned rather than introducing a broader downgrade during the compressed delivery window;
4. the five-second goal remains a measured deployment target rather than an assumption.

If disabling oneDNN causes unacceptable deployed latency, the next tested alternatives are:

1. benchmark PaddlePaddle 3.2.2 with oneDNN enabled, because upstream reports identify 3.2.x as a pre-regression path;
2. benchmark RapidOCR as the already-approved deployment contingency.

Do not change runtime versions solely on speculation. Each alternative must pass real OCR integration and performance QC before adoption.

### Activated Python 3.14 deployment contingency

The first Streamlit Community Cloud deployment used Python 3.14.7. Dependency resolution failed before application startup because PaddlePaddle 3.3.1 has no compatible CPython 3.14 wheel.

The repository now uses Python environment markers plus a runtime backend factory:

- Python 3.11–3.13 → PaddleOCR/PaddlePaddle;
- Python 3.14 → RapidOCR 3.9.2 + ONNX Runtime 1.30.0.

Exactly one OCR backend is active. This is not ensemble OCR and the engines are never raced against each other.

GitHub Actions now verifies both environments independently. On the Python 3.14.7 job, the deployment dependency set installed successfully, Streamlit passed its health check, RapidOCR processed the controlled demo label, all supported deterministic checks passed, and the controlled full pipeline measured **1.200 seconds**.

That result is evidence for compatibility and a controlled CI performance observation. It is **not** a Streamlit Community Cloud performance claim; deployed latency and memory still require measurement.

The Python 3.11/Paddle path remains separately gated and green. The fallback was activated because of observed interpreter/package incompatibility, not because PaddleOCR was removed as the preferred supported-runtime engine.

Do not add `packages.txt` or Linux GUI libraries speculatively. If Community Cloud next reports a concrete shared-library error (for example `libGL.so.1`), add only the required system package and rerun deployment QC.

## 15. Four Accepted Additions

The architecture now includes:

1. OpenCV image-quality triage before OCR.
2. Targeted evidence crops for human review.
3. RapidOCR as the activated deployment contingency for incompatible host runtimes while preserving a single active OCR engine.
4. Synthetic test labels + pytest + GitHub Actions for regression QA.

These additions are accepted design requirements for v0.2.


## 16. Performance Priority Order

When optimization goals conflict, use this order:

1. **Correct deterministic decisions.**
2. **Never fabricate uncertain evidence.**
3. **Meet the approximately five-second simple-label target when deployment measurements permit.**
4. **Remain within the free-host CPU and memory budget.**
5. **Gracefully survive Gemini or network failure.**
6. **Improve batch throughput.**
7. **Add advanced image-recovery techniques.**

This order is intentional. A faster result is not acceptable if it weakens correctness, silently guesses unreadable text, or makes the application unstable.

## 17. Pipeline-Concurrency Rule

Use concurrency only where the tasks are both independent and inexpensive enough to coexist inside the deployment budget.

Preferred pattern:

```text
cheap input normalization
        +
cheap image-quality analysis
        |
        v
one adaptive preprocessing path
        |
        v
ONE warm OCR engine
        |
        v
field parsing + evidence crops + deterministic validation
        |
        v
optional Gemini rescue only if unresolved
```

Do not race PaddleOCR and Gemini on every request.

Do not launch multiple OCR model instances merely to increase parallelism.

The implementation should prefer **pipeline concurrency and resource reuse** over model-level parallelism.


## 18. Adaptive Multi-Pass OCR Strategy

The prototype should not repeat the exact same OCR request multiple times and treat repetition as independent confirmation.

Repeated recognition is useful only when the evidence or processing path changes.

### Pass 1 — Fast full-label pass

Run the normal local path:

```text
uploaded image
    |
    v
light/adaptive OpenCV preprocessing
    |
    v
one PP-OCRv5 mobile pass
    |
    v
field extraction + OCR confidence
```

If all required fields are extracted with sufficient tested confidence and the deterministic checks can proceed, stop immediately.

Do not perform an unnecessary second pass and do not call Gemini.

### Pass 2 — Targeted local rescue

If Pass 1 leaves one or more important fields unresolved:

1. identify the problem field/region using OCR bounding boxes where possible;
2. crop only that region;
3. apply only the correction appropriate to the problem, such as enlargement, contrast improvement, deskewing, thresholding, or perspective correction;
4. run OCR on the targeted crop.

Examples of priority retry targets:

- alcohol content;
- government warning;
- brand;
- class/type.

Do not rerun the entire high-resolution image when a small evidence crop is sufficient.

### Optional narrow third local attempt

A third local attempt may be allowed only when testing demonstrates that a specific alternative preprocessing transform materially improves a critical crop without violating the latency/memory budget.

It must remain bounded and targeted.

The implementation must never loop indefinitely until OCR produces a desired value.

### Gemini escalation

Escalate to Gemini only after the bounded local passes leave a critical field unresolved or contradictory.

Gemini receives the original image or the most relevant evidence crop and a constrained extraction schema.

Gemini remains extraction-only and never determines compliance.

### Agreement handling

Multiple OCR passes improve evidence quality; they do not vote on regulatory compliance.

Examples:

```text
Pass 1: 45% Alc./Vol.
Pass 2: 45% Alc./Vol.
=> stronger extraction evidence
=> deterministic Python rules decide result
```

```text
Pass 1: 45% Alc./Vol.
Pass 2: 46% Alc./Vol.
=> extraction conflict
=> Gemini rescue or REVIEW
```

A repeated identical result from the same pixels/model/configuration is not treated as independent confirmation.

### Confidence states

The implementation may internally classify extraction status conceptually as:

```text
GREEN  -> sufficient local evidence; validate now
YELLOW -> targeted local retry
RED    -> unresolved/missing/conflicting evidence; Gemini or REVIEW
```

Exact numerical thresholds are test-derived configuration values, not design-time assumptions.

### Bounded-pass rule

Default MVP maximum:

- one full-image local OCR pass;
- one targeted local OCR retry;
- optionally one additional narrow crop retry only if benchmark evidence justifies it;
- then Gemini fallback or human REVIEW.

This bounded escalation protects Sarah's latency requirement, Marcus's resource/network concerns, Dave's need for human judgment, and Jenny's difficult-image requirement.
