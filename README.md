# IRCCF — Integrated Regulatory Compliance and Cybersecurity Ontology

**Research reproducibility repository — preliminary regulatory mappings.**

Companion materials for *A Unified Ontological Framework for Integrated Regulatory Compliance and Cybersecurity Requirements in Critical Infrastructure* (IEEE Access manuscript under revision).

## Research baseline and scope

- Pinned source: MITRE ATT&CK for ICS **v19.2** (historical release, not necessarily the most recent version).
- Canonical experimental graph: [`ontology/releases/irccf_stage5_3_PRELIMINARY_all47_active.ttl`](ontology/releases/irccf_stage5_3_PRELIMINARY_all47_active.ttl), **9,420 asserted RDF triples**.
- Source inventory: **12 ICS tactics, 79 unique parent techniques, 18 sub-techniques, 52 mitigations, 402 mitigation-to-technique links**.
- NIST CSF 2.0 Function associations are calculated through source-referenced mitigation/NIST SP 800-53 controls and an SP 800-53-to-CSF 2.0 crosswalk using a **25% parent-technique coverage threshold**; 32 tactic-to-Function associations were reported. The crosswalk file is labelled *draft*; see provenance notes.
- **47 author-proposed regulatory-to-technical-control mappings** are activated for exploratory analysis. These are not legally validated and should not be treated as authoritative compliance determinations.
- The reported **1,319 distinct SPARQL evidence paths** are graph-query results, not distinct legal duties or evidence that an operator complies with legislation.

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
