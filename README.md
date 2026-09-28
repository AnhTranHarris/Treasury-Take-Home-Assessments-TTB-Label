# Treasury Take-Home Assessment — TTB Label Verification

Prototype repository for the **AI-Powered Alcohol Label Verification App** take-home assessment.

## Current Status

**Requirements gate complete. The distilled-spirits prototype now supports two user workflows, including a label-first auto-fill path designed for low-friction human review.**

**Quick Label Review** accepts one label image, performs local OCR once, spatially groups detected evidence, auto-fills TTB-oriented label fields beside the uploaded image, and flags uncertain/missing extraction for human review before deterministic label screening.

**Compare to Reference** preserves the original application/reference comparison workflow and remains the path for independent consistency checking.

PASS means the implemented automated checks passed. It is **not** a complete legal-compliance determination.

## Quick Start

**Python 3.11 is the preferred local-development/PaddleOCR target.** The runtime dependency set is now interpreter-aware: Python 3.11–3.13 use PaddleOCR/PaddlePaddle, while Python 3.14 uses the tested RapidOCR/ONNX Runtime deployment contingency.

```bash
git clone https://github.com/AnhTranHarris/Treasury-Take-Home-Assessments-TTB-Label.git
cd Treasury-Take-Home-Assessments-TTB-Label

python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install the prototype runtime:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the browser application:

```bash
streamlit run streamlit_app.py
```

The local Streamlit URL will be printed in the terminal.

### First OCR initialization

On Python 3.11–3.13, the application selects PaddleOCR PP-OCRv5 mobile. A machine that does not already have the required Paddle model assets cached may require network access during initial model initialization.

On Python 3.14, where PaddlePaddle 3.3.1 has no compatible wheel, the application selects RapidOCR with ONNX Runtime instead. Exactly one local OCR backend is active in a process.

## Reproducible Demo Label

Generate a synthetic distilled-spirits label:

```bash
python -m scripts.generate_demo_label
```

This creates:

```text
sample_labels/demo_happy_path.png
```

Use the application's default reference values and upload that image for a controlled happy-path demonstration.

The synthetic image is a regression/demo fixture. It is not an example of a complete legally approved commercial label.

## Fast Tests

The normal regression suite deliberately avoids downloading or initializing heavyweight OCR models.

```bash
python -m pip install -r requirements-test.txt
python -m pytest -q
```

GitHub Actions runs the same fast test suite on pushes and pull requests.

A separate **OCR integration** workflow verifies both supported runtime paths:

- Python 3.11 + PaddleOCR/PaddlePaddle;
- Python 3.14 + RapidOCR/ONNX Runtime.

The current fast suite has **52 tests**, and both real-OCR integration jobs pass.

## Architecture

The submission architecture and supporting decisions are documented here:

- [Brief Documentation — Approach, Tools, Assumptions & Maturation Path](docs/BRIEF_DOCUMENTATION.md)
- [Project Management & Delivery Record](PROJECT_MANAGEMENT.md)
- [Architecture v0.4](docs/ARCHITECTURE.md)
- [Performance Architecture](docs/PERFORMANCE_ARCHITECTURE.md)
- [TTB Rule Scope](docs/TTB_RULE_SCOPE.md)
- [TTB Requirements Matrix](docs/REQUIREMENTS_MATRIX.md)
- [Extraction Refinement & Blind-Test Protocol](docs/EXTRACTION_REFINEMENT_AND_BLIND_TEST.md)
- [Government Source Registry](docs/GOVERNMENT_SOURCES.md)

Current implementation baseline:

```text
Streamlit
+ OpenCV
+ one runtime-selected local OCR backend:
    - PaddleOCR PP-OCRv5 mobile on Python < 3.14
    - RapidOCR + ONNX Runtime on Python 3.14
+ deterministic Python validation rules
+ human review for unresolved evidence
```

Core principle:

> **AI extracts evidence. Python rules determine the prototype result. Ambiguous cases go to a human reviewer.**

## Quick Label Review Workflow

The default user workflow is:

```text
upload label image
        ↓
one local OCR pass
        ↓
spatial evidence grouping
        ↓
auto-fill core TTB-oriented fields
        ↓
human visually reviews yellow warnings beside image
        ↓
edit / confirm extracted values
        ↓
Run TTB label checks
        ↓
PASS / REVIEW / FAIL for supported label-screening rules
```

Core auto-fill fields are based on current TTB distilled-spirits labeling guidance:

- brand name;
- class/type designation;
- alcohol content statement;
- net contents;
- bottler / producer / importer name and address;
- import status;
- country/origin when applicable;
- government health warning.

The UI also exposes conditional fields for age statements, specified color disclosures, and commodity statements. A blank conditional field is not treated as proof of compliance or noncompliance because applicability can depend on product facts not visible in the artwork.

A provisional OCR-score review gate of **0.90** is used only to decide whether an auto-filled value should be visibly flagged for human review. It is **not** a compliance-confidence threshold and should be tuned against the benchmark label set.

Label-derived values are not treated as independent application data. Use **Compare to Reference** when independent application/reference consistency is required.

## First Vertical Slice

Current user inputs:

- brand name;
- class/type;
- alcohol content (% Alc./Vol.);
- net contents;
- bottler / producer / importer name and address;
- imported yes/no;
- country of origin when imported;
- one JPG/PNG label image.

Current automated checks include:

- application/reference brand consistency;
- class/type consistency;
- numeric ABV consistency;
- supported mandatory alcohol-statement form;
- net-contents consistency when visible;
- name/address consistency;
- imported country-of-origin consistency when applicable;
- government-warning wording, numbering, and punctuation after whitespace normalization; heading capitalization is surfaced as a human-review advisory because real OCR integration showed case instability.

The application separately surfaces manual-review advisories for requirements the MVP cannot safely establish from ordinary OCR pixels, including warning boldness, physical type size/characters-per-inch/true contrast, and full physical same-field-of-vision geometry.

## Result Model

Overall automated precedence:

```text
any supported deterministic FAIL
        -> FAIL

otherwise any unresolved supported automated check
        -> REVIEW

otherwise all supported automated checks pass
        -> PASS
```

Human-review advisories remain visible even when the supported automated result is PASS.

## Current Limitations

The repository intentionally does **not** claim complete TTB compliance.

### Submission scope decisions

- **Live camera capture is disabled.** File upload is the tested path. Camera capture needs broader testing across mobile devices, browsers, permissions, orientation metadata, compression, lighting, and webcam hardware before it should be enabled.
- **External generative-AI fallback is not implemented.** Before any Google Gemini or similar service could be used in a federal environment, the design would require additional cybersecurity, privacy, network, data-handling, authorization, and vendor/service review. Unresolved evidence therefore routes to a human reviewer.


Current limitations include:

- distilled spirits only;
- one label image at a time;
- local OCR first pass only in the current runnable slice;
- targeted OCR retry is designed but not yet part of the first submitted code path;
- external generative-AI fallback is intentionally excluded pending federal cybersecurity, privacy, network, and authorization testing;
- batch processing is deferred;
- physical typography/container-geometry requirements remain human-review items;
- composition-dependent disclosures such as sulfites, certain colors, age statements, and other conditional rules are documented but deferred from the core MVP;
- no COLA integration, production federal authentication, user database, or production authorization claim.

## Performance Principle

The prototype uses **maximum useful concurrency, not maximum simultaneous work**.

The intended runtime model is:

- lightweight input and image analysis may overlap where beneficial;
- one cached/warm OCR engine performs local inference;
- deterministic validation remains lightweight;
- uncertain evidence routes to human review rather than being guessed.

The stakeholder target is approximately five seconds for a simple label. Current controlled GitHub Actions evidence includes:

- Python 3.11/PaddleOCR: 18.093 seconds for the first OCR call and 5.368 seconds for the warm full pipeline;
- Python 3.14/RapidOCR: 1.200 seconds for the controlled full demo-label pipeline.

The five-label deployed benchmark on Streamlit Community Cloud completed in 2.55–4.09 seconds per label (mean approximately 3.15 seconds) on the RapidOCR path. This is a small benchmark set, not a universal latency guarantee. The blind holdout labels will provide additional evidence.

## Development Approach

This prototype uses a **human-directed, AI-assisted development process**.

The human developer retains responsibility for scope, requirements, architecture decisions, trade-offs, and acceptance of changes. ChatGPT assists with source research, implementation, testing, debugging, performance analysis, and documentation.

The version-controlled collaboration rules, source-verification process, mandatory post-write QC, change-control process, and chat-session handoff procedure are documented in:

- [Human + ChatGPT Development Protocol](PROTOCOLS.md)

AI-generated or AI-modified code is treated as provisional until executable QC passes. Time pressure reduces scope before it reduces testing.

## Source Transparency

Official government websites and publications used to define or verify regulatory requirements are maintained separately in the [Government Source Registry](docs/GOVERNMENT_SOURCES.md).

Individual TTB requirements and the prototype's AUTOMATE / REVIEW / CONDITIONAL / OUT OF MVP decisions are recorded in the [TTB Requirements Matrix](docs/REQUIREMENTS_MATRIX.md).

## Project Status

Lifecycle, milestones, risks, quality gates, decisions, and the current delivery position are maintained in the [Project Management & Delivery Record](PROJECT_MANAGEMENT.md).

The record uses PMI-CPMAI as an AI-project lifecycle reference and official OPM/USAJOBS material for federal project-management and job-specific alignment. It records evidence and project state without making a self-awarded General Schedule grade determination.


## Streamlit Community Cloud Deployment

The deployment is designed to survive either interpreter outcome currently encountered on Community Cloud.

Preferred path:

1. choose this repository and branch `main`;
2. use `streamlit_app.py` as the entrypoint;
3. if Advanced settings offers Python 3.11, select it;
4. deploy.

Runtime behavior:

- Python 3.11–3.13 → PaddleOCR/PaddlePaddle;
- Python 3.14 → RapidOCR/ONNX Runtime.

The repository does not rely on `runtime.txt` or `.python-version` to force Streamlit Community Cloud's interpreter. Instead, `requirements.txt` uses Python environment markers so Python 3.14 does not attempt to install incompatible PaddlePaddle wheels.

The application displays the active local OCR backend near the top of the UI.

GitHub Actions separately verifies both the Python 3.11/Paddle path and the Python 3.14/RapidOCR deployment-contingency path before changes are accepted.

### Native OpenCV libraries on Community Cloud

RapidOCR currently depends on the regular `opencv-python` package. Streamlit Community Cloud runs on Debian Linux, so native libraries required by OpenCV must be declared separately.

The repository therefore includes a root-level `packages.txt` containing:

```text
libgl1
libglib2.0-0
```

These packages address the observed Community Cloud failure at `import cv2` and the corresponding `libGL` / GLib dependency pattern documented by Streamlit Community users.

If another native-library error appears, add only the library named by the new deployment log rather than expanding the operating-system dependency list speculatively.


## Submission Presentation

The Streamlit interface uses a restrained federal-document visual style inspired by the current TTB.gov information hierarchy: dark-blue agency-style header treatment, blue action hierarchy, white/gray content areas, and green accents. The application prominently identifies itself as an **unofficial take-home prototype** and does not use an official TTB seal or imply agency endorsement.

Typography and spacing use current OPM/USAJOBS federal résumé guidance as a presentation baseline: sans-serif type, clear title/body hierarchy, and approximately 0.5-inch-equivalent page gutters. These résumé recommendations are adapted for browser readability rather than treated as web-development requirements.
