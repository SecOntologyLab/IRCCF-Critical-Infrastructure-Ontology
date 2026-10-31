#                                                      IRCCF 
#                             Regulatory-to-Control Correspondences: Expert Review Register

## Purpose and status

This directory provides a structured review register for **47 author-proposed correspondences** between selected provisions of four European Union legislative instruments and cybersecurity controls referenced by the IRCCF (Integrated Regulatory Compliance and Cybersecurity Framework) ontology.

The register is made available so that readers, reviewers, and domain specialists can inspect the proposed interpretations, understand the unresolved issues and, where appropriate, submit reasoned assessments or corrections. **The 47 correspondences have not yet received documented independent legal approval.** Their presence in the research ontology supports exploratory computational traceability; it does **not yet** demonstrate legal equivalence, regulatory compliance, or expert endorsement.

The related IEEE Access research manuscript examines ontology-based relationships among regulatory requirements, cybersecurity controls, MITRE ATT&CK for ICS, and NIST Cybersecurity Framework (CSF) 2.0 Functions. This register provides transparency about the *legal interpretation layer* of those relationships; it is not a substitute for legal advice or a compliance assessment.

## Review workbook

**File:** [`IRCCF_Legal_Expert_Review_47_Mappings.xlsx`](IRCCF_Legal_Expert_Review_47_Mappings.xlsx)

The workbook retains **47 uniquely identified records (P53-001–P53-047)** and contains four worksheets:

| Worksheet | Contents and intended use |
|---|---|
| **START HERE** | Workbook overview, source provenance, and a brief review workflow. |
| **Legal Review** | The complete 47-row register, including provision, candidate control, prior desk assessment, legal source, and blank fields for expert decisions. **This is the primary review sheet.** |
| **Supplement Draft** | A publication-oriented table that can be populated **only after** approved decisions are obtained. Blank review fields are not endorsements. |
| **Review priorities** | Summary of preliminary classifications and suggested order of review. |

The current register spans **NIS2 (20 records), GDPR (9), Cyber Resilience Act (12), and EU AI Act (6)**. Counts refer to proposed mapping *rows*, not to numbers of legally distinct duties.

## What a reviewer is being asked to assess

For each candidate mapping, the reviewer should:

1. **Verify the legal provision** against the official legislative text, identifying the exact article, paragraph, or annex point.
2. **Confirm the scope and applicability** of the obligation, including relevant addressees, conditions, and qualifications.
3. **Assess the proposed correspondence:** does the identified technical control credibly contribute to addressing the specified legal obligation, or does the association overstate its scope? A technical safeguard should not be described as satisfying an entire legislative requirement merely because it addresses one component.
4. **Record a decision:** accept as a partial correspondence; accept with narrowing; revise/split; replace the control; reject; or defer pending further evidence.
5. **Supply the reasoning and citation:** provide a concise legal rationale, a precise authoritative reference, and any material reservations. Sign off only on interpretations actually examined and accepted.

Reviewers need **not** run Stardog, execute SPARQL, modify RDF/Turtle files, or independently validate every MITRE–NIST technical chain. Technical sufficiency and any resulting ontology changes are assessed separately.

### Decision vocabulary

| Decision | Meaning |
|---|---|
| **ACCEPT AS PARTIAL** | The control is a defensible *contributing* measure, not full legal equivalence or proof of compliance. |
| **ACCEPT WITH NARROWING** | The relationship is supportable only for a more precisely defined part of the cited obligation. |
| **REVISE / SPLIT** | The original citation combines distinct obligations; they should be separated and evaluated individually. |
| **REPLACE CONTROL** | The nominated control is not a sufficiently relevant correspondence; a technically appropriate alternative requires separate assessment. |
| **REJECT** | The proposed legal premise, scope, or applicability cannot be supported. |
| **DEFER / NEEDS EVIDENCE** | A decision requires additional authoritative material or specialist examination. |

### Preliminary review priorities

The existing desk review classified the 47 entries as **23 PLAUSIBLE—unchanged, 13 NARROW, 6 SPLIT, and 5 REPLACE**. These are triage recommendations, **not legal decisions**. The suggested order is to review SPLIT and REPLACE cases first, followed by NARROW and then PLAUSIBLE; **all 47 require an actual expert decision**.

### Illustrative example: P53-004

- **Proposed legal obligation:** NIS2 Article 21(2)(a), on policies for risk analysis and information system security.
- **Original candidate:** NIST SP 800-53 Rev. 5 **SI-4 (System Monitoring)**.
- **Prior desk-review concern:** Monitoring is not equivalent to establishing risk-analysis and information-security policies; the row is provisionally marked **REPLACE**.
- **Question for a legal reviewer:** Does the interpretation accurately describe the obligation, and what narrower contribution, if any, can system monitoring make to it?
- **Technical follow-up:** Potential alternatives, such as risk assessment or security-planning controls, must be examined by a technical expert; they are **not pre-approved replacements**.

This example illustrates a review task; it is **not a completed expert assessment**.

## How to record or propose changes

In the **Legal Review** worksheet, retain the supplied mapping IDs and original source columns. Enter findings in the designated reviewer fields, notably **Legal reviewer**, **Review date**, **Legal decision**, **Exact verified article / point**, **Revised legal interpretation / scope**, **Legal rationale**, **Official source / supporting citation**, **Applicability / obligations caveat**, and **Legal sign-off (Yes/No)**. Record any suggested technical-control change separately rather than silently replacing the original control.

An external reader wishing to contribute can use a separate copy of the workbook, or provide a structured comment quoting the mapping ID and proposed correction. **Submitting a suggestion does not constitute approval or automatic incorporation into the ontology.** If the repository permits Issues or pull requests, those may be used for non-confidential feedback; otherwise, contact the corresponding author through the published paper's contact details.

Avoid entering personal contact information or confidential legal advice into materials intended for public distribution.

## Relationship to the ontology and manuscript

The exploratory ontology contains the 47 author-proposed mapping relationships as active graph assertions for its computational analysis. An earlier desk-review register used the label **“NOT AUTHORISED FOR ACTIVE TRIPLE”** to indicate lack of legal/technical sign-off *before* exploratory activation. That historical label should **not** be read as describing the current technical state of the ontology. Conversely, technical activation is **not** legal approval.

The original mapping IDs are retained as traceability keys. Any expert-approved narrowing, split, replacement, or rejection should be recorded with its rationale and mapped to the corresponding technical action. New records created by a split should have new identifiers linked to the original record. The **Supplement Draft** worksheet is intended to facilitate a concise, evidence-backed supplementary table in the IEEE Access paper once decisions have been validated.

Approved changes made after the verified computational baseline should be implemented in a **separately versioned ontology** and accompanied by rerun traceability results when the changes affect graph relationships. They must not be retroactively presented as part of the already reported **1,320 distinct evidence paths**.

## Important boundary: GDPR Article 22 and AI Act Article 14

The 47-row register covers proposed **regulatory-to-technical-control** correspondences. It does **not** include the separate ontological/SHACL demonstration distinguishing **GDPR Article 22** (certain solely automated individual decisions) from **EU AI Act Article 14** (human oversight obligations for high-risk AI systems). Those legal interpretations warrant their own review and should not be presumed approved by completion of this workbook. Nor should those distinct provisions be treated as legally equivalent.

## Official legislative sources

- **NIS2:** [Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj/eng)
- **GDPR:** [Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng)
- **Cyber Resilience Act:** [Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng)
- **EU AI Act:** [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng)

The corresponding technical-control definitions should be checked against the applicable NIST SP 800-53 Rev. 5 or IEC 62443 edition. This repository does not purport to reproduce proprietary IEC normative text.

## Provenance and limitations

- Source decision register: `data/regulatory/Stage_5_3_Refined_Decisions.csv` in the main repository.
- Review workbook prepared from 47 author-derived candidate correspondences and their preliminary desk-review rationale.
- The candidate register is **research material awaiting independent legal and technical validation**, not an authoritative mapping standard.
- This directory and its review workbook do not certify that any entity, product, system, or organisation complies with the cited legislation.
- Results of any subsequent expert review should be recorded transparently, with the reviewing authority, decision date, and affected mapping identifiers.
