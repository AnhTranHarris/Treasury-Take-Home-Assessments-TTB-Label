# Distilled Spirits Requirements Matrix

**Status:** MVP regulatory implementation gate  
**Scope:** Distilled spirits only  
**Reviewed:** 2026-09-23  
**Source basis:** Current official TTB distilled-spirits labeling guidance, TTB Mandatory Label Information Checklist, 27 CFR references identified by TTB, and CBP country-of-origin dependency where applicable.

## 1. Purpose

This matrix separates two different questions that the prototype must not conflate:

1. **Application consistency** — does evidence detected on the submitted label match the reference/application information supplied to the prototype?
2. **Limited regulatory validation** — does the evidence satisfy a machine-verifiable TTB labeling rule that this MVP explicitly implements?

A label can match an application field without proving complete regulatory compliance.

The prototype is not a legal-opinion engine and does not attempt to automate every distilled-spirits labeling requirement.

## 2. Classification

### AUTOMATE

The requirement can be evaluated deterministically from information the prototype can reasonably obtain from the submitted image and/or explicit application inputs.

### REVIEW

The requirement depends on human judgment, physical-container evidence, typography/layout measurements that the MVP cannot reliably establish, ambiguous OCR, or external records not supplied to the prototype.

### CONDITIONAL

The rule applies only when product/application facts trigger it. The image alone is not sufficient to establish whether the rule applies.

### OUT OF MVP

The requirement is valid, but implementation is intentionally deferred to protect the working vertical core within the take-home delivery window.

## 3. Result Semantics

- **PASS** — sufficient reliable evidence exists and the implemented deterministic check matches.
- **FAIL** — sufficient reliable evidence exists and a supported deterministic requirement clearly does not match.
- **REVIEW** — evidence is missing, unreadable, contradictory, externally dependent, physically unverifiable from the submitted image, or outside safe automated judgment.
- **NOT APPLICABLE** — a conditional rule is explicitly known not to apply.

A conditional rule must never be treated as PASS merely because its trigger data was not supplied.

## 4. Source Hierarchy

Primary implementation sources:

1. TTB Mandatory Label Information Checklist — Distilled Spirits  
   https://www.ttb.gov/system/files/images/labeling-ds/ds-labeling-checklist.pdf
2. TTB Distilled Spirits Labeling  
   https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling
3. TTB Mandatory Label Information / Same Field of Vision  
   https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label
4. TTB Anatomy of a Distilled Spirits Label  
   https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/anatomy-of-a-distilled-spirits-label-tool
5. TTB field-specific guidance pages identified below.
6. 27 CFR provisions identified by TTB guidance/checklist.

The older Beverage Alcohol Manual is not used as controlling authority because TTB states that it has not been updated to be consistent with the current 27 CFR part 5 labeling regulations.

## 5. Core MVP Requirements

| Rule ID | Requirement | Application consistency | Limited regulatory check | Automation class | Result behavior | Evidence / input | MVP disposition |
|---|---|---|---|---|---|---|---|
| DS-BRAND-001 | Brand name | Compare detected brand to application Brand Name. Normalize case, whitespace, apostrophe style, and harmless punctuation. Material fuzzy uncertainty routes to REVIEW rather than silently passing. | Presence only. Misleading-brand legal judgment is not automated. | AUTOMATE + REVIEW boundary | Match = PASS; clear reliable mismatch = FAIL; ambiguous/fuzzy-only evidence = REVIEW | Application brand + OCR evidence | **CORE** |
| DS-CLASS-001 | Class/type or other designation | Compare detected designation to supplied expected class/type/designation using conservative normalization. | Presence can be checked; full standards-of-identity/formula correctness is not inferred from artwork alone. | AUTOMATE for supplied reference; REVIEW for regulatory semantics | Match = PASS; reliable mismatch = FAIL; uncertain meaning/formula dependency = REVIEW | Expected designation + OCR evidence | **CORE** |
| DS-ABV-001 | Alcohol content value | Parse numeric percent alcohol by volume and compare to supplied application value numerically. Do not apply product-production tolerance to application-vs-label matching. | Presence of percent-alcohol-by-volume statement. | AUTOMATE | Exact normalized numeric match = PASS; clear mismatch = FAIL; unreadable/conflicting = REVIEW | Expected ABV + OCR evidence | **CORE** |
| DS-ABV-002 | Alcohol-content statement format | Not applicable beyond app match. | Mandatory statement must express percentage alcohol by volume. TTB permits “alc.” and “vol.” abbreviations; “ABV” is not an allowed substitute for the mandatory wording. Optional proof must be distinct from the mandatory percentage statement. | AUTOMATE, limited | Supported format = PASS; clear unsupported mandatory format = FAIL; extraction ambiguity = REVIEW | OCR text around ABV | **CORE** |
| DS-NET-001 | Net contents value | Compare detected metric volume/unit to expected application/reference net contents after unit normalization. | Presence/format can be evaluated when visible. Absence from artwork alone is not an automatic violation because net contents may be blown, embossed, or molded into the container. | AUTOMATE + REVIEW boundary | Visible match = PASS; visible reliable mismatch = FAIL; not found in image = REVIEW | Expected net contents + OCR evidence | **CORE** |
| DS-NET-002 | Net contents format | Normalize L/liter/litre and mL variants documented by TTB. | Check that visible statement uses a supported metric form. | AUTOMATE | Supported visible form = PASS; clear unsupported form = FAIL; no visible statement = REVIEW | OCR text | **CORE** |
| DS-NAME-001 | Bottler/distiller/importer name and address | Compare detected name/address to the supplied application/reference fields using conservative normalization. | Presence can be checked. Identity against a TTB basic permit is not performed because the prototype has no permit database. | AUTOMATE for reference match; REVIEW for permit/legal identity | Match = PASS; reliable mismatch = FAIL; permit-level verification needed = REVIEW | Expected name/address + OCR evidence | **CORE** |
| DS-IMPORT-001 | Country of origin | If application says imported and supplies expected country, compare detected country-of-origin evidence. If domestic, mark NOT APPLICABLE. | Full CBP country-of-origin legal compliance is not determined by this prototype. | CONDITIONAL + AUTOMATE presence/match + REVIEW legal compliance | Imported + visible expected country = PASS for app consistency; missing/ambiguous = REVIEW; reliable different country = FAIL for app consistency | Imported? + expected country + OCR evidence | **CORE CONDITIONAL** |
| DS-WARN-001 | Government health warning textual content | No ordinary application-field comparison; use configured statutory text as reference. | Check exact wording, punctuation, required capitalization of “GOVERNMENT WARNING,” and capitalization of Surgeon/General. Normalize only whitespace/line wrapping that does not change the prescribed statement. | AUTOMATE | Exact supported textual match = PASS; clear textual/case/punctuation defect = FAIL; OCR uncertainty = targeted retry then REVIEW | Warning OCR text | **CORE** |
| DS-WARN-002 | Government warning paragraph separation / continuity | None | TTB requires the warning as one continuous statement and separate/apart from other information. OCR/layout evidence may assist but is not treated as conclusive in MVP. | REVIEW | Show warning crop and reason for human inspection | OCR boxes + evidence crop | **CORE REVIEW** |
| DS-WARN-003 | Government warning boldness | None | “GOVERNMENT WARNING” must be bold; remainder may not be bold. Reliable font-weight determination is outside the text-OCR MVP. | REVIEW | Human review | Warning evidence crop | **CORE REVIEW** |
| DS-WARN-004 | Government warning physical type size / characters per inch / true contrast | None | TTB requirements depend on physical container size and measurable print characteristics. Pixel measurements from an arbitrary uploaded image are not sufficient without calibration. | REVIEW | Human review | Container size context + physical label evidence | **CORE REVIEW** |
| DS-SFV-001 | Same field of vision: brand + class/type + alcohol content | None | TTB requires these items in the same field of vision. A single submitted image can show that the three items were detected together, but the MVP cannot prove physical-container geometry or that the image captures one legally defined side. | REVIEW with machine evidence | Display whether all three were found in submitted image; do not claim legal PASS from image alone | OCR boxes / submitted image | **CORE REVIEW** |

## 6. Additional Deterministic Rule — Standards of Fill

TTB updated its distilled-spirits net-contents guidance on May 20, 2026 for new container sizes under T.D. TTB-200.

Current TTB guidance lists these authorized standards of fill:

3.75 L, 3 L, 2 L, 1.8 L, 1.75 L, 1.5 L, 1.00 L, 945 mL, 900 mL, 750 mL, 720 mL, 710 mL, 700 mL, 570 mL, 500 mL, 475 mL, 375 mL, 355 mL, 350 mL, 331 mL, 250 mL, 200 mL, 187 mL, 100 mL, and 50 mL.

Source:  
https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-net-contents

| Rule ID | Requirement | Automation class | Result behavior | MVP disposition |
|---|---|---|---|---|
| DS-NET-003 | Visible net contents corresponds to a currently authorized standard of fill | AUTOMATE using a versioned list reviewed 2026-09-23 | Listed size = PASS; clearly unlisted size = FAIL within supported scope; extraction uncertainty = REVIEW | **SECOND SLICE if time permits** |

This list must live in version-controlled configuration/rule data. The application must not scrape TTB live for each request.

## 7. Exact Health Warning Reference

Configured reference text:

> GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.

Source:  
https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning

Machine comparison policy:

- preserve required words, capitalization, punctuation, and numbering;
- tolerate OCR line breaks and repeated whitespace only;
- do not lowercase the entire warning before comparison;
- if punctuation/case is uncertain because OCR confidence is weak, use the bounded targeted warning-crop retry;
- conflicting/uncertain extraction after bounded rescue = REVIEW, not FAIL.

## 8. Conditional Requirements — Valid but Deferred from Core MVP

The May 2026 TTB checklist identifies the following requirements as conditional on product facts.

The MVP does not infer these triggering facts from label artwork.

| Rule ID | Conditional requirement | Trigger identified by TTB | Potential machine check if trigger is explicitly supplied | MVP disposition |
|---|---|---|---|---|
| DS-COND-SULFITE-001 | Sulfite declaration | Product has 10 ppm or more total sulfur dioxide | Search for required sulfite declaration once trigger is known | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-COLOR-001 | Presence of coloring materials disclosure | Certain coloring materials used | Validate configured disclosure once formula/product input identifies requirement | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-YELLOW5-001 | FD&C Yellow No. 5 disclosure | FD&C Yellow No. 5 used | Search for specific disclosure | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-CARMINE-001 | Cochineal extract / carmine disclosure | Cochineal extract and/or carmine used | Search for specific disclosure | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-WOOD-001 | Wood-treatment disclosure | Specified whisky/brandy treatment with wood outside ordinary oak-container contact, subject to TTB exception | Search for required disclosure after trigger is established | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-NEUTRAL-001 | Neutral-spirit percentage + commodity statement | Certain blended/rectified spirits use neutral spirits | Validate percentage/commodity statement after formulation context supplied | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-GIN-001 | Commodity statement for neutral spirits / continuously distilled gin | Product falls within specified neutral-spirit/gin condition | Validate commodity statement after product context supplied | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-STATE-001 | State of distillation | Certain U.S. whiskies where distillation state differs from state in label address | Validate state statement after production/address facts supplied | CONDITIONAL / OUT OF CORE MVP |
| DS-COND-AGE-001 | Age statement | Includes whisky aged under four years; specified grape brandies aged under two years; certain age representations; distillation date | Validate presence/format after age/product facts supplied | CONDITIONAL / OUT OF CORE MVP |

Primary source: TTB Mandatory Label Information Checklist.  
Supporting age guidance: https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/distilled-spirits-faqs

These rules are documented now so the architecture can expand later without redesigning the result model.

## 9. Requirements Intentionally Routed to Human Review

The following are valid labeling concerns but are not safely determined from ordinary OCR text alone:

- whether a brand name is misleading;
- whether a class/type designation is legally correct under all standards of identity;
- whether a formula-required statement of composition exactly corresponds to an approved formula when no formula record is supplied;
- physical type size in millimeters;
- true characters-per-inch measurement;
- reliable font-weight determination;
- physical container “same field of vision” geometry;
- true contrast/legibility under ordinary conditions;
- basic-permit identity verification;
- full CBP country-of-origin compliance;
- physical net-contents embossing/molding when it is not visible in submitted artwork;
- broader misleading graphics/optional-claim review.

The UI should explain which evidence was detected and why human review remains necessary.

## 10. First Vertical Slice — LOCKED

The requirements gate is now sufficient to begin implementation.

### User inputs

For the first runnable slice:

- Brand name
- Class/type or designation
- Alcohol content (% by volume)
- Net contents
- Bottler / producer / importer name
- Address
- Imported? Yes / No
- Country of origin when Imported = Yes
- One JPG/PNG label image

### Machine path

```text
Streamlit form + image
        ↓
decode / basic image checks
        ↓
one local OCR pass
        ↓
normalize OCR evidence
        ↓
extract/search:
  brand
  class/type
  ABV
  net contents
  name/address
  country if applicable
  health warning
        ↓
deterministic application consistency
        +
limited TTB textual rules
        ↓
PASS / REVIEW / FAIL
        ↓
field-by-field reasons + timing
```

### First-slice rules

Implement first:

- DS-BRAND-001
- DS-CLASS-001
- DS-ABV-001
- DS-ABV-002
- DS-NET-001
- DS-NET-002
- DS-NAME-001
- DS-IMPORT-001
- DS-WARN-001

Surface as REVIEW evidence rather than automated legal PASS:

- DS-WARN-002
- DS-WARN-003
- DS-WARN-004
- DS-SFV-001

Do not implement the conditional disclosure family until the working core remains stable and the schedule permits.

## 11. Test Cases Required With the First Slice

At minimum:

1. **Happy path** — all supplied fields match and warning textual content is correct.
2. **Dave normalization case** — application `Stone's Throw`, label `STONE'S THROW` => application brand consistency PASS.
3. **ABV mismatch** — application 45%, label 46% => FAIL.
4. **Warning heading case defect** — `Government Warning:` => FAIL when OCR evidence is reliable.
5. **Net contents absent from submitted image** => REVIEW, not automatic FAIL.
6. **Imported product missing country evidence** => REVIEW unless reliable evidence establishes a clear contradictory country.
7. **Unreadable/low-confidence critical field** => REVIEW after bounded local retry when that retry is implemented.
8. **Conflicting OCR evidence** => REVIEW; never majority-vote compliance.

## 12. Implementation Boundary

This matrix authorizes implementation of the first vertical slice.

It does **not** authorize:

- claiming complete TTB compliance;
- implementing wine/malt-beverage rules;
- treating the uploaded image as proof of physical container geometry;
- inferring product formulation facts not supplied by the user;
- silently expanding conditional rules;
- allowing Gemini to make PASS/FAIL decisions.

Any material expansion should follow the repository change-control protocol.
