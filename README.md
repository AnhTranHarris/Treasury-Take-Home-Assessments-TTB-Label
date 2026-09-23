# Treasury Take-Home Assessment — TTB Label Verification

Prototype repository for the **AI-Powered Alcohol Label Verification App** take-home assessment.

## Current Status

**Architecture/design phase. Application implementation has not started yet.**

The frozen v0.2 design baseline is documented here:

- [Architecture v0.2](docs/ARCHITECTURE.md)
- [Performance Architecture](docs/PERFORMANCE_ARCHITECTURE.md)
- [TTB Rule Scope](docs/TTB_RULE_SCOPE.md)

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


## Performance Principle

The prototype uses **maximum useful concurrency, not maximum simultaneous work**.

The intended runtime model is:

- lightweight input and image analysis may overlap where beneficial;
- one cached/warm OCR engine performs local inference;
- deterministic validation remains lightweight;
- Gemini is called only for unresolved cases;
- uncertain evidence routes to human review rather than being guessed.

Performance optimization must preserve correctness, explainability, and deployment stability.


## Development Approach

This prototype uses a **human-directed, AI-assisted development process**.

The human developer retains responsibility for scope, requirements, architecture decisions, trade-offs, and acceptance of changes. ChatGPT assists with source research, implementation, testing, debugging, performance analysis, and documentation.

The version-controlled collaboration rules, source-verification process, change-control process, and chat-session handoff procedure are documented in:

- [Human + ChatGPT Development Protocol](PROTOCOLS.md)

This keeps the project auditable without requiring a reviewer to read the original ChatGPT conversation.
