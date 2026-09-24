# Project Management & Delivery Record

**Project:** Treasury Take-Home Assessment — TTB Label Verification Prototype  
**Status:** Active — compressed requirements-to-prototype delivery phase  
**Last updated:** 2026-09-23  
**Internal stabilization/submission target:** Saturday, 2026-09-26 end of day  
**Delivery approach:** Human-directed, ChatGPT-assisted, vertically sliced AI prototype development

## 1. Purpose

This document records where the project has been, where it is now, what decisions have been made, which risks remain, and what the next delivery gate requires.

It is written for human reviewers as well as future project handoffs.

The project-management approach is informed by:

- **PMI-CPMAI™** for AI-project lifecycle structure;
- **OPM Federal Program and Project Management guidance** for federal project-management competencies and work behaviors;
- the **Treasury IT Specialist (Artificial Intelligence), GS-2210-12 through GS-15** announcement for job-specific AI expectations.

This file does **not** claim that the project or developer has been formally evaluated at a particular General Schedule grade. It records observable project behaviors and work products so reviewers can assess the evidence directly.

## 2. Mission

Build a working browser-based prototype that helps a TTB compliance reviewer compare distilled-spirits label evidence against application/reference data.

The prototype must:

- reduce routine manual comparison work;
- preserve human judgment for ambiguous cases;
- remain explainable;
- tolerate imperfect label images;
- avoid unnecessary cloud dependence;
- fail safely;
- prioritize a working core over incomplete breadth.

## 3. Stakeholder Mission Needs

| Stakeholder | Mission need | Project response |
|---|---|---|
| Sarah Chen — Deputy Director | Faster review, simple UX, eventual batch capability | Five-second target for simple labels, minimal UI, measured latency, batch deferred until core works |
| Marcus Williams — IT Systems Administrator | Standalone prototype, network/firewall awareness, security/privacy discipline | Local-first OCR, no COLA integration, no persistent document store, Gemini optional only |
| Dave Morrison — Senior Compliance Agent | Preserve regulatory judgment and avoid literal false mismatches | Tolerant comparison only where appropriate, explainable evidence, PASS / REVIEW / FAIL |
| Jenny Park — Junior Compliance Agent | Exact warning checks and better handling of poor images | Deterministic warning rules, image-quality triage, targeted OCR retries, human review for unsupported visual requirements |

## 4. AI Project Lifecycle — PMI-CPMAI Alignment

The project uses the current PMI-CPMAI six-phase methodology as a lifecycle reference.

| PMI-CPMAI phase | Project interpretation | Current status | Exit evidence |
|---|---|---|---|
| I — Matching AI with Business Needs | Define mission problem, stakeholders, success criteria, scope, and whether AI is appropriate | **SUBSTANTIALLY COMPLETE** | Stakeholder analysis, architecture baseline, scope boundaries |
| II — Identifying Data Needs for AI Projects | Identify application fields, label-image evidence, regulatory sources, and test data needs | **IN PROGRESS** | Government source registry complete; requirements matrix still pending |
| III — Managing Data Preparation Needs for AI Projects | Define image-quality triage, preprocessing, synthetic labels, normalization, and data-quality controls | **DESIGNED / NOT IMPLEMENTED** | Performance architecture and synthetic-test strategy documented |
| IV — Iterating Development and Delivery of AI Projects | Build vertical slices and validate working behavior incrementally | **NOT STARTED** | First runnable end-to-end vertical slice |
| V — Testing & Evaluating AI Systems | Evaluate reliability, explainability, error handling, latency, and regression behavior | **PLANNED** | pytest, synthetic regression labels, deployed benchmarks |
| VI — Operationalizing AI | Deploy prototype, document limitations, monitor behavior, plan future integration boundaries | **PLANNED** | Deployed Streamlit URL, runbook/README, measured limitations |

The phases are treated as iterative. New evidence may send the project back to an earlier phase.

## 5. Current Lifecycle Position

The project is **between requirements definition and implementation readiness**.

Current gate:

> Regulatory requirements must be traceable to authoritative sources and classified as AUTOMATE / REVIEW / CONDITIONAL before the first production-intent rule set is coded.

Current implementation state:

- application code: **not started**;
- architecture: **v0.2 locked baseline**;
- performance design: **documented**;
- government-source registry: **documented**;
- AI-development protocol: **documented**;
- TTB requirements matrix: **next major artifact**.

## 6. Scope

### In scope for the MVP

- distilled-spirits label verification;
- browser-based Streamlit interface;
- JPG/PNG upload;
- camera input if deployment supports it reliably;
- OpenCV image-quality triage and adaptive preprocessing;
- one local OCR engine loaded once;
- application-to-label field comparison;
- deterministic TTB rule checks within documented scope;
- PASS / REVIEW / FAIL outcomes;
- targeted evidence crops;
- bounded OCR retries;
- optional Gemini extraction fallback;
- synthetic test labels;
- automated tests;
- deployed prototype.

### Out of scope for the MVP

- COLA integration;
- production federal authentication;
- database/user accounts;
- enterprise identity;
- full FedRAMP authorization design;
- autonomous regulatory decisions;
- wine and malt-beverage rule packs;
- unrestricted cloud-first OCR;
- complete legal determination of every physical-label requirement.

### Deferred until the core works

- batch uploads;
- CSV batch workflow;
- downloadable results;
- broader conditional TTB rules;
- wine/malt beverage support;
- advanced typography/computer-vision checks.

## 7. Delivery Strategy — Vertical Slices First

The project follows the repository protocol that **vertical viability outranks horizontal breadth**.

Planned delivery sequence:

1. **Vertical Slice 1 — Happy path**
   - one distilled-spirits label;
   - application fields;
   - local OCR;
   - extract brand + alcohol content;
   - deterministic comparison;
   - user-visible result;
   - automated tests.

2. **Vertical Slice 2 — Deterministic mismatch**
   - clear label/application mismatch;
   - FAIL with evidence and explanation.

3. **Vertical Slice 3 — Uncertainty**
   - unreadable or low-confidence evidence;
   - REVIEW rather than fabricated answer.

4. **Vertical Slice 4 — Local rescue**
   - targeted crop;
   - adaptive second OCR pass;
   - bounded retry behavior.

5. **Vertical Slice 5 — External fallback**
   - Gemini extraction only after local failure;
   - no AI-generated compliance decision;
   - network/API failure routes safely to REVIEW.

6. **Vertical Slice 6+ — Rule expansion**
   - additional TTB rules;
   - conditional requirements;
   - evidence crops;
   - batch workflow after single-label viability is measured.

## 8. Requirements Traceability

Every implemented behavior should trace to at least one of:

- Treasury take-home stakeholder requirement;
- official TTB requirement;
- eCFR/federal source;
- deployment constraint;
- measured test/benchmark result.

The future `docs/REQUIREMENTS_MATRIX.md` is the planned system of record for individual regulatory requirements.

No material rule should exist only because it was discussed in chat.

## 9. Architecture Decisions and Alternatives

| Decision | Alternatives considered | Reasoning | Current disposition |
|---|---|---|---|
| Streamlit UI | React/custom web stack | Faster prototype delivery, browser access, fewer moving parts | Approved |
| Local-first OCR | Cloud-first vision API | Marcus's network concern, resilience, privacy, explainability | Approved |
| PaddleOCR PP-OCRv5 mobile preferred | Tesseract, EasyOCR, RapidOCR, cloud OCR | Strong modern OCR capability with local deployment path | Benchmark pending |
| RapidOCR contingency | Run two OCR engines simultaneously | Lower-resource deployment option if PaddleOCR does not fit free hosting | Contingency only |
| Gemini fallback | Gemini-first processing, multiple cloud LLMs | Useful for difficult images but should not become hard dependency | Approved as last resort |
| PASS / REVIEW / FAIL | Binary pass/fail | Preserves human judgment and handles uncertainty explicitly | Approved |
| Bounded multi-pass OCR | Repeat same image indefinitely | Targeted retry improves evidence without uncontrolled latency | Approved |
| Distilled spirits first | Beer + wine + spirits together | Matches assignment sample and controls regulatory scope | Approved |
| Versioned local rule pack | Live scraping TTB.gov per request | Lower latency, reproducibility, reviewed rule changes | Approved |

## 10. Risk Register

| Risk | Probability | Impact | Mitigation / response | Status |
|---|---|---|---|---|
| OCR model exceeds free-host memory budget | Medium | High | One cached model; benchmark PaddleOCR; RapidOCR contingency | Open |
| Streamlit deployment selects unsupported Python interpreter | High (observed) | High | Deploy/redeploy Community Cloud app with Python 3.11 selected in Advanced settings; keep CI on 3.11 | Mitigation active |
| Simple-label latency exceeds stakeholder target | Medium | High | Adaptive preprocessing; bounded retries; measure deployed latency | Open |
| OCR confidently reads incorrect text | Medium | High | Evidence display, conservative automation boundaries, targeted retry, REVIEW on conflict; real integration showed warning case instability, so capitalization is now advisory | Active / demonstrated |
| Gemini/network unavailable | Medium | Medium | Local-first architecture; Gemini optional; REVIEW on fallback failure | Controlled |
| Regulatory rule implemented incorrectly | Low/Medium | High | Government-source registry, requirements matrix, test coverage, source hierarchy | Open until matrix complete |
| Prototype scope expands beyond time budget | Medium | High | Vertical-slice rule, explicit non-goals, deferred feature list | Controlled |
| Visual label requirements cannot be reliably inferred from pixels | High | Medium | Mark unsupported physical/typographic checks for human REVIEW | Controlled |
| Chat context drifts over long sessions | Medium | Medium | PROTOCOLS.md, GitHub source of truth, handoff snapshot | Controlled |
| Batch processing destabilizes single-label path | Medium | Medium | Batch deferred until single-label benchmark and memory gates pass | Deferred |
| Compressed delivery window causes unverified code accumulation | High | High | Mandatory post-write QC; vertical-slice scope control; defer features before reducing tests; final-day stabilization | Active |

Risk levels are qualitative planning labels, not measured statistical probabilities.

## 11. Assumptions and Constraints

### Assumptions

- the take-home prototype may use demonstration/non-sensitive images;
- the evaluator primarily needs a working standalone proof of concept;
- distilled spirits are sufficient for the first complete regulatory slice;
- external AI fallback is allowed for the exercise but may be blocked in a real federal network;
- a human compliance reviewer remains the final authority on ambiguous cases.

### Constraints

- approximately five-second simple-label stakeholder target;
- free/low-cost prototype deployment;
- limited Streamlit Community Cloud CPU/RAM;
- no COLA integration;
- no production federal security authorization;
- regulatory requirements vary by beverage category;
- physical typography and container geometry may not be fully provable from uploaded artwork.

## 12. Quality Gates

A phase or vertical slice is not complete merely because code exists.

### Gate A — Requirement readiness

- official source identified;
- scope classification defined;
- expected PASS / REVIEW / FAIL behavior documented.

### Continuous code-change gate

After every coherent code-change batch, run the applicable syntax/import check, targeted test, fast regression tests, affected-path smoke check, and error/log inspection. A failed gate blocks additional feature layering until corrected.

### Gate B — Implementation viability

- end-to-end slice runs;
- errors handled without fabricated results;
- repository remains runnable;
- latest coherent code-change batch has passed its applicable QC gate.

### Gate C — Test readiness

- unit tests pass;
- relevant negative tests pass;
- synthetic/regression case added where appropriate.

### Gate D — Performance readiness

- elapsed time measured;
- peak-resource behavior inspected;
- no unsupported performance claim made.

### Gate E — Deployment readiness

- public prototype URL works;
- secrets excluded from GitHub;
- README instructions reproduce the application;
- limitations are documented.

## 13. Performance Measures

Planned measures include:

- cold-start time;
- warm simple-label latency;
- warm difficult-label latency;
- preprocessing time;
- OCR inference time;
- fallback time;
- peak memory;
- percentage of test cases resolved locally;
- percentage routed to REVIEW;
- regression-test pass rate;
- 5-label and 10-label batch behavior after the core is stable.

No performance target will be reported as achieved until measured in the deployed environment.

## 14. Compressed Delivery Schedule

Treasury's verified September 21 email requires submission within one week of the earlier of the original assessment receipt date or that email. The human reports original receipt on September 20. The project therefore uses **Saturday, September 26 end of day as an internal safety deadline**, not as a quoted Treasury deadline.

| Date | Delivery focus | Exit condition |
|---|---|---|
| Wed Sep 23 | Finish authoritative TTB requirement classification and lock MVP rule scope | Requirements matrix sufficient to define first vertical slice |
| Thu Sep 24 | Build and continuously QC the first complete label-to-result vertical slice | Runnable core with PASS / REVIEW / FAIL and targeted tests |
| Fri Sep 25 | Add highest-value resilience only: uncertainty handling, targeted retry, integration/deployment work | Stable core, meaningful regression coverage, deployment path working |
| Sat Sep 26 | **Stabilization / submission day** — no nonessential scope expansion | Full regression/smoke QC, deployed URL verified, README/setup verified, secrets checked, submission package inspected |
| Sun Sep 27 | Contingency buffer only | Normal plan must not depend on this day |

### Schedule control

If work slips, defer lower-value features in this order before weakening core QC:

1. batch-processing enhancements;
2. additional conditional regulatory rules beyond the demonstrated core;
3. advanced image-recovery variants;
4. optional polish that does not improve evaluator access, correctness, or explainability.

Do not defer the working core, reproducible setup instructions, safe uncertainty handling, tests protecting implemented behavior, deployed accessibility, or final submission verification.

## 15. Milestone Record

| Milestone | Status | Evidence |
|---|---|---|
| Read and interpret Treasury assignment | Complete | Stakeholder-driven architecture |
| Identify stakeholder pain points | Complete | Architecture / conversation-derived requirements |
| Select initial technology stack | Complete | `docs/ARCHITECTURE.md` |
| Define performance/concurrency model | Complete | `docs/PERFORMANCE_ARCHITECTURE.md` |
| Define distilled-spirits scope | Complete | `docs/TTB_RULE_SCOPE.md` |
| Establish government source registry | Complete | `docs/GOVERNMENT_SOURCES.md` |
| Establish AI-development protocol | Complete | `PROTOCOLS.md` |
| Establish project-management lifecycle record | Complete | this file |
| Build TTB requirements matrix | **Complete** | `docs/REQUIREMENTS_MATRIX.md` |
| Define first vertical slice | **Complete** | Locked in `docs/REQUIREMENTS_MATRIX.md` |
| Implement first runnable slice | **Complete** | Current main implements Streamlit → local PaddleOCR → core extraction → deterministic PASS / REVIEW / FAIL |
| Add automated regression suite | **Core suite complete / ongoing** | 27 fast tests + real OCR/full-pipeline integration workflow passing |
| Deploy Streamlit prototype | **NEXT / ACTIVE** | public deployment and runtime-resource validation pending |
| Benchmark and document results | **Partial** | GitHub Actions: first OCR call 18.093s; warm full pipeline 5.368s; deployed benchmark pending |
| Submission readiness review | Planned — internal target Sep 26 | final QC + deployment + README + submission package |

## 16. Current Work / Next Decision Gate

### Current work

Redeploy and validate the current green first vertical slice on Streamlit Community Cloud using **Python 3.11**.

The first deployment attempt failed before application startup because Streamlit selected Python 3.14.7, while the pinned `paddlepaddle==3.3.1` dependency has no matching CPython 3.14 wheel. The immediate remediation is environment correction, not an application-logic rewrite.

### Current verified build

The current main head (`31b89e734cedf87992c6b785ed43dbe1cfc4a694`) has:

- 27 fast tests passing;
- successful Streamlit startup smoke coverage;
- successful real PaddleOCR integration;
- successful full controlled label-to-result pipeline;
- controlled Paddle 3.3 CPU compatibility through `enable_mkldnn=False`;
- government-warning capitalization routed to human-review advisory because OCR case proved unstable;
- current GitHub Actions timing of 18.093 seconds for the first OCR call and 5.368 seconds for the warm full pipeline.

### Active deployment gate

The first slice remains locked to:

- one Streamlit form;
- one JPG/PNG label image;
- application/reference fields for brand, class/type, ABV, net contents, name/address, import status, and country when applicable;
- one local OCR pass;
- deterministic comparison of the supported core fields;
- textual government-warning validation;
- PASS / REVIEW / FAIL with field-level reasons;
- timing;
- automated tests.

Physical typography/container-geometry checks remain REVIEW. Product-composition-triggered disclosures remain conditional/deferred.

### Exit criteria for first vertical slice

- application starts successfully;
- one representative happy-path label reaches a deterministic result;
- clear ABV mismatch reaches FAIL;
- warning wording/numbering/punctuation are evaluated from OCR evidence, while warning capitalization remains a human-review advisory until a targeted case-verification path is proven reliable;
- missing/unreadable supported evidence reaches REVIEW rather than guessed PASS/FAIL;
- targeted tests and fast regression tests pass;
- README setup instructions reflect the actual runnable application.

## 17. Federal Project-Management Alignment

This section documents alignment to official federal competency language; it is not a formal grade determination.

OPM groups GS-12/13 project/program management as an **Expert-Level** career stage and identifies technical competencies including project management, requirements management, risk management, quality management, stakeholder management, schedule management, scope management, compliance, and knowledge management.

Repository evidence currently maps as follows:

| OPM competency area | Observable project evidence |
|---|---|
| Project management | Lifecycle/status record, milestones, gates, delivery sequencing |
| Requirements management | Stakeholder analysis, TTB scope, planned requirements matrix |
| Risk management | Risk register, fallback design, bounded OCR retries |
| Quality management | pytest/regression plan, synthetic labels, explicit quality gates |
| Stakeholder management | Sarah/Marcus/Dave/Jenny needs mapped to design decisions |
| Scope management | Distilled-spirits-only MVP, explicit non-goals and deferred work |
| Schedule/delivery management | Milestones and vertical-slice sequence |
| Compliance | Official government-source registry and deterministic rule strategy |
| Knowledge management | GitHub as durable source of truth, handoff protocol |
| Performance measurement | Five-second target, benchmark plan, resource constraints |
| Decision making / problem solving | Alternatives analysis, trade-offs, contingency planning |
| Attention to detail | Source hierarchy, rule traceability, explicit uncertainty handling |

## 18. Treasury GS-12 Job-Specific Alignment

Treasury announcement **26-DO-12891471-DH** covers GS-12 through GS-15 IT Specialist (Artificial Intelligence) positions.

The GS-12 specialized-experience language includes assisting in designing, developing, testing, or deploying AI models and prototypes. The announcement also includes a selective factor requiring ability to implement AI solutions in production or test environments.

This project is intentionally structured to produce evidence relevant to that kind of work:

- design of an AI-assisted prototype;
- technology and architecture selection;
- regulatory and stakeholder requirements analysis;
- planned implementation in a test/deployed environment;
- deterministic control of AI outputs;
- test strategy;
- deployment planning;
- performance measurement;
- documented alternatives and risks.

The announcement also identifies four IT competencies:

- Attention to Detail;
- Customer Service;
- Oral Communication;
- Problem Solving.

The stakeholder-centered, explainable, source-traceable design is intended to make those behaviors visible in the repository rather than merely assert them.

## 19. Framework and Source References

### AI project management

- PMI-CPMAI™ — PMI Certified Professional in Managing AI  
  https://www.pmi.org/certifications/ai-project-management-cpmai
- PMI — The Standard for Artificial Intelligence in Portfolio, Program and Project Management  
  https://www.pmi.org/standards/artificial-intelligence

### Federal project management

- OPM Federal Program and Project Management Competency Development Framework — Part I  
  https://www.opm.gov/policy-data-oversight/career-paths-for-federal-program-and-project-management-guide/federal-program-and-project-management-competency-development-framework-part-i/
- OPM Federal Program and Project Management Competency Development Framework — Part II  
  https://www.opm.gov/policy-data-oversight/career-paths-for-federal-program-and-project-management-guide/federal-program-and-project-management-competency-development-framework-part-ii/
- OPM Appendix E — Competency Model Proficiency Level Guidance  
  https://www.opm.gov/policy-data-oversight/career-paths-for-federal-program-and-project-management-guide/appendix-e/

### Job-specific reference

- USAJOBS — IT Specialist (Artificial Intelligence), announcement 26-DO-12891471-DH  
  https://www.usajobs.gov/job/858700600

## 20. Change History

### 2026-09-23 — OCR capitalization scope refinement

Integration evidence:

- PaddleOCR correctly extracted brand, class/type, ABV, net contents, and reconstructed name/address from the controlled full label;
- the warm full pipeline measured 5.206 seconds on the GitHub Actions CPU runner;
- PaddleOCR read the correctly rendered `GOVERNMENT` heading as `GOvERNMENT`;
- the project therefore moved warning capitalization from deterministic first-pass validation to a human-review advisory rather than allowing a false regulatory FAIL.

Warning wording/numbering/punctuation remain automated; targeted case verification remains a later evidence-driven enhancement.

### 2026-09-23 — Requirements gate completed

Completed:

- current official TTB distilled-spirits checklist/source review;
- `docs/REQUIREMENTS_MATRIX.md`;
- AUTOMATE / REVIEW / CONDITIONAL / OUT OF MVP classification;
- first vertical slice definition;
- conditional-rule deferral to protect the working core.

Next gate: deploy the current green slice, verify runtime resource compatibility, and measure deployed latency before considering additional resilience work.

### 2026-09-23 — Compressed delivery controls

Added:

- September 26 internal stabilization/submission target;
- continuous post-write QC gate;
- schedule-compression risk and mitigation;
- final-day stabilization rule;
- scope-reduction order for schedule recovery.

### 2026-09-23 — Initial record

Established:

- project lifecycle and current position;
- PMI-CPMAI phase mapping;
- federal project-management competency alignment;
- Treasury GS-12 job-specific alignment;
- milestone record;
- risk register;
- quality gates;
- vertical delivery sequence;
- next decision gate.
