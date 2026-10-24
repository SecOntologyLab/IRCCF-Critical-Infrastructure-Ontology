"""Reproducible RDFS/OWL RL entailment experiment. Python 3.10+.

Runs inference in isolated child processes. By default uses 1 run per profile;
repeat with --runs 3 for reported benchmark statistics.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

NAME = 'irccf_stage5_3_PRELIMINARY_all47_active.ttl'
ROOT = Path(__file__).resolve().parents[2]
PROFILES = ('RDFS', 'OWL_RL')


def worker(ontology, profile, output):
    from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
    from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
    import psutil
    import rdflib
    import owlrl

    proc = psutil.Process()
    initial = time.perf_counter()
    g = Graph()
    g.parse(str(ontology), format='turtle')
    load_s = time.perf_counter() - initial
    asserted = set(g)
    basic = {
        'rdf_triples_before': len(asserted),
        'explicit_subclass_axioms': sum(1 for _ in g.triples((None,RDFS.subClassOf,None))),
        'explicit_equivalentclass_axioms': sum(1 for _ in g.triples((None,OWL.equivalentClass,None))),
        'load_seconds': round(load_s, 5),
        'profile': profile,
        'rdflib_version': rdflib.__version__,
        'owlrl_version': getattr(owlrl,'__version__','unknown'),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
    }
    begin = time.perf_counter()
    semantics = RDFS_Semantics if profile=='RDFS' else OWLRL_Semantics
    DeductiveClosure(semantics, axiomatic_triples=False, datatype_axioms=False).expand(g)
    reasoning_s = time.perf_counter() - begin
    inferred = set(g) - asserted
    # These include axiomatic/schema-derived statements; not all are domain-relevant.
    relevant_predicates = [RDF.type,RDFS.subClassOf,RDFS.subPropertyOf,OWL.sameAs]
    counts = {p.split('#')[-1]:sum(1 for triple in inferred if triple[1] == p) for p in relevant_predicates}
    ns = Namespace('https://purl.org/ircc-framework#')
    named_inferred = [t for t in inferred if str(t[0]).startswith(str(ns)) and str(t[2]).startswith(str(ns))]
    examples = []
    for s,p,o in sorted(named_inferred, key=lambda x: tuple(map(str,x))):
        if p in relevant_predicates:
            examples.append(f'{s.n3()} {p.n3()} {o.n3()} .')
        if len(examples)>=25:break
    basic.update({
        'status':'ok','inference_seconds':round(reasoning_s,5),
        'rdf_triples_after':len(g), 'newly_entailed_triples':len(inferred),
        'inferred_type_triples':counts['type'],
        'inferred_subclass_triples':counts['subClassOf'],
        'inferred_subproperty_triples':counts['subPropertyOf'],
        'inferred_sameas_triples':counts['sameAs'],
        'named_to_named_inferences':len(named_inferred),
        'peak_memory_mb_at_end':round(proc.memory_info().rss/(1024*1024),2),
        'sample_named_entailments':examples,
    })
    Path(output).write_text(json.dumps(basic,indent=2), encoding='utf8')


def positive_control():
    """Separate synthetic test: deliberately not merged into research ontology."""
    from rdflib import Graph, Namespace, RDF, RDFS, OWL
    from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
    ex=Namespace('https://example.org/controlled-owl-test#')
    gr=Graph()
    gr.add((ex.ICSAsset,RDFS.subClassOf,ex.Asset))
    gr.add((ex.Asset,RDFS.subClassOf,ex.CybersecurityEntity))
    gr.add((ex.Sensor1,RDF.type,ex.ICSAsset))
    base=set(gr)
    out={}
    for prof,sem in [('RDFS',RDFS_Semantics),('OWL_RL',OWLRL_Semantics)]:
        gg=Graph()
        for t in base:gg.add(t)
        DeductiveClosure(sem,axiomatic_triples=False,datatype_axioms=False).expand(gg)
        out[prof]={
          'transitive_subclass_entailment':(ex.ICSAsset,RDFS.subClassOf,ex.CybersecurityEntity) in gg and (ex.ICSAsset,RDFS.subClassOf,ex.CybersecurityEntity) not in base,
          'inferred_instance_type':(ex.Sensor1,RDF.type,ex.CybersecurityEntity) in gg and (ex.Sensor1,RDF.type,ex.CybersecurityEntity) not in base,
        }
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ontology',type=Path,default=ROOT/'ontology'/'releases'/NAME)
    ap.add_argument('--runs',type=int,default=1)
    ap.add_argument('--timeout',type=int,default=240, help='Seconds allowed per inference run')
    ap.add_argument('--max-memory-mb',type=int,default=2500)
    ap.add_argument('--output',type=Path,default=ROOT/'results'/'verification'/'reasoning')
    ap.add_argument('--_worker',nargs=3,metavar=('TTL','PROFILE','JSON'))
    a=ap.parse_args()
    if a._worker:
        worker(Path(a._worker[0]),a._worker[1],Path(a._worker[2]));return
    try:
        import rdflib, owlrl, psutil
    except ImportError:
        print('Missing packages. Run: py -m pip install rdflib owlrl psutil');sys.exit(2)
    if not a.ontology.is_file():
        print('Cannot find:',a.ontology);sys.exit(2)
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'positive_control.json').write_text(json.dumps(positive_control(),indent=2),encoding='utf8')
    rows=[]
    for profile in PROFILES:
        for i in range(1,a.runs+1):
            filepath=a.output/f'{profile}_run{i}.json'
            command=[sys.executable,str(Path(__file__).resolve()),'--_worker',str(a.ontology.resolve()),profile,str(filepath)]
            start=time.perf_counter()
            child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            mem_peak=0
            try:
                proc=psutil.Process(child.pid)
                while child.poll() is None:
                    try:mem_peak=max(mem_peak,proc.memory_info().rss/(1024*1024))
                    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
                    if time.perf_counter()-start>a.timeout or mem_peak>a.max_memory_mb:
                        child.kill()
                        child.communicate()
                        reason='timeout' if time.perf_counter()-start>a.timeout else 'memory_limit'
                        rows.append({'profile':profile,'run':i,'status':reason,'wall_seconds':round(time.perf_counter()-start,3),'observed_peak_rss_mb':round(mem_peak,2)})
                        print(profile,i,reason,flush=True)
                        break
                    time.sleep(.15)
                else:
                    stdout,stderr=child.communicate()
                    if child.returncode==0 and filepath.exists():
                        data=json.loads(filepath.read_text(encoding='utf8'))
                        row={k:v for k,v in data.items() if not isinstance(v,list)}
                        row.update({'run':i,'wall_seconds':round(time.perf_counter()-start,3),'observed_peak_rss_mb':round(mem_peak,2)})
                        rows.append(row)
                        print(f"{profile} run {i}: {data['newly_entailed_triples']} new triples in {data['inference_seconds']} sec",flush=True)
                    else:
                        rows.append({'profile':profile,'run':i,'status':'error','error':stderr[-2000:],'wall_seconds':round(time.perf_counter()-start,3)})
                        print(profile,i,'ERROR:',stderr[-600:],flush=True)
            finally:
                if child.poll() is None:child.kill();child.wait()
    keys=list(dict.fromkeys(key for row in rows for key in row))
    with (a.output/'benchmark_results.csv').open('w',newline='',encoding='utf8') as f:
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(rows)
    summary={p:{'successful_runs':len(v),'mean_seconds':round(statistics.mean(v),5) if v else None,'median_seconds':round(statistics.median(v),5) if v else None} for p in PROFILES for v in [[r['inference_seconds'] for r in rows if r.get('profile')==p and r.get('status')=='ok']]}
    (a.output/'summary.json').write_text(json.dumps({'ontology':str(a.ontology),'positive_control':positive_control(),'timings':summary},indent=2),encoding='utf8')
    print('Results:',a.output.resolve())

if __name__=='__main__':main()
