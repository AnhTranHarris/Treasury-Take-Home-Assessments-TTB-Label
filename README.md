# Treasury Take-Home Assessment — TTB Label Verification

Prototype repository for the **AI-Powered Alcohol Label Verification App** take-home assessment.

## Current Status

**Architecture/design phase. Application implementation has not started yet.**

The frozen v0.1 design baseline is documented here:

- [Architecture v0.2](docs/ARCHITECTURE.md)

## Locked Baseline

```text
Streamlit
+ OpenCV
+ PaddleOCR PP-OCRv5 mobile
+ RapidFuzz
+ deterministic Python compliance rules
+ optional Google Gemini image-text fallback as a last resort
```

Core principle:

> **AI extracts evidence. Python rules determine the prototype result. Ambiguous cases go to a human reviewer.**

Implementation changes that materially alter this architecture should update the architecture document first.


## Accepted v0.2 Refinements

- image-quality triage with OpenCV;
- targeted evidence crops;
- RapidOCR as a deployment contingency only;
- synthetic regression labels + pytest + GitHub Actions;
- bounded pipeline concurrency with one warm OCR model;
- distilled-spirits rule pack based on reviewed TTB guidance.
