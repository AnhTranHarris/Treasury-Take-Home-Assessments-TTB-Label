# Brief Documentation — Approach, Tools, Assumptions, and Maturation Path

**Project:** AI-Powered Alcohol Label Verification Prototype  
**Author:** Anh Tran (Harris), developed through vibe coding with ChatGPT  
**Status:** Take-home prototype / proof of concept

## 1. What I built

This prototype helps a reviewer examine a distilled-spirits label image without requiring every field to be typed manually.

The default workflow is intentionally simple:

1. choose one of seven built-in synthetic sample labels or upload a JPG/PNG label image;
2. local OCR extracts visible text and bounding boxes;
3. deterministic Python logic groups likely TTB-oriented fields;
4. the application auto-fills editable review fields beside the uploaded image;
5. uncertain or ambiguous extraction is highlighted for human review;
6. supported label checks return PASS / REVIEW / FAIL with reasons.

A second **Compare to Reference** workflow preserves independent comparison against separately supplied expected/application values.

The prototype does **not** claim complete legal or regulatory compliance.

### Built-in reviewer examples

Seven ChatGPT-generated label illustrations are included directly in the GitHub repository. A reviewer can select one from a dropdown beside the upload control instead of downloading test images onto a personal or government workstation. Uploading a different JPG/PNG remains available for independent testing; if both are selected, the uploaded image takes precedence.

These are synthetic **development and stress-test fixtures**, not examples of TTB-approved artwork. Some deliberately contain damaged lettering, decoy panels, ambiguous quantities, and other inconsistencies. A PASS is limited to the checks actually implemented, and some samples should produce REVIEW or FAIL.

**Training disclosure:** The project did not train or fine-tune a custom machine-learning model on the seven images. Existing OCR models extract text; the Python extraction rules were implemented and revised using the known development labels. Liberty Creek and Raven Creek were initially blind holdouts and were added as built-in examples only after the untouched first-run evaluations were recorded. Reviewers can use their own independent label to test generalization.

## 2. My approach to the Treasury problem

I am still developing my programming skills and do not have deep formal software-engineering experience. To deliver a working prototype within Treasury's short take-home schedule, I relied on **vibe coding with ChatGPT** to help research technical options, write and troubleshoot Python code, and integrate existing open-source OCR tools. My role was to interpret the stakeholder needs, decide what the prototype should and should not attempt, review what the software actually produced, and keep the design focused on an easy-to-use label-review workflow.

For quality control, I applied project-management practices I am learning from **PMI's CPMAI approach to AI projects**; this was a learning framework, not a certification or a claim of professional project-manager experience. I broke the work into small, usable stages, documented assumptions and risks, checked code changes with automated tests, and compared actual label results against expected behavior before accepting improvements. When testing exposed unreliable extraction, I kept uncertain fields available for human review rather than claiming the AI was always correct. This approach helped me complete and explain a bounded proof of concept while identifying what would require more training, testing, and federal security review before production use.

## 3. Tools used

### Application

- **Python** — orchestration, extraction, validation, tests.
- **Streamlit** — browser interface and prototype deployment.
- **OpenCV** — image decode/resize preparation.
- **PaddleOCR / PaddlePaddle** — preferred local OCR path on Python 3.11–3.13.
- **RapidOCR / ONNX Runtime** — tested deployment contingency on Python 3.14.
- **GitHub / GitHub Actions** — source control, change history, fast tests, and real-OCR integration checks.
- **pytest** — deterministic regression tests.

Exactly one OCR backend is active in a running process.

### Open-source OCR foundations — GitHub project acknowledgments

To complete a working prototype within the take-home schedule, I **integrated existing open-source OCR libraries instead of attempting to develop or train a new OCR engine**. The two upstream GitHub projects are:

1. **[PaddleOCR — PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)**. Used as the preferred local text-detection and text-recognition engine, configured with PP-OCRv5 mobile models for the supported Python 3.11–3.13 path. PaddlePaddle provides the inference framework.
2. **[RapidOCR — RapidAI/RapidOCR](https://github.com/RapidAI/RapidOCR)**. Used as the alternative local OCR engine with ONNX Runtime for the Python 3.14 deployment path, where the pinned PaddlePaddle dependency does not have a compatible wheel.

Using these established projects saved the time and complexity of creating OCR detection/recognition models from scratch and let me focus the limited assignment window on **TTB-specific field extraction, spatial grouping, deterministic checks, the reviewer interface, human-review safeguards, and testing**. I wrote project-specific provider adapters to convert each engine's outputs into a shared representation of detected text, OCR confidence, and bounding boxes; those adapters are in `src/ocr/`. The two engines are **runtime alternatives**, not a combined two-model voting system; one is selected per run.

**Attribution and scope:** PaddleOCR and RapidOCR are independent open-source projects, not code or models authored by me or ChatGPT. The prototype uses their existing OCR capabilities through Python dependencies and does not train or fine-tune either engine on the seven synthetic labels. The custom work in this repository is the surrounding application and its extraction/validation workflow.

### AI-assisted development

ChatGPT was used as a development collaborator for research, architecture discussion, coding assistance, test design, debugging, documentation, and review.

I retained human control over scope, acceptance, regulatory assumptions, and submission decisions. Source documents, tests, deployment evidence, and reproducible behavior are treated as stronger authority than an AI-generated suggestion.

## 4. Assumptions

- Initial regulatory scope is **distilled spirits**.
- Input is a readable JPG/PNG label image.
- This prototype evaluates only the explicitly implemented rules.
- OCR confidence is an extraction-quality signal, not a compliance probability.
- A yellow field means a human should verify the extracted value against the image.
- Conditional disclosures may depend on product facts that are not visible in the label artwork.
- The prototype has no COLA database integration, permit database, production identity system, or federal authorization to operate.
- A submitted image cannot reliably prove all physical-container requirements such as actual print size or full same-field-of-vision geometry.

### Scenario-based assumptions inferred from the Treasury assignment

These are **my design interpretations** of the stakeholder interviews in the [Treasury take-home instructions](https://github.com/treasurytakehome-rgb/instructions). They are not additional TTB regulations or guarantees about an operational agency system.

**1. Review speed — Sarah Chen.** Sarah said agents abandoned a scanner that took 30–40 seconds and wanted results in about five seconds. I treated five seconds as a target to measure, not a guarantee for every label.

**2. Ease of use — Sarah Chen.** Sarah described reviewers with different levels of technical comfort who needed an obvious interface. I assumed a reviewer should be able to select a sample or upload a label, check auto-filled fields, and see clear results without technical setup.

**3. High-volume submissions — Sarah Chen.** Sarah described importers submitting hundreds of applications at once and said batch processing would be helpful. I treated batch upload as a future enhancement because the assignment favored a complete, working core within limited time.

**4. Restricted network access — Marcus Williams.** Marcus described blocked outbound domains that disrupted a previous vendor's machine-learning features. I assumed the core label-reading workflow should run without calling an external generative-AI service.

**5. Standalone prototype and data protection — Marcus Williams.** Marcus explicitly said the prototype should not integrate with COLA and should avoid sensitive data. I assumed a standalone, sample-driven demonstration was appropriate, while production identity, retention, and security controls remained out of scope.

**6. Harmless differences in names — Dave Morrison.** Dave described a brand name written in uppercase on the label and title case in the application. I inferred that ordinary capitalization differences should not automatically fail appropriate text comparisons, while material differences still need review.

**7. Exact health warning — Jenny Park.** Jenny emphasized that the government warning's wording and heading must be exact, including capitalization and bold formatting. I treated textual checks as strict where reliable, but kept visual typography and physical sizing as human-review items.

**8. Imperfect label images — Jenny Park.** Jenny described glare, poor lighting, and angled photographs as common obstacles. I assumed basic image preparation could help, but unreadable or conflicting OCR evidence should go to a human rather than be guessed.

**9. Application comparison versus label screening — Sarah Chen's review process.** Sarah described comparing application values with what appears on the label artwork. I kept a separate *Compare to Reference* workflow because values extracted from a label cannot independently verify that same label against an application.

**10. Beverage type and conditional rules — assignment technical context.** The instructions note that labeling requirements vary between beer, wine, and distilled spirits and provide a distilled-spirits example. I chose distilled spirits as the initial scope and did not assume a missing conditional disclosure always means a violation.

## 5. Deliberate scope decisions

### Live camera capture — disabled for submission

A live camera path is visible but disabled.

I did not have enough test time to verify camera capture across a representative range of:

- iOS and Android devices;
- mobile browsers;
- desktop/laptop webcams;
- camera permissions;
- image orientation metadata;
- compression/resolution behavior;
- glare, focus, and low-light conditions.

File upload is the tested submission path. Camera capture should be enabled only after cross-device testing demonstrates that it does not reduce reliability or create unnecessary support burden.

### External generative-AI fallback — not implemented

No Google Gemini or other external generative-AI backup is enabled in the submitted prototype.

A cloud AI fallback could potentially help with difficult images, but a federal production path would first require security, privacy, network, data-handling, authorization, and vendor/service review. The prototype therefore remains local-OCR-first and routes unresolved evidence to a human rather than sending label images to an external AI service.

This is a deliberate safety and deployment decision, not a missing runtime dependency.

## 6. Testing and evidence

The repository uses a layered test approach:

- fast unit/regression tests for extraction and validation;
- synthetic label fixtures;
- real OCR integration tests on both supported runtime paths;
- deployed benchmark labels;
- two blind holdout labels that were not used for tuning before their first run.

At the current submission state:

- **57 fast tests pass**;
- Python 3.11 + PaddleOCR integration passes;
- Python 3.14 + RapidOCR/ONNX integration passes;
- a five-label deployed benchmark completed in approximately 2.55–4.09 seconds per label on the RapidOCR deployment path;
- blind testing confirmed that uncertain damaged fields route to REVIEW, while also identifying several future extraction refinements.

The goal was not to make every damaged label pass automatically. A correct REVIEW is safer than a confident wrong answer.

## 7. Known limitations

- distilled spirits only;
- one image at a time;
- live camera disabled;
- no batch processing;
- no external generative-AI fallback;
- no production authentication/authorization;
- no database or COLA integration;
- no federal ATO/FedRAMP claim;
- physical typography and container-geometry requirements remain human-review items;
- very damaged/ambiguous artwork can still require manual correction;
- conditional requirements are not fully automated without product/formulation context.

## 8. How I would mature this system

### Near-term prototype hardening

My next technical steps would be practical and measurable:

- expand the benchmark set with real-world image conditions;
- test mobile/camera capture across representative devices;
- improve generalized field extraction from blind-test findings;
- add batch upload only after the single-label path remains stable;
- strengthen accessibility and user-error handling;
- add structured operational logging and repeatable performance tests.

### Production engineering / security path

Before a federal deployment, I would involve security, infrastructure, privacy, records-management, accessibility, and application owners rather than treating the prototype as production-ready.

Work would include:

- authentication and role-based authorization;
- data-retention and records rules;
- encryption and secrets management;
- audit logging;
- dependency and vulnerability management;
- threat modeling;
- approved network/service boundaries;
- formal testing in the target government environment;
- deployment/rollback procedures;
- incident and operational support planning;
- authorization processes applicable to the hosting/services selected.

Any external generative-AI fallback would enter only after that review establishes what data can leave the application boundary, which service is permitted, and how failures are safely handled.

### Enterprise / program maturation

At larger scale, the problem becomes more than OCR code.

A mature program would need:

- product ownership and measurable service-level objectives;
- integration strategy with authoritative systems such as COLA;
- versioned regulatory rule management;
- governance for model/service changes;
- quality monitoring and reviewer feedback loops;
- accessibility and training;
- change management across compliance teams;
- cost/capacity planning;
- acquisition/vendor and federal cloud considerations where applicable;
- executive risk/benefit decisions about where AI should and should not automate judgment.

I can describe that path and identify the stakeholders and controls it would require. I would still seek experienced federal security, legal/regulatory, infrastructure, and enterprise-architecture guidance before making production decisions outside the prototype scope.

## 9. Main design principle

> **Automate the obvious evidence, expose uncertainty, and keep consequential judgment reviewable by a human.**

That principle guided the implementation and the decisions about what **not** to add before submission.


## 10. Capability posture

This project is intended to show what I can currently do and where I would still need training.

At the hands-on level, I can define a bounded problem, research requirements, build and test a working prototype with AI assistance, inspect failures, preserve evidence, and explain why the code behaves the way it does.

At the next level of responsibility, I can structure work around stakeholder needs, scope control, risk, testing, rollback, documentation, and measurable acceptance criteria. I am still developing deeper formal experience in production software engineering, federal cybersecurity, enterprise integration, and large-team delivery, so I would expect to learn from experienced specialists in those areas.

Looking forward, I can identify the major workstreams that would be required to move this proof of concept toward production: security and privacy review, authorization, infrastructure, identity/access management, records handling, accessibility, operational monitoring, integration with authoritative systems, governance of rule/model changes, and user adoption.

At an enterprise level, I understand that the decision is no longer simply “can the OCR work?” It becomes a program question involving mission value, risk tolerance, policy, acquisition, architecture, workforce impact, funding, governance, accountability, and measurable outcomes across organizations.

I would not present myself as the final authority for those higher-level decisions. I can recognize the path, frame the questions, document the dependencies, and work with the appropriate technical, security, regulatory, and leadership stakeholders to mature the system responsibly.
