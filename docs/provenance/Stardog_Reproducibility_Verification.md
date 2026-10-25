# Stardog Reproducibility Verification

## Purpose

This document records the independent verification of the IRCCF Stage 5.3 and Stage 5.4 ontology releases using Stardog Cloud Free.

The purpose of the verification was to establish whether the principal numerical results of the IRCCF research could be reproduced from the archived RDF/Turtle ontology files using newly created Stardog databases.

The verification was conducted on 25 October 2026.

## 1. Stardog verification environment

- **Verification date:** 25 October 2026
- **Platform:** Stardog Cloud Free (web-based service)
- **Interface:** Stardog Studio
- **Server version:** Not disclosed through the Stardog Free interface
- **Reasoner:** OFF
- **Query display limit:** Manually increased from the default of 1,000 to 1,500 through Stardog Studio Preferences (`Ctrl + ,`). This setting permitted inspection of all 1,319 and 1,320 regulatory evidence paths. It is a configurable Studio interface setting, not an inherent Stardog query-processing limit.
- **Verification method:** SPARQL queries executed against freshly created databases populated separately from the archived ontology releases.

Each database was queried independently. No additional RDF datasets were intentionally imported into the verification databases.

## 2. Ontology files

### Stage 5.3 — Original experimental baseline

File:

`ontology/releases/irccf_stage5_3_PRELIMINARY_all47_active.ttl`

Expected properties:

- 9,420 asserted RDF triples
- 32 calculated tactic-to-CSF Function associations
- 1,319 distinct regulatory evidence paths

### Stage 5.4 — Corrected traceability release

File:

`ontology/releases/irccf_stage5_4_PRELIMINARY_all47_active.ttl`

Expected properties:

- 9,421 asserted RDF triples
- 33 calculated tactic-to-CSF Function associations
- 1,320 distinct regulatory evidence paths

Stage 5.4 incorporates one additional qualifying Discovery-to-Detect Function association. The change is documented in:

`docs/provenance/Stage5_4_Change_Record.md`

## 3. Verification procedure

Two freshly created Stardog databases were populated separately from the Stage 5.3 and Stage 5.4 ontology files.

For each database:

1. Import the corresponding RDF/Turtle ontology file.
2. Select that database in Stardog Studio.
3. Set the Reasoner option to OFF.
4. Set the Studio query display limit to 1,500 through Preferences.
5. Execute the three SPARQL verification queries below.
6. Record the results and compare them against the expected values.

## 4. SPARQL verification queries

### Query 1 — Asserted RDF triple count

Purpose: Determine the number of asserted RDF triples available in the selected database with reasoning disabled.

```sparql
SELECT (COUNT(*) AS ?tripleCount)
WHERE {
    ?s ?p ?o .
}
```

Expected results:

- Stage 5.3: 9,420
- Stage 5.4: 9,421

### Query 2 — Tactic-to-CSF Function association count

Purpose: Count explicitly represented tactic-to-NIST CSF 2.0 Function associations.

```sparql
PREFIX irccf: <https://purl.org/ircc-framework#>

SELECT (COUNT(*) AS ?associationCount)
WHERE {
    ?tactic irccf:calculatedFunctionAssociation ?function .
}
```

Expected results:

- Stage 5.3: 32
- Stage 5.4: 33

### Query 3 — Distinct regulatory evidence paths

Purpose: Retrieve the eight-column regulatory traceability results linking regulations, requirements, author-proposed mappings, technical controls, MITRE mitigations, techniques, tactics, and NIST CSF 2.0 Functions.

```sparql
PREFIX irccf: <https://purl.org/ircc-framework#>

SELECT DISTINCT
    ?regulation ?requirement ?mapping ?control
    ?mitigation ?technique ?tactic ?function
WHERE {
    ?regulation irccf:imposesRequirement ?requirement .

    ?mapping a irccf:ProposedRegulatoryControlMapping ;
             irccf:proposedRequirement ?requirement ;
             irccf:proposedControl ?control .

    ?requirement irccf:implementedBy ?control .

    ?mitigation irccf:referencesStandardsControl ?control ;
                irccf:mitigatesTechnique ?technique .

    ?technique irccf:belongsToTactic ?tactic .

    ?tactic irccf:calculatedFunctionAssociation ?function .

    FILTER NOT EXISTS {
        ?technique a irccf:SubTechnique
    }

    FILTER EXISTS {
        ?control irccf:hasCSFSubcategory ?subcategory .
        ?subcategory irccf:inCSFFunction ?function .
    }
}
ORDER BY
    ?regulation ?requirement ?mapping ?control
    ?mitigation ?technique ?tactic ?function
```

The number of distinct returned rows was recorded for each release.

Expected results:

- Stage 5.3: 1,319 distinct evidence paths
- Stage 5.4: 1,320 distinct evidence paths

The query uses `SELECT DISTINCT` to avoid counting duplicate eight-column solution rows.

The Stardog Studio query display limit was set to 1,500, allowing the complete result sets to be displayed without adding a `LIMIT` clause to the SPARQL query.

## 5. Verification results

The following results were obtained on 25 October 2026.

| Verification measure | Stage 5.3 expected | Stage 5.3 observed | Stage 5.4 expected | Stage 5.4 observed |
|---|---:|---:|---:|---:|
| Asserted RDF triples | 9,420 | 9,420 | 9,421 | 9,421 |
| Tactic-to-CSF Function associations | 32 | 32 | 33 | 33 |
| Distinct regulatory evidence paths | 1,319 | 1,319 | 1,320 | 1,320 |
| Verification status | PASS | PASS | PASS | PASS |

All six numerical verification checks passed.

The results were reproduced from separately imported archived ontology files, rather than relying exclusively on the original development database.

## 6. Interpretation

The independent verification confirms that the archived ontology releases reproduce the principal aggregate SPARQL results recorded during the IRCCF research.

The Stage 5.4 correction produces:

- One additional asserted RDF triple.
- One additional calculated tactic-to-CSF Function association.
- One additional distinct regulatory evidence path.

These differences are consistent with the documented Discovery-to-Detect correction.

The verification does not establish that the underlying author-proposed regulatory mappings are legally authoritative or that the resulting evidence paths demonstrate operational regulatory compliance.

## 7. Scope and limitations

This verification establishes reproducibility of the six reported aggregate counts from the archived ontology files.

The following remain outside the scope of this specific verification:

1. Row-by-row comparison between freshly exported Stardog results and archived evidence-path CSV files.
2. Independent recalculation of all tactic-to-Function associations from the 25% parent-technique coverage criterion.
3. Complete reconstruction of the ontology from the original MITRE ATT&CK for ICS and NIST source datasets.
4. Independent legal validation of the 47 author-proposed regulatory mappings.
5. Re-execution of the separate Python-based SHACL, RDFS/OWL 2 RL reasoning, and synthetic scalability benchmarks as part of this Stardog verification.

The verification was conducted using Stardog Cloud Free, a managed service whose underlying server version was not disclosed through the user interface.

The verification date and relevant user-configurable settings have therefore been recorded to support methodological transparency.

## 8. Verification conclusion

On 25 October 2026, the original Stage 5.3 and corrected Stage 5.4 IRCCF ontology releases successfully passed independent count-level SPARQL verification in Stardog Cloud Free.

Both releases reproduced their expected asserted RDF triple counts, calculated tactic-to-CSF Function association counts, and distinct regulatory evidence-path counts.

These findings support the reproducibility of the archived ontology-based traceability results, subject to the limitations described above.
