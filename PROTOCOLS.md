# Human + ChatGPT Development Protocol

**Protocol version:** 1.5  
**Effective date:** 2026-09-23  
**Applies to:** Treasury Take-Home Assessment — TTB Label Verification Prototype

## 1. Purpose

This document defines the operating protocol for the human-directed, ChatGPT-assisted development of this repository.

It has two audiences:

1. **ChatGPT**, which must use this file as the persistent development contract for research, architecture, implementation, testing, documentation, and handoff.
2. **Human reviewers**, who may use it to understand how AI assistance was governed during development.

This file exists so important project decisions do not depend on long-chat memory, informal recollection, or assumptions reconstructed many messages later.

## 2. Development Model

This project uses **human-directed, AI-assisted software development**.

The human developer retains decision authority over:

- project scope;
- acceptance criteria;
- architecture approval;
- external-service use;
- trade-offs;
- regulatory assumptions;
- feature acceptance;
- submission readiness.

ChatGPT may assist with:

- requirements analysis;
- source research;
- official-source verification;
- architecture design;
- implementation;
- code review;
- testing;
- debugging;
- performance analysis;
- documentation;
- regression analysis;
- GitHub maintenance.

ChatGPT must not silently replace the human decision-maker.

## 3. README vs. Protocols

`README.md` is written primarily for the hiring manager, interviewer, or other human reviewer.

`PROTOCOLS.md` is the operational contract for the human + ChatGPT collaboration.

The README may summarize and link to this file, but should not become an internal development notebook.

## 4. Source Authority Order

When sources conflict, use this order unless the human explicitly directs otherwise:

1. Treasury take-home assignment.
2. Official TTB.gov guidance.
3. Applicable official federal regulations and other official government sources.
4. Official documentation for frameworks, libraries, APIs, and hosting platforms.
5. Upstream GitHub repositories for the technologies being used.
6. Reproducible tests and measured application behavior.
7. Secondary technical sources.
8. Prior chat discussion, memory, or unverified assumptions.

If a lower-authority source conflicts with a higher-authority source, the higher-authority source controls.

Chat history is never authoritative merely because something was discussed earlier.

## 5. Repository as the Persistent Source of Truth

Important decisions must be committed to GitHub.

Current governing documents include:

- `README.md` — human-facing project overview;
- `PROTOCOLS.md` — development and handoff protocol;
- `PROJECT_MANAGEMENT.md` — lifecycle, risks, milestones, quality gates, and current delivery status;
- `docs/ARCHITECTURE.md` — product architecture;
- `docs/PERFORMANCE_ARCHITECTURE.md` — runtime/performance rules;
- `docs/TTB_RULE_SCOPE.md` — supported regulatory scope;
- `docs/GOVERNMENT_SOURCES.md` — official government-source registry;
- future `docs/REQUIREMENTS_MATRIX.md` — machine-readable/implementation-oriented TTB requirement mapping.

When chat memory and committed documentation differ, ChatGPT must inspect the repository and use the committed documentation unless the human explicitly changes it.

## 6. Evidence and Verification Rules

ChatGPT must not invent:

- TTB requirements;
- statutory wording;
- regulatory thresholds;
- framework capabilities;
- API pricing or limits;
- hosting constraints;
- stakeholder requirements;
- benchmark results;
- test results;
- deployment behavior.

When a material fact is uncertain, ChatGPT must do one of the following:

1. verify it from an authoritative source;
2. mark it as `TBD`;
3. document it as an assumption;
4. route the application behavior to `REVIEW` where uncertainty is operationally relevant.

The development equivalent of the application's safety rule is:

> **Uncertain evidence is verified, not guessed.**

## 7. Regulatory Research Protocol

Before implementing a TTB rule:

1. identify the exact requirement;
2. verify it against TTB.gov or another authoritative federal source;
3. determine whether the rule is universal, conditional, beverage-specific, or outside MVP scope;
4. determine whether it is machine-verifiable from the evidence available to the prototype;
5. define PASS / REVIEW / FAIL behavior;
6. record the source;
7. create tests before or with implementation.

For each automated rule, the project should eventually be able to identify:

- stable rule ID;
- rule description;
- source/reference;
- date reviewed when recorded;
- automation level;
- supported scope;
- failure/review behavior;
- associated tests.

## 8. AI Boundary During Runtime

The same control philosophy applies to runtime AI.

AI systems may:

- extract visible text;
- estimate OCR confidence;
- identify candidate evidence regions;
- assist with difficult-image recovery.

AI systems may not:

- independently determine legal/regulatory compliance;
- fabricate missing text;
- silently resolve conflicting evidence;
- override deterministic rules;
- convert uncertainty into PASS.

PaddleOCR/RapidOCR provide local recognition.

Gemini is optional and last-resort only.

Deterministic Python rules produce the supported PASS / REVIEW / FAIL result.

## 9. Architecture Change Protocol

For a meaningful architecture change:

```text
PROPOSE
   ↓
RESEARCH / VERIFY
   ↓
DOCUMENT RATIONALE
   ↓
UPDATE GOVERNING DOCS
   ↓
IMPLEMENT
   ↓
TEST
   ↓
MEASURE
   ↓
ACCEPT OR ROLLBACK
```

ChatGPT must not silently change architecture because a different approach appears convenient during coding.

If implementation evidence shows an existing decision is poor, document the reason before changing the baseline.

## 10. Coding Protocol

Implementation should favor:

- small modules with clear responsibility;
- explicit interfaces between OCR, extraction, validation, and UI;
- deterministic behavior where possible;
- graceful failure;
- readable code;
- no unnecessary dependencies;
- no unused architecture scaffolding merely to appear sophisticated.

A feature is not complete because code exists.

Completion requires appropriate tests and working behavior.

### Mandatory continuous QC after code writes

Because this take-home has a compressed delivery window and the human cannot manually inspect every AI-assisted code change at programming-engineer speed, **every coherent code-change batch must pass executable QC before another feature is layered on top of it**.

A coherent code-change batch is a logically complete edit such as adding or modifying one validator, parser, OCR adapter, UI behavior, configuration path, or tightly related set of files. This rule does not require rerunning an expensive full OCR/deployment suite after every individual line.

Minimum post-write QC, as applicable:

1. syntax / import / dependency check for the changed code;
2. targeted test for the behavior that changed;
3. fast regression tests protecting previously working behavior;
4. application or module smoke check for the affected path;
5. inspect exceptions, tracebacks, warnings, and logs;
6. if any check fails, fix and repeat QC before proceeding.

AI-generated or AI-modified code is **provisional until it has been executed and verified**.

Expensive integration checks should be risk-based. OCR changes must exercise OCR. Streamlit changes must smoke-test the UI/application startup path. Regulatory-rule changes must run the relevant positive and negative rule tests. Documentation-only changes do not require loading the OCR model.

At the completion of each vertical slice, run the broader gate appropriate to the implemented scope, including unit/regression tests, synthetic or representative input, error path, application path, dependency/import checks, and performance/resource measurements when relevant.

### Time-pressure safety rule

**Time pressure reduces scope before it reduces QC.**

If the delivery schedule becomes threatened:

```text
reduce or defer features
        ↓
preserve the working vertical core
        ↓
run QC
        ↓
document deferred work
        ↓
submit a stable prototype
```

Do not respond to schedule pressure by stacking unverified code, removing tests, or claiming behavior that has not been executed.

## 11. Vertical-Slice Viability Rule

Horizontal coding and vertical coding both matter, but **vertical coding has priority for prototype viability**.

For this project:

- **horizontal coding** means building breadth across one technical layer, such as creating many validators, many OCR helpers, many UI controls, or many rule modules before an end-to-end workflow is proven;
- **vertical coding** means completing a thin end-to-end path that starts with user input and finishes with a tested user-visible result.

The project should prefer this sequence:

```text
small working vertical slice
        ↓
test it end to end
        ↓
measure it
        ↓
preserve the working path
        ↓
expand the next vertical slice
        ↓
only then broaden horizontally where useful
```

The first implementation target should therefore be a minimal but complete distilled-spirits path such as:

```text
Streamlit input
   ↓
one label image
   ↓
image preprocessing
   ↓
local OCR
   ↓
extract core fields
   ↓
one or more deterministic checks
   ↓
PASS / REVIEW / FAIL result
   ↓
tests
```

After that path works, additional capability should be added in vertical increments, for example:

1. valid happy-path label;
2. clear deterministic mismatch;
3. unreadable/uncertain evidence routed to REVIEW;
4. targeted OCR retry;
5. optional Gemini fallback;
6. additional TTB rules;
7. conditional requirements;
8. batch workflow.

### Viability gate

Before beginning substantial horizontal expansion, ChatGPT should ask:

> **Does the repository still contain a runnable, testable end-to-end prototype path?**

If the answer is no, restore a working vertical slice before expanding breadth.

Do not create large amounts of disconnected scaffolding, rule modules, UI surfaces, or integrations that cannot yet participate in a runnable workflow.

### Reason

The Treasury assignment explicitly prefers a working core application with clean code over ambitious but incomplete features.

Therefore prototype viability outranks architectural breadth.

Horizontal refactoring and breadth are appropriate after the relevant vertical path works and when they improve maintainability, testability, performance, or future extension.

## 12. Project Management Record Maintenance

`PROJECT_MANAGEMENT.md` is the human-facing lifecycle and delivery record for this repository.

ChatGPT should update it when a material project-management event occurs, including:

- lifecycle phase change;
- milestone completion;
- new material risk or mitigation;
- major scope decision;
- architecture decision with delivery impact;
- benchmark/performance gate result;
- deployment event;
- change to the next vertical slice;
- project handoff;
- submission-readiness decision.

The file must distinguish:

- completed work from planned work;
- measured results from targets;
- project evidence from self-evaluation;
- official federal competency language from any informal interpretation.

The file may map repository evidence to PMI/OPM/Treasury frameworks, but it must not claim that the project formally establishes a General Schedule grade or certification.

At every major phase gate, ChatGPT should verify that `PROJECT_MANAGEMENT.md` accurately reflects the repository's actual state.

### Compressed submission-window control

Treasury's verified September 21, 2026 email states that the assessment must be submitted within one week of the earlier of the original assessment receipt date or that email. The human reports first receiving the assessment on September 20.

For project management, use **Saturday, September 26, 2026 end of day as the internal hard stabilization/submission target**. This is a conservative internal safety deadline, not a claim that Treasury explicitly stated September 26 as the official deadline.

Sunday, September 27 is treated only as contingency buffer. Normal feature development must not depend on that buffer.

As the internal target approaches:

- prioritize the working vertical core;
- stop nonessential scope expansion;
- reserve the final day for regression testing, deployment verification, README/setup verification, secrets review, and submission-package inspection;
- document deferred features rather than destabilizing the prototype.

## 13. Temporary Interview Readiness Protocol — ACTIVE

### Purpose

Maintain a private Google Docs interview-preparation guide for this Treasury application so the human can prepare for a possible live interview using verified evidence from the application record, project repositories, and current federal role requirements.

This protocol is temporary. It remains active through the current Treasury application/interview cycle unless the human explicitly deactivates, replaces, or extends it.

### Evidence separation

The interview guide must keep three categories visibly separate:

1. **Formal documented record** — facts supported by the current résumé, SF-50, and other official employment/application records.
2. **Project-demonstrated capability** — behaviors, technical decisions, artifacts, tests, repositories, and outcomes demonstrated through portfolio/project work.
3. **Knowledge-growth bridge** — GS-13 or future-role concepts the human is studying and preparing to discuss, but must not present as prior professional experience unless separately documented.

ChatGPT must never merge project evidence into formal qualifying employment, convert self-directed study into claimed professional experience, or imply a General Schedule qualification that the formal record does not establish.

### Private-document boundary

The interview guide is a private personal study artifact in the human's Google Drive.

**Canonical private guide title:** `Treasury AI Interview Preparation Guide — Anh T. Tran (Harris)`

The guide should be maintained in the human's private `ChatGPT` Google Drive folder when available. The document URL must not be committed to this public repository.

Do not:

- commit the private Google Doc link to this public repository;
- copy Social Security numbers, dates of birth, personnel action identifiers, personal telephone numbers, supervisor telephone numbers, or other unnecessary personal identifiers into GitHub;
- reproduce the SF-50 itself in this repository;
- expose private interview-preparation notes in the public README.

The guide may summarize non-sensitive facts necessary for preparation, such as current federal series/grade, role type, documented duties, and verified project evidence.

### Authoritative preparation sources

Use this order for interview-preparation content:

1. current résumé and SF-50 actually available to ChatGPT;
2. current repository/project evidence and measured outcomes;
3. current Treasury job announcement;
4. current OPM qualification/competency guidance;
5. current official federal AI/cybersecurity guidance such as NIST/CISA when relevant;
6. current PMI AI-project-management material where useful;
7. prior chat discussion only when corroborated by the sources above.

If a source cannot support a claimed accomplishment, the guide must label it as study, inference, planned work, or unavailable rather than filling the gap.

### Required guide content

The living interview guide should include, as applicable:

- a truthful professional introduction;
- the formal-record baseline and important discrepancies to verify before interview;
- GS-12 job-specific expectations;
- GS-13 knowledge/experience gap analysis;
- the TTB prototype architecture and stakeholder rationale;
- likely technical and project-management interview questions;
- concise answer frameworks;
- STAR-style examples grounded in actual employment or verified project work;
- project portfolio examples that demonstrate transferable capability;
- AI governance, human-in-the-loop, testing, security, and risk questions;
- Agile and DevSecOps study material where relevant;
- questions for the interview panel;
- a demo/interview-day checklist;
- a vocabulary/reference section;
- official source links.

### GS-13 through GS-15 stretch-ladder rule

GS-13 through GS-15 preparation is a **graduated knowledge-growth ladder**, not a claim of current equivalent employment or formal qualification.

Where the Treasury announcement identifies GS-13 requirements beyond the GS-12 prototype baseline, the guide should:

1. identify the specific additional requirement;
2. explain what the human already has evidence for;
3. identify the actual gap;
4. provide a concise study explanation;
5. connect the concept to this project where truthful;
6. state what must not be claimed without real experience.

For the current announcement, the preparation depth is:

- **GS-13:** working knowledge of AI/cloud cybersecurity practices and Agile sprint planning/execution, with truthful connections to project controls;
- **GS-14 stretch:** identify senior-executive alignment responsibilities and AI cybersecurity risk-assessment responsibilities, and sketch a rough roadmap for how the work should proceed;
- **GS-15 super-stretch:** grasp the enterprise concepts behind collaborative project direction, cloud-native modernization, production-grade AI systems, DevSecOps, enterprise AI strategy, and cross-agency coordination, and explain a high-level conceptual roadmap.

The guide must make the decreasing evidence level explicit as the grade rises. GS-14 and GS-15 material is for recognition, structured reasoning, vocabulary, dependencies, and roadmap thinking—not for claiming prior execution or leadership.

### Project evidence rule

Other repositories may be used to demonstrate transferable behaviors such as:

- requirements decomposition;
- iterative experimentation;
- testing and QA;
- technical risk management;
- source/provenance control;
- human-in-the-loop governance;
- exception/failure handling;
- documentation;
- replayability/auditability;
- structured AI workflows.

They must not be represented as paid employment or formal federal specialized experience unless the underlying record actually supports that characterization.

### Maintenance triggers

ChatGPT should refresh the private interview guide when any of the following occurs:

- the TTB requirements matrix is completed;
- the first runnable vertical slice is completed;
- meaningful automated tests pass;
- measured latency/memory results become available;
- Gemini fallback is implemented/tested;
- the app is deployed;
- a major architecture decision changes;
- a new verified portfolio artifact materially improves an interview example;
- the human receives an interview invitation;
- the human requests mock-interview preparation.

Do not create duplicate interview guides. Search for and update the existing guide by title unless the human explicitly requests a new version.

### Interview-invitation escalation

If an interview is scheduled:

1. re-check the current job announcement and any interview instructions;
2. refresh the guide against the latest repository state;
3. prioritize answers supported by completed evidence over planned work;
4. add likely panel questions mapped to the announcement's competencies;
5. add timed 30-second, 60-second, and 2-minute answer variants where useful;
6. prepare a mock panel/quiz workflow if requested;
7. flag any résumé/SF-50/application inconsistency that should be resolved before the interview.

### Rapid interview-preparation window

Because the date of any live interview is unknown, prepare as though a live interview could occur by approximately **Wednesday, September 30, 2026**.

The objective is not to become a full programming-engineering expert in a few days. Preparation should optimize for **project mastery and defensible technical literacy**.

Priority order:

1. understand and explain the mission, stakeholders, requirements, architecture, risks, and failure behavior;
2. trace a label through the actual implemented code path from input to PASS / REVIEW / FAIL;
3. read and explain the Python constructs actually used by this project;
4. understand and run the project's tests;
5. diagnose a basic traceback or failed test and explain the debugging path;
6. make or explain a small bounded rule change safely;
7. discuss GS-13 AI/cloud cybersecurity and Agile concepts accurately without claiming experience not held;
8. recognize GS-14 responsibilities and sketch a rough roadmap;
9. grasp GS-15 enterprise concepts at a high level.

Generic programming study is subordinate to the code actually used in this repository. Focus on functions, variables, dictionaries/data models, classes where used, conditionals, imports, exceptions, lists, return values, tests/assertions, configuration/secrets, module boundaries, and reading tracebacks.

Before submission, interview study should not jeopardize the prototype. After the stable submission package is complete, increase interview-practice intensity using the private guide and the final repository evidence.

### Sunset rule

After this Treasury application/interview cycle ends, the human may:

- deactivate this temporary protocol;
- archive the guide;
- convert it into a general federal AI interview-preparation protocol;
- or delete the temporary section.

ChatGPT must not silently keep the protocol active after the human explicitly ends it.

## 14. Testing Protocol

Before declaring a material feature complete, check as applicable:

1. unit tests;
2. regression tests;
3. synthetic-label tests;
4. negative/error cases;
5. stakeholder requirement mapping;
6. regulatory source mapping;
7. performance measurement where relevant;
8. documentation updates.

Tests must not be described as passing unless they actually ran and passed.

## 15. Performance Protocol

Performance changes must follow the priority order documented in `docs/PERFORMANCE_ARCHITECTURE.md`.

In particular:

- correctness outranks speed;
- uncertainty must not be fabricated away;
- one warm OCR model is preferred;
- multiple OCR model instances are not created merely for parallelism;
- adaptive local retries are bounded;
- Gemini is not raced against local OCR on every request;
- deployment performance must be measured rather than assumed.

## 16. Git and Commit Discipline

Preferred commit prefixes:

- `docs:` — documentation, architecture, requirements, research;
- `feat:` — new capability;
- `fix:` — defect correction;
- `test:` — tests and fixtures;
- `perf:` — measured performance work;
- `refactor:` — structural change with no intended behavior change;
- `chore:` — maintenance.

Meaningful architectural changes should be identifiable from Git history.

Do not commit secrets, API keys, private credentials, or sensitive information.

## 17. Why Normal Chat May Be Used Instead of Work

This project may intentionally use a normal ChatGPT conversation for research, design, and iterative implementation rather than handing every phase to ChatGPT Work.

Reasons may include:

- the human wants direct conversational control over each design decision;
- the human wants to interrupt and redirect reasoning as requirements are discovered;
- the project benefits from explicit discussion before code changes;
- the human prefers more deliberate management of context and token usage during long research/design sessions;
- the current task may not require the additional multi-step execution capabilities of Work;
- maintaining the GitHub documents as the durable project state reduces dependence on any one ChatGPT execution mode.

This is a workflow choice, not a claim that one ChatGPT mode is universally better.

Work may be used later when its capabilities materially improve a task. If that occurs, the same repository protocol and source hierarchy still apply.

## 18. Chat Length and Session Handoff Protocol

Long conversations can become difficult to navigate and may approach practical context limits.

The repository must make a clean handoff possible without relying on the previous chat transcript.

### Handoff trigger

A handoff should be prepared when one or more of these conditions occurs:

- the conversation has become very long;
- important decisions are being repeated because earlier context is hard to recover;
- ChatGPT shows uncertainty about previously settled project state;
- the human plans to start a new chat;
- a major project phase has completed;
- the human explicitly requests a handoff.

### Before handoff

ChatGPT should update the **Current Handoff Snapshot** section of this file with:

- date;
- current architecture/protocol version;
- latest known relevant commit;
- current project phase;
- locked decisions;
- recently completed work;
- unresolved questions;
- known risks;
- exact next recommended task;
- governing files the next ChatGPT session must read.

If the handoff state becomes too large for this file, the protocol may later be amended to use a dedicated handoff document. Until then, this file is the canonical handoff anchor.

### New-chat bootstrap

At the start of a new ChatGPT development session, ChatGPT should:

1. inspect the current GitHub repository;
2. read `PROTOCOLS.md`;
3. read `README.md`;
4. read `PROJECT_MANAGEMENT.md`;
5. read `docs/ARCHITECTURE.md`;
6. read `docs/PERFORMANCE_ARCHITECTURE.md`;
7. read `docs/TTB_RULE_SCOPE.md`;
8. read `docs/GOVERNMENT_SOURCES.md`;
9. read any requirements/handoff file named by this protocol;
10. inspect recent commits if needed;
11. verify the requested task against the current repository state before changing code.

ChatGPT should not reconstruct the project from remembered chat history when the repository contains the answer.

## 19. Protocol Amendment Procedure

This protocol is intentionally updateable.

The human may change, add, remove, or refine protocols when the collaboration reveals a meaningful reason to do so.

Examples include:

- a better handoff process;
- a recurring source-verification failure;
- a new testing requirement;
- a better Git workflow;
- a deployment limitation;
- a new regulatory-source requirement;
- an AI behavior that needs tighter control.

When the human approves a protocol change:

1. update this file;
2. increment the protocol version when the change is material;
3. record the reason in the protocol changelog;
4. ensure other governing documents are updated if affected.

ChatGPT must not silently amend this protocol on its own.

If ChatGPT identifies a needed protocol change, it should propose the change to the human or clearly identify it while carrying out an already-authorized documentation update.

## 20. Stop / Rollback Rule

If a change:

- breaks previously working behavior;
- conflicts with an authoritative requirement;
- materially increases resource usage without demonstrated benefit;
- weakens explainability;
- introduces unsafe uncertainty handling;
- or cannot be defended from source evidence,

ChatGPT should stop building on that change, identify the problem, and either correct or roll back to the last known-good state.

## 21. Transparency to Human Reviewers

The use of ChatGPT is not hidden.

The intended development story is:

> The human developer directed scope, requirements, architecture, and acceptance decisions. ChatGPT assisted with source research, implementation, testing, debugging, and documentation under a persistent, version-controlled protocol.

The repository should make that process auditable without requiring a reviewer to read the original chat transcript.

## 22. Current Handoff Snapshot

**Date:** 2026-09-23  
**Protocol version:** 1.5  
**Architecture version:** v0.2  
**Latest relevant commit before this snapshot update:** `86214ed36b3464beaba652b4a385f140dda7c275`

### Current phase

Compressed requirements-to-prototype delivery: finish regulatory matrix, then implement and continuously QC the first working vertical slice before the September 26 internal stabilization/submission target.

### Locked decisions

- Streamlit web UI.
- OpenCV image-quality triage and adaptive preprocessing.
- PaddleOCR PP-OCRv5 mobile preferred local OCR.
- RapidOCR is a deployment contingency, not a simultaneous second engine.
- RapidFuzz only for fields where tolerant comparison is appropriate.
- Deterministic Python rules decide supported compliance outcomes.
- Gemini image extraction is optional, last-resort only.
- PASS / REVIEW / FAIL are separate result states.
- One warm OCR engine and bounded adaptive local retries.
- One full local OCR pass, one targeted retry by default, optional additional narrow retry only if benchmark evidence justifies it.
- Synthetic regression labels + pytest + GitHub Actions are accepted QA additions.
- Distilled spirits are the initial regulatory implementation scope.

### Recently completed

- stakeholder pain-point analysis;
- v0.2 architecture documentation;
- performance/concurrency architecture;
- distilled-spirits scope document;
- adaptive multi-pass OCR escalation design;
- government-source registry separated from non-government sources;
- vertical-slice viability rule added to the development protocol;
- project-management lifecycle record added with PMI/OPM/Treasury alignment;
- OPM and USAJOBS sources added to the government-source registry;
- private interview-readiness protocol activated for the current application cycle;
- private Google Docs interview guide initialized under the canonical title recorded in this protocol;
- continuous executable QC required after every coherent code-change batch;
- September 26 internal stabilization/submission target established;
- rapid interview-preparation window established through approximately September 30.

### Unresolved / next research

- complete the deeper TTB.gov requirement analysis;
- build `docs/REQUIREMENTS_MATRIX.md`;
- classify TTB requirements as AUTOMATE / REVIEW / CONDITIONAL;
- decide which conditional fields belong in the MVP UI;
- only then begin application implementation.

### Governing files for the next session

- `PROTOCOLS.md`
- `README.md`
- `PROJECT_MANAGEMENT.md`
- `docs/ARCHITECTURE.md`
- `docs/PERFORMANCE_ARCHITECTURE.md`
- `docs/TTB_RULE_SCOPE.md`
- `docs/GOVERNMENT_SOURCES.md`

## 23. Protocol Changelog

### 1.5 — 2026-09-23

Added:

- mandatory executable QC after every coherent code-change batch;
- rule that AI-assisted code is provisional until executed and verified;
- time-pressure rule requiring scope reduction before QC reduction;
- September 26, 2026 internal stabilization/submission target, with September 27 treated only as contingency buffer;
- final-day stabilization and submission-package controls;
- rapid interview-preparation window through approximately September 30, focused on project mastery rather than broad programming-engineer expertise.

### 1.4 — 2026-09-23

Added:

- five-rung interview-development ladder from GS-11 foundation through GS-15 conceptual awareness;
- GS-14 stretch goal for executive alignment and AI cybersecurity risk-assessment roadmap thinking;
- GS-15 super-stretch goal for enterprise AI strategy, cloud modernization, production AI, DevSecOps, and cross-agency systems thinking;
- explicit rule that GS-14/15 preparation is recognition and roadmap reasoning, not claimed experience.

### 1.3 — 2026-09-23

Added:

- temporary private interview-readiness protocol for the current Treasury application cycle;
- explicit separation of formal documented experience, project-demonstrated capability, and GS-13 knowledge-growth material;
- privacy boundary preventing SF-50/personal data and the private Google Doc link from entering the public repository;
- interview-guide maintenance triggers tied to real project milestones;
- interview-invitation escalation and protocol sunset rules.

### 1.2 — 2026-09-23

Added:

- `PROJECT_MANAGEMENT.md` as the lifecycle/status system of record;
- project-management maintenance rules at phase gates and handoffs;
- PMI-CPMAI lifecycle mapping;
- OPM GS-12/13 project-management competency alignment;
- Treasury GS-12 job-specific evidence mapping;
- project-management file added to new-chat bootstrap.

### 1.1 — 2026-09-23

Added:

- dedicated government-source registry;
- source-separation rule for government websites;
- vertical-slice viability rule;
- explicit priority of working end-to-end prototype paths over horizontal feature breadth;
- government-source registry added to new-chat bootstrap/handoff reading set.

### 1.0 — 2026-09-23

Initial protocol established:

- human + ChatGPT role separation;
- source hierarchy;
- evidence-verification rules;
- architecture/change control;
- testing and Git discipline;
- normal Chat vs Work workflow rationale;
- chat-length handoff procedure;
- updateable protocol governance;
- initial handoff snapshot.
