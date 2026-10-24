# Pre-push checklist

## Add from the Windows laptop
- [ ] `IRCCF_Scalability_Benchmark/results_3runs/` summaries (`runs.csv`, `summary.csv`, `methods.json`) to `results/reasoning/scalability/`.
- [ ] `IRCCF_Reasoning_Benchmark/results_3runs/` to `results/reasoning/baseline/`.
- [ ] `SHACL_Python_VSCode/reports/` full pySHACL reports to `results/shacl/`.
- [ ] Canonical 4-scenario validation metadata (Python/rdflib/pySHACL versions, OS, date, outcome).
- [ ] Versioned script(s) that generated Stage 5.1–5.3 regulatory additions, if saved locally.
- [ ] SPARQL COUNT query establishing 1,319 paths and evidence aggregation query used to generate Table III.
- [ ] Exact source URLs, release dates, hashes and licence/attribution statements for MITRE and NIST.
- [ ] Clarify whether original ontology in SHACL package is identical to the manuscript baseline.
- [ ] Check scripts run from documented working directory; pin dependencies in requirements.txt.
- [ ] Verify that every Figure/Table in manuscript can be traced to a script/query/data/result.
- [ ] Keep manuscript drafts, peer review communications, the licensed IEC standard, copyrighted paper PDFs and personal correspondence private.
- [ ] Add contributor/author permission and explicit licence before opening public repository.

## Proposed Git workflow
1. Unzip and open the folder in VS Code.
2. Inspect contents; move sensitive, copyrighted or unlicensed material outside the Git working tree.
3. Add missing benchmark results and document source provenance.
4. `git init`; `git add .`; `git status`; inspect staged files; `git commit -m "Initial reproducibility materials"`.
5. Create an empty GitHub repository (prefer **private** until review complete).
6. `git branch -M main`; `git remote add origin <GITHUB_URL>`; `git push -u origin main`.
