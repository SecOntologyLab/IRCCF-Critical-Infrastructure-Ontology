# IRCCF pre-commit checklist

- [ ] Stage 5.3 TTL remains 9,420 triples; Stage 5.4 TTL remains 9,421 triples.
- [ ] Stage 5.4 contains Discovery → Detect, and Stage 5.3 does not.
- [ ] Stage 5.4 normalized evidence CSV contains 1,320 distinct eight-column evidence tuples.
- [ ] Revised Table III includes Discovery DE and PR, Discovery 13 paths, 12 tactics overall.
- [ ] Preserved Stage 5.3 results are not overwritten or relabelled.
- [ ] All updated Python scripts work with paths relative to repository root.
- [ ] Local paths, user names, secrets and collaborator-only data are absent from tracked files (including generated JSON and CSV metadata).
- [ ] Review source licence/redistribution requirements for MITRE and NIST data and any IEC or article content.
- [ ] Confirm no local-only or private files are staged: `git status --short` / `git diff --cached --name-only`.
- [ ] Run `py scripts/maintenance/refresh_manifest.py`; verify manifest paths and count.
- [ ] Record exact Python/library versions and testing environment for release-level reproducibility.
- [ ] Initially create the SecOntologyLab repository as private and confirm organisation write permission.
