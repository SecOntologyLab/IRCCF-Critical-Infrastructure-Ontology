"""Run the four GDPR Art 22 / AI Act Art 14 SHACL demonstrator scenarios.

Install: python -m pip install rdflib pyshacl
Run:     python validate_shacl.py
All paths are relative to this script; writes reports/ and results.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

from rdflib import Graph, Namespace, OWL
from pyshacl import validate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = HERE / 'inputs'
IRCCF = Namespace("https://purl.org/ircc-framework#")
OUT = ROOT / "results" / "verification" / "shacl"
OUT.mkdir(exist_ok=True)

def load_graph(filename: str) -> Graph:
    graph = Graph()
    path = (HERE if filename == "validation_shapes.ttl" else INPUTS) / filename
    graph.parse(path.as_uri(), format="turtle")
    return graph

def run_case(name: str, data_graph: Graph, shapes: Graph) -> dict:
    conforms, report_graph, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes,
        inference="none",  # Check asserted triples, not owl:sameAs closure
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        advanced=False,
        meta_shacl=False,
    )
    (OUT / f"{name}.txt").write_text(str(report_text), encoding="utf-8")
    if isinstance(report_graph, Graph):
        report_graph.serialize(destination=str(OUT / f"{name}.ttl"), format="turtle")
    print(f"{name}: {'PASS' if conforms else 'VIOLATION'}")
    print(str(report_text)[:1200])
    print()
    return {"scenario": name, "conforms": bool(conforms), "triple_count": len(data_graph)}


def main() -> None:
    shapes = load_graph("validation_shapes.ttl")
    original = load_graph("original_ontology.ttl")
    revised = load_graph("revised_ontology.ttl")
    print(f"Loaded {len(original)} original triples, {len(revised)} revised triples, {len(shapes)} shape triples.\n")

    outcomes = [
        run_case("01_original_shared_oversight", original, shapes),
        run_case("02_revised_separate_articles", revised, shapes),
    ]

    # Deliberately wrong claim, GDPR Article 22 -> AI Act Article 14
    wrong_forward = revised + Graph()
    wrong_forward.add((IRCCF.GDPR_Art__22_1, OWL.sameAs, IRCCF.AIAct_Art__14_1__4))
    outcomes.append(run_case("03_erroneous_sameAs_forward", wrong_forward, shapes))

    # Reverse orientation, AI Act Article 14 -> GDPR Article 22
    wrong_reverse = revised + Graph()
    wrong_reverse.add((IRCCF.AIAct_Art__14_1__4, OWL.sameAs, IRCCF.GDPR_Art__22_1))
    outcomes.append(run_case("04_erroneous_sameAs_reverse", wrong_reverse, shapes))

    with (OUT / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["scenario", "conforms", "triple_count"])
        writer.writeheader()
        writer.writerows(outcomes)

    expected = [False, True, False, False]
    actual = [record["conforms"] for record in outcomes]
    print("Matches expected four-scenario pattern:", actual == expected)
    print("Reports saved to:", OUT)
    if actual != expected:
        raise SystemExit("Unexpected results. Review individual SHACL reports before citing.")


if __name__ == "__main__":
    main()
