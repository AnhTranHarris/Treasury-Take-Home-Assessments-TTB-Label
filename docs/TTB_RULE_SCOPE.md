# TTB Rule Scope — Distilled Spirits MVP

**Status:** DESIGN BASELINE  
**Scope:** Machine-verifiable portions of the take-home prototype.  
**Authority:** Current TTB distilled-spirits labeling guidance and the Treasury take-home assignment.

## 1. Scope Decision

The MVP will implement **distilled spirits** first because the take-home sample is a distilled-spirits label and TTB rules differ among distilled spirits, wine, and malt beverages.

The internal policy layer should be modular so later rule packs can be added for wine or malt beverages without changing the OCR pipeline.

## 2. Two Different Validation Jobs

The system performs two distinct kinds of checks.

### A. Application consistency

Compare detected label evidence against the reference/application fields provided to the prototype.

Examples:

- brand name;
- class/type;
- alcohol content;
- net contents;
- name/address;
- country of origin when applicable.

### B. Limited TTB rule validation

Check only rules that are explicitly implemented and machine-verifiable from the provided image/evidence.

Examples:

- presence of required common information within supported scope;
- exact government-warning wording where OCR evidence is sufficiently reliable;
- capitalization of `GOVERNMENT WARNING`;
- alcohol-content formatting rules implemented from TTB guidance;
- supported same-image evidence checks.

The MVP is not a complete legal-compliance engine.

## 3. Same Field of Vision

TTB currently requires brand name, alcohol content, and class/type designation to appear in the same field of vision for distilled spirits.

The prototype may report:

> Brand, class/type, and alcohol content were all detected in the submitted image.

It must not overstate this as proof that the physical bottle satisfies the full regulatory definition of "same field of vision" unless the submitted evidence is sufficient to establish that fact.

## 4. Brand Name

Brand comparison may use normalization/RapidFuzz for harmless presentation differences.

Example:

```text
Application: Stone's Throw
Label:       STONE'S THROW
```

may be treated as a match after normalization.

The MVP does not attempt to decide whether a brand name is misleading as to age, origin, identity, or other characteristics. That requires regulatory judgment and should remain REVIEW / unsupported.

## 5. Class / Type

Compare the detected class/type designation to the reference/application value.

Do not attempt to independently classify every distilled-spirit standard of identity in the MVP.

If the submitted product needs a statement of composition or other specialized designation beyond the implemented rule set, route to REVIEW / unsupported.

## 6. Alcohol Content

Distilled spirits require an alcohol-content statement expressed as percent alcohol by volume.

The MVP should:

- extract a numeric alcohol percentage;
- compare that numeric value to the application/reference value;
- distinguish optional proof from mandatory percent alcohol by volume;
- validate only supported formatting rules.

A numerically different value is a material mismatch even if the text strings are highly similar.

Do not use fuzzy text similarity to decide ABV equality.

## 7. Net Contents

Extract quantity and unit.

Normalize permitted spelling/case variants for comparison where appropriate.

Compare the normalized quantity to the application/reference value.

Do not silently infer an unreadable volume.

Current TTB standards-of-fill guidance changes over time; if the project later validates authorized container sizes, those values must live in a versioned rule data file with source/effective-date metadata rather than scattered hard-coded literals.

## 8. Name and Address

Check for the expected bottler/distiller/processor/importer name and address data supplied in the application/reference fields.

The MVP should not attempt to validate a federal permit database.

If an imported distilled spirit is used in a test case, import-related wording and address checks should be limited to explicitly implemented rules.

## 9. Country of Origin

Country of origin is relevant to imported distilled spirits.

The UI/reference data should include an import indicator so the rule engine knows whether this field is expected.

Do not require a country-of-origin result for a domestic sample merely because the generic assignment lists country of origin among common elements.

## 10. Government Health Warning

TTB requires the prescribed health warning for covered alcoholic beverages.

Supported automated checks should include, when OCR confidence is adequate:

- warning text present;
- wording matches the prescribed text after only explicitly allowed OCR/whitespace normalization;
- punctuation matches where reliably extracted;
- `GOVERNMENT WARNING` appears in capital letters.

The visual evidence panel should show the warning crop.

### Manual / REVIEW items for the MVP

Do not automatically certify these unless separately proven by testing:

- boldness;
- exact physical type size in millimeters;
- characters per inch;
- full contrasting-background determination;
- physical placement beyond what the submitted image actually shows.

## 11. Result Semantics

### PASS

All implemented checks within the supported scope pass and evidence is sufficiently reliable.

### REVIEW

Examples:

- unreadable or low-confidence evidence;
- local OCR / Gemini conflict;
- visual typography requirement not automatically verifiable;
- rule outside implemented scope;
- ambiguous regulatory judgment.

### FAIL

Use only for clear, deterministic failures inside implemented scope, such as:

- high-confidence material ABV mismatch;
- required supported field clearly absent;
- high-confidence warning wording/capitalization failure.

## 12. Rule-Pack Structure

Rules should be centralized and versioned.

Suggested structure:

```text
rules/
└── distilled_spirits/
    ├── rule_metadata.json
    ├── warning.py
    ├── alcohol_content.py
    ├── net_contents.py
    ├── brand.py
    ├── class_type.py
    ├── name_address.py
    └── country_origin.py
```

Each rule should expose:

- stable rule ID;
- description;
- source URL/reference;
- source last-reviewed date when recorded;
- implementation status;
- PASS / REVIEW / FAIL behavior;
- automated-test cases.

## 13. Official Source Pages Used for This Design

- TTB Distilled Spirits Labeling:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling
- Mandatory Label Information:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label
- Brand Name:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-name
- Alcohol Content:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-alcohol-content
- Net Contents:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-net-contents
- Name and Address:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-name-address
- Health Warning:
  https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning

## 14. No Live TTB Scraping in the Request Path

Do not fetch TTB.gov during each label review.

Reasons:

- adds network latency;
- creates an unnecessary external dependency;
- makes results depend on website availability;
- can introduce unreviewed rule changes at runtime.

Instead, implement a small, reviewed, versioned rule pack derived from official guidance and cite the source inside the repository.

Updates to regulatory rules should be deliberate code/rule-data changes with tests.
