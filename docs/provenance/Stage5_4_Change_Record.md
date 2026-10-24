# Stage 5.4 correction and evidence provenance

The Stage 5.3 baseline remains preserved: 9,420 asserted triples, 32 materialised tactic-to-CSF-Function associations, and 1,319 distinct regulatory-to-technical evidence paths.

Stage 5.4 adds one asserted triple to the canonical Stage 5.3 source: `irccf:TA0102_Discovery irccf:calculatedFunctionAssociation irccf:CSF2Function_DE .` The user's local RDFLib parse reported 9,421 triples.

The inclusion threshold is at least 25% of parent techniques in a tactic. Discovery has 8 parents; 2 have eligible mitigation-to-control-to-CSF Detect mappings, so 2/8 = 25%. A 72-combination Stardog audit found this to be the sole discrepancy between computed coverage and the stored associations.

The user's corrected working-copy Stardog database returned 1,320 distinct eight-variable traceability paths. The two supplied CSV datasets were independently compared here by stripping only the shared `https://purl.org/ircc-framework#` prefix from each of the eight fields: **1 added path, 0 removed paths, 0 duplicates**.

## The sole new path

- **regulation**: `NIS2`
- **requirement**: `NIS_Art__21_2_i`
- **mapping**: `P53_016`
- **control**: `Standards_8c2f91e7db9c2a5aae42`
- **mitigation**: `MITRE_M0926`
- **technique**: `T0842_NetworkSniffing`
- **tactic**: `TA0102_Discovery`
- **function**: `CSF2Function_DE`

This is an author-derived exploratory traceability link, not independently legally validated compliance evidence. The eight-column paths are distinct query solutions, not separate obligations or verified controls.

## Files and version boundaries

- Preserve the original `Stage5_Preliminary_Evidence_Paths.csv` and `Stage5_Preliminary_Merged_TableIII.csv` as Stage 5.3 historical results.
- Put `Stage5_4_Evidence_Paths_Normalized.csv` and `Stage5_4_Merged_TableIII.csv` in `results/traceability/`.
- Place this note in `docs/provenance/`.
- Preserve `ontology/releases/irccf_stage5_3_PRELIMINARY_all47_active.ttl`. The corrected release is `ontology/releases/irccf_stage5_4_PRELIMINARY_all47_active.ttl`.
- Prior SHACL, reasoning and scalability results were generated against Stage 5.3 and must remain labelled accordingly. Stage 5.4 computational rechecks are pending.
- Update the README's preferred current ontology and the 33/1,320 claims only after retaining the baseline documentation.
