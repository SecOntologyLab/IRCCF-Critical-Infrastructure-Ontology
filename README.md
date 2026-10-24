# IRCCF — Integrated Regulatory Compliance and Cybersecurity Ontology

**Research reproducibility repository — preliminary regulatory mappings.**

Companion materials for *A Unified Ontological Framework for Integrated Regulatory Compliance and Cybersecurity Requirements in Critical Infrastructure* (IEEE Access manuscript under revision).

## Research baseline and scope

- **Pinned source:** MITRE ATT&CK for ICS v19.2 (historical release, not necessarily the most recent version).

- **Source inventory:** 12 ICS tactics, 79 unique parent techniques, 18 sub-techniques, 52 mitigations, and 402 mitigation-to-technique links.

- **Original experimental baseline (Stage 5.3):** `ontology/releases/irccf_stage5_3_PRELIMINARY_all47_active.ttl`, containing 9,420 asserted RDF triples, 32 calculated tactic-to-NIST CSF 2.0 Function associations, and 1,319 distinct regulatory evidence paths.

- **Corrected traceability release (Stage 5.4):** `ontology/releases/irccf_stage5_4_PRELIMINARY_all47_active.ttl`, containing 9,421 asserted RDF triples, 33 calculated tactic-to-Function associations, and 1,320 distinct regulatory evidence paths.

- **Tactic-to-Function calculation:** NIST CSF 2.0 Function associations are derived through source-referenced MITRE mitigation relationships, NIST SP 800-53 Rev. 5 controls, and an SP 800-53-to-CSF 2.0 crosswalk. A Function association is established when at least 25% of the relevant parent techniques satisfy the coverage criterion. The crosswalk file is identified as a draft and is retained for research provenance; its mappings should not be interpreted as independently validated normative relationships.

- **Stage 5.4 correction:** A targeted audit identified one previously omitted qualifying association between MITRE ICS Discovery (`TA0102`) and the NIST CSF 2.0 Detect (`DE`) Function. Two of the eight relevant parent techniques satisfied the criterion, meeting the 25% threshold. Adding this association increased the number of calculated tactic-to-Function associations from 32 to 33 and the distinct regulatory evidence paths from 1,319 to 1,320. No additional regulatory mapping or source mitigation relationship was introduced. The correction is documented in `docs/provenance/Stage5_4_Change_Record.md`.

- **Experimental scope:** The recorded SHACL, RDFS/OWL 2 RL reasoning, and synthetic scalability experiments were performed using the original Stage 5.3 experimental baseline or its documented SHACL-specific inputs. Their reported results have been preserved unchanged. The corrected Stage 5.4 ontology is provided for regulatory traceability analysis and has not been independently subjected to the complete benchmark suite reported for Stage 5.3.

- **Regulatory mappings:** The framework activates 47 author-proposed regulatory-to-technical-control mappings for exploratory analysis. These mappings are preliminary and have not been independently validated as authoritative legal interpretations.

- **Interpretation of traceability results:** The 1,319 evidence paths associated with Stage 5.3 and the 1,320 paths associated with Stage 5.4 represent distinct SPARQL graph-query results. They are not counts of distinct legal obligations, independently verified compliance requirements, or evidence that an infrastructure operator complies with applicable legislation.
  
## Repository structure

| Path | Purpose |
| --- | --- |
| `ontology/releases/` | Canonical experimental ontology |
| `ontology/history/` | Earlier ontology snapshots; not interchangeable with the release graph |
| `data/mitre/`, `data/nist/`, `data/regulatory/`, `data/audits/` | Versioned source data, crosswalk and source/mapping audits |
| `scripts/build/` | Data extraction and mapping builders; full end-to-end execution order not yet independently verified |
| `scripts/shacl/` | SHACL validation script, shapes and **specific historical test inputs** in `inputs/` |
| `scripts/reasoning/` | RDFS and OWL 2 RL benchmarking scripts |
| `queries/` | SPARQL traceability and diagnostic queries |
| `results/` | Original curated experimental outputs |
| `results/verification/` | Independent reruns from the assembled repository; do not overwrite the originals |
| `docs/provenance/` | Assembly checklist and manifest; refresh file hashes after final repository assembly |

## Local environment

Tested locally using Python 3.12 on Windows. From the **repository root** in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Dependencies are listed in `requirements.txt`. They are currently **not version-pinned**. To strengthen exact environment reproducibility, record the package versions used for the release in a separate lock or environment record.

## Reproduce the computational experiments

The scripts below are configured for this repository hierarchy. Keep the canonical ontology and SHACL experimental input files in their documented locations.

**1. SHACL scenario checks** (689-triple original input, 9,420-triple revised input, 13 SHACL shape triples):

```powershell
.\.venv\Scripts\python.exe scripts\shacl\validate_shacl.py
```

Expected scenario outcomes: `VIOLATION`, `PASS`, `VIOLATION`, `VIOLATION`. These rules detect **two specifically defined semantic modelling errors**, not general legal conflicts.

**2. RDFS and OWL 2 RL reasoning**, three repetitions per profile:

```powershell
.\.venv\Scripts\python.exe scripts\reasoning\benchmark.py --runs 3
```

Expected inferred counts: **3,601** (RDFS) and **4,909** (OWL 2 RL). Execution times and memory consumption depend on the machine and environment.

**3. Synthetic ABox scalability**, graph sizes 1×, 2×, 5× and 10×, three repetitions per profile (24 runs):

```powershell
.\.venv\Scripts\python.exe scripts\reasoning\scale_benchmark.py --runs 3
```

| Scale | Asserted triples | RDFS newly inferred | OWL 2 RL newly inferred |
| --- | ---: | ---: | ---: |
| 1× | 9,420 | 3,601 | 4,909 |
| 2× | 18,711 | 4,856 | 7,059 |
| 5× | 46,584 | 8,621 | 13,509 |
| 10× | 93,039 | 14,896 | 24,259 |

The graph-size expansion is **synthetic** and does not represent a deployed SOC, real-world incident workload, unrestricted OWL DL reasoning or tested SPARQL scalability.

The scripts write new outputs beneath `results/verification/`, retaining the recorded experiment outputs separately in `results/shacl/`, `results/reasoning/` and `results/scalability/`.

## Traceability results and outstanding verification

The repository includes recorded candidate/active SPARQL queries and CSVs for tactic/CSF coverage and EU regulatory traceability, including the 1,319-path result. **Independent re-execution of the recorded Stardog traceability and coverage queries has not yet been performed as part of this repository assembly.** Source data, graph imports and query execution requirements must be documented before claiming full end-to-end reconstruction of those results.

## Provenance, interpretation and redistribution

- Check the MITRE and NIST datasets' licence terms, attribution requirements and the redistribution suitability of the NIST draft crosswalk before public release.
- Do not upload proprietary IEC 62443 normative text, journal PDFs, private correspondence, confidential partner material or personal data without authorisation.
- The 20 source-observed IEC 62443-3-3 SR identifiers do **not** constitute validation against the complete normative IEC catalogue.
- GDPR Article 22 and EU AI Act Article 14 are distinct provisions with different legal scopes. The demonstration's SHACL rules detect selected incorrectly modelled relationships only.
- The source inventory and stored file manifest should be checked and regenerated after all edits. The repository is not yet an independently audited complete archive of every development step.

## GitHub release status

Prepare the first commit as a **private** repository under `SecOntologyLab`. Review licensing, provenance and final output data before changing repository visibility.
