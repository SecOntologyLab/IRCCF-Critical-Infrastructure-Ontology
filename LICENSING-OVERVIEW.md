# Licensing overview — IRCCF research repository

**Start here if you want to reuse, adapt, redistribute, or cite materials from this repository.** The IRCCF repository combines original research outputs, software, and materials from external sources. **There is no single license covering everything.** The terms applicable to a particular item depend on its source and copyright status.

## Which licensing file should I read?

| If you are interested in… | Read this file | Applicable terms |
| --- | --- | --- |
| Original IRCCF ontology contributions, author-developed regulatory correspondence analyses, experimental results, and research documentation | **[`LICENSE-RESEARCH-DATA.md`](LICENSE-RESEARCH-DATA.md)** | **Creative Commons Attribution 4.0 International (CC BY 4.0)**, only for material the relevant rights holders are authorised to license |
| Original IRCCF Python scripts and other eligible software or query code | **[`LICENSE-MIT-CODE.md`](LICENSE-MIT-CODE)** | **MIT License**, subject to confirmation of the actual copyright holder(s) |
| MITRE ATT&CK, NIST resources, IEC references, EU legislative material, and other externally sourced content | **[`LICENSE-THIRD-PARTY.md`](LICENSE-THIRD-PARTY.md)** | **Each source's applicable terms**; neither CC BY 4.0 nor MIT overrides them |

**For the complete CC BY 4.0 legal terms:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode). The [plain-language summary](https://creativecommons.org/licenses/by/4.0/) is also available. The full MIT License appears in `LICENSE-MIT-CODE.md`.

## Practical examples

- **Reusing an original IRCCF mapping table or explanatory diagram:** Consult `LICENSE-RESEARCH-DATA.md`; attribute the source, link to CC BY 4.0, identify any changes, and cite the version or commit used.
- **Adapting an original IRCCF Python script:** Consult `LICENSE-MIT-CODE.md` and retain the copyright and permission notices required by the MIT License.
- **Redistributing the MITRE ICS v19.2 source JSON, a NIST crosswalk, or text from a standard:** Check `LICENSE-THIRD-PARTY.md` and the source's own conditions first. Presence in the repository does **not** mean that third-party material is available under the IRCCF licenses.
- **Working with a file that mixes author-generated content and imported data:** The IRCCF license, where valid, covers only the eligible original contribution. The imported components retain their own legal status or permissions.

## Status of the regulatory correspondences

The **47 author-proposed regulatory-to-control correspondences** are available for research scrutiny and independent expert review. They are **preliminary interpretations**, not certified statements of legal equivalence, compliance, or legal correctness. Their use in exploratory ontology queries and their publication in this repository do not constitute expert legal approval. Review materials are under [`docs/legal-review/`](docs/legal-review/).

## Copyright ownership and publication status

The licensing statements for original contributions apply **only where the relevant authors, institutions, or other rights holders have the authority to grant the specified permissions**. Confirm the copyright-holder attribution in `LICENSE-MIT-CODE.md` before public release. Any required third-party attribution and redistribution notices must also be preserved.

The **IEEE Access article's publication license** is a separate matter: it does not automatically license all repository data or software, and these repository licenses do not supersede the journal's publication agreement.

For research provenance, identify the relevant Git commit or release when citing or reusing material. Questions or suspected licensing ambiguities can be raised with the repository maintainers; GitHub Issues may be used where enabled.

---

**Repository:** https://github.com/SecOntologyLab/IRCCF-Critical-Infrastructure-Ontology

**Note to maintainers:** This overview assumes the three filenames shown above. Update internal links in the renamed licensing files and add a link to this page from the main `README.md` before publication.
