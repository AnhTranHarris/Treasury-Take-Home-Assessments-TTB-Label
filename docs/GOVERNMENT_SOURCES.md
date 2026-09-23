# Government Source Registry

**Status:** Authoritative-source registry  
**Last reviewed:** 2026-09-23  
**Purpose:** Keep official government sources separate from implementation notes, architecture decisions, and third-party technical documentation.

## 1. Purpose

This file is the project's registry for **government websites and official government publications only**.

It exists so a human reviewer or future ChatGPT session can quickly determine:

- which official government sources informed the project;
- what each source is used for;
- which agency owns the source;
- whether the source is primary or supporting authority;
- when the project last reviewed it;
- which project documents depend on it.

This file must not become a general web bibliography.

Third-party libraries, GitHub projects, hosting documentation, Google/Gemini documentation, community sources, and secondary commentary belong elsewhere.

## 2. Source-Use Rule

Government-source research should follow this order when possible:

1. governing statute or regulation;
2. official agency regulation/guidance page;
3. official agency checklist, form, or publication;
4. another official federal agency source when the requirement crosses agency boundaries.

If two official sources appear to conflict, ChatGPT must not silently reconcile them. The conflict must be documented and resolved through higher-authority or more current official material before implementation.

## 3. Scope Exclusion: Non-Government-Domain Sources

This registry contains official government websites and publications only.

The Treasury take-home assignment is authoritative for this project but is hosted on GitHub rather than a government domain. It is therefore tracked in `PROTOCOLS.md` and the repository project documentation, not in this government-source registry.

Third-party and non-government-domain sources must remain outside this file even when they are important to the project.

## 4. TTB — Distilled Spirits Labeling

### Distilled Spirits Labeling Home

**Agency:** Alcohol and Tobacco Tax and Trade Bureau (TTB), U.S. Department of the Treasury  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling  
**Role:** Primary navigation/source hub for distilled-spirits label requirements  
**Reviewed:** 2026-09-23

Used to establish the distilled-spirits MVP regulatory domain.

### Mandatory Label Information / Brand Label

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label  
**Role:** Required information and same-field-of-vision requirements  
**Reviewed:** 2026-09-23

Used for:

- brand name;
- class/type;
- alcohol content;
- same-field-of-vision context.

### Brand Name

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-name  
**Role:** Brand-name labeling guidance  
**Reviewed:** 2026-09-23

Used for brand-name validation scope and limitations.

### Alcohol Content

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-alcohol-content  
**Role:** Alcohol-content statement requirements  
**Reviewed:** 2026-09-23

Used for:

- percent alcohol by volume;
- permitted presentation/abbreviation concepts;
- distinction between proof and mandatory alcohol-by-volume statement;
- regulatory context separate from application-to-label equality.

### Net Contents

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-net-contents  
**Role:** Net-contents requirements  
**Reviewed:** 2026-09-23

Used for:

- quantity/unit extraction;
- recognition that net contents may appear on the label or elsewhere on the container;
- avoiding automatic failure when submitted artwork alone is insufficient.

### Name and Address

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-name-address  
**Role:** Name/address requirements for distilled spirits  
**Reviewed:** 2026-09-23

Used to scope comparison of expected producer/bottler/importer information.

### Government Health Warning

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning  
**Role:** Government health-warning text and presentation requirements  
**Reviewed:** 2026-09-23

Used for:

- mandatory warning text;
- capitalization;
- presentation requirements;
- separation of machine-verifiable textual checks from physical/visual checks that may require human review.

### Anatomy of a Distilled Spirits Label

**Agency:** TTB  
**Source:** https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/anatomy-of-a-distilled-spirits-label-tool  
**Role:** Supporting explanation of distilled-spirits label elements  
**Reviewed:** 2026-09-23

Used as a supporting implementation reference, not as a substitute for higher-authority regulatory material.

## 5. TTB — Official Distilled Spirits Checklist

### Distilled Spirits Labeling Checklist

**Agency:** TTB  
**Source:** https://www.ttb.gov/system/files/images/labeling-ds/ds-labeling-checklist.pdf  
**Role:** Official review checklist closely matching the workflow described in the Treasury take-home assignment  
**Reviewed:** 2026-09-23

Used to identify and organize:

- brand-name/application comparison;
- alcohol content;
- class/type;
- net contents;
- name/address;
- health warning;
- country of origin for imports;
- sulfite declarations;
- color disclosures;
- age statements;
- commodity statements;
- state-of-distillation disclosures;
- other conditional label elements.

The future `docs/REQUIREMENTS_MATRIX.md` should map individual checklist items to AUTOMATE / REVIEW / CONDITIONAL implementation states.

## 6. eCFR — Federal Regulations

### Electronic Code of Federal Regulations

**Agency / publisher:** U.S. Government Publishing Office / Office of the Federal Register  
**Source:** https://www.ecfr.gov/  
**Role:** Higher-authority regulatory verification when TTB guidance requires confirmation against codified federal regulations  
**Reviewed:** 2026-09-23

Use eCFR when:

- exact regulatory text matters;
- a TTB guidance page summarizes rather than reproduces a requirement;
- a requirement's legal scope/effective language needs confirmation;
- two TTB pages appear inconsistent.

Specific CFR sections should be recorded in the future requirements matrix when implemented.

## 7. U.S. Customs and Border Protection

### CBP

**Agency:** U.S. Customs and Border Protection, Department of Homeland Security  
**Source:** https://www.cbp.gov/  
**Role:** Supporting authority for import/country-of-origin matters when TTB guidance delegates or references customs requirements  
**Reviewed:** 2026-09-23

The MVP should not independently implement broad CBP country-of-origin law unless the requirement is necessary to the take-home scope and has been verified from the specific governing source.

## 8. U.S. Department of the Treasury

### Treasury

**Agency:** U.S. Department of the Treasury  
**Source:** https://home.treasury.gov/  
**Role:** Department-level institutional context only  
**Reviewed:** 2026-09-23

Do not use general Treasury pages as substitutes for TTB-specific beverage-labeling authority.

## 9. OPM — Federal Program and Project Management

### Federal Program and Project Management Competency Development Framework — Part I

**Agency:** U.S. Office of Personnel Management (OPM)  
**Source:** https://www.opm.gov/policy-data-oversight/career-paths-for-federal-program-and-project-management-guide/federal-program-and-project-management-competency-development-framework-part-i/  
**Role:** Federal project/program-management competency framework and GS 12-13 expert-level competency context  
**Reviewed:** 2026-09-23

Used to inform the competency-alignment section in `PROJECT_MANAGEMENT.md`.

### Federal Program and Project Management Competency Development Framework — Part II

**Agency:** OPM  
**Source:** https://www.opm.gov/policy-data-oversight/career-paths-for-federal-program-and-project-management-guide/federal-program-and-project-management-competency-development-framework-part-ii/  
**Role:** Federal work behaviors associated with project/program management career levels  
**Reviewed:** 2026-09-23

Used to inform project-management behaviors such as requirements, risk, quality, stakeholder, scope, schedule, compliance, knowledge management, problem solving, planning, and evaluation.

### Appendix E — Competency Model Proficiency Level Guidance

**Agency:** OPM  
**Source:** https://www.opm.gov/policy-data-oversight/career-paths-for-federal-program-and-project-management-guide/appendix-e/  
**Role:** Proficiency-level guidance and GS 12-13 project-management competency levels  
**Reviewed:** 2026-09-23

Used to avoid vague or inflated descriptions of federal competency expectations.

## 10. USAJOBS — Treasury AI Position

### IT Specialist (Artificial Intelligence), GS-2210-12 through GS-15

**Agency:** U.S. Department of the Treasury, Departmental Offices  
**Source:** https://www.usajobs.gov/job/858700600  
**Announcement:** 26-DO-12891471-DH  
**Role:** Job-specific reference for the Treasury AI position associated with this take-home project  
**Reviewed:** 2026-09-23

Relevant GS-12 context includes:

- assisting in designing, developing, testing, or deploying AI models and prototypes;
- ability to implement AI solutions in production or test environments;
- IT competencies including Attention to Detail, Customer Service, Oral Communication, and Problem Solving.

This source is used for evidence alignment only. The repository does not make a formal qualification or grade determination.

## 11. Source Classification

Government sources used by this project should be classified as one of:

- **PRIMARY REGULATORY** — statute/regulation or direct authoritative regulatory text;
- **AGENCY GUIDANCE** — official TTB guidance interpreting or operationalizing requirements;
- **OFFICIAL CHECKLIST/FORM** — official workflow/checklist source;
- **CROSS-AGENCY SUPPORT** — official source from another agency needed for a conditional rule;
- **FEDERAL CAREER FRAMEWORK** — official OPM career/competency guidance used for project-management alignment;
- **OFFICIAL JOB ANNOUNCEMENT** — official USAJOBS announcement used for position-specific alignment.

The future requirements matrix should reference the relevant government-source classification.

## 12. Update Procedure

When a government source is added or materially re-reviewed:

1. confirm it is an official government source;
2. add or update the entry here;
3. record the review date;
4. identify what part of the project depends on it;
5. update `docs/REQUIREMENTS_MATRIX.md` if a rule changed;
6. update tests if implemented behavior changed;
7. update architecture only if the source change affects architecture.

A government webpage changing does **not** automatically change application behavior. Rule changes enter the program only after deliberate review, documentation, implementation, and testing.

## 13. Separation of Duties

This file answers:

> **Which official government sources govern or inform the prototype?**

Other files answer different questions:

- `PROTOCOLS.md` — how the human + ChatGPT collaboration operates;
- `PROJECT_MANAGEMENT.md` — lifecycle status, decisions, risks, milestones, gates, and federal/AI-project-management alignment;
- `docs/ARCHITECTURE.md` — how the application is designed;
- `docs/PERFORMANCE_ARCHITECTURE.md` — how the application should run efficiently;
- `docs/TTB_RULE_SCOPE.md` — which regulatory domain the MVP supports;
- `docs/REQUIREMENTS_MATRIX.md` — which individual government requirements are automated, conditional, or human-review items.

This separation is intentional so regulatory sources can be reviewed or updated without rewriting the development protocol or application architecture.
