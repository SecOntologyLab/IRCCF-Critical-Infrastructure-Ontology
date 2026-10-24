"""IRCCF controlled synthetic ABox scaling and entailment benchmark (Python 3.10+).
Original source graph is preserved. Each synthetic replica reuses original schema,
and creates uniquely identified synthetic individuals with copied instance relationships.
RDFLib+owlrl entailment does not assess full OWL DL or operational SOC performance.
"""
import argparse, csv, json, platform, statistics, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
FILENAME = 'irccf_stage5_3_PRELIMINARY_all47_active.ttl'
SCALES = (1, 2, 5, 10)
PROFILES = ('RDFS', 'OWL_RL')


def construct(source, scale):
    from rdflib import Graph, URIRef, BNode, RDF, RDFS, OWL
    from rdflib.namespace import SKOS
    from collections import defaultdict
    graph = Graph()
    graph.parse(source, format='turtle')
    original = len(graph)
    # Exclude all known schema/predicate nodes, so all added statements describe
    # synthetic instances of *unchanged original vocabulary*.
    schema_types = {OWL.Class, RDFS.Class, RDF.Property, OWL.ObjectProperty,
                    OWL.DatatypeProperty, OWL.AnnotationProperty, OWL.Ontology,
                    OWL.Restriction, OWL.NamedIndividual if False else OWL.Ontology}
    schema_subjects = set()
    for s,p,o in graph.triples((None,RDF.type,None)):
        if o in schema_types:
            schema_subjects.add(s)
    schema_subjects.update(p for s,p,o in graph)
    # Prevent ontology vocabulary terms from being cloned as individuals.
    for s,p,o in graph.triples((None, RDFS.subClassOf, None)):
        schema_subjects.update((s,o))
    for s,p,o in graph.triples((None, RDFS.subPropertyOf, None)):
        schema_subjects.update((s,o))
    for s,p,o in graph.triples((None, OWL.equivalentClass, None)):
        schema_subjects.update((s,o))
    # Include instance subjects (URI or blank) but do not reproduce schema declarations.
    triples = sorted(((s,p,o) for s,p,o in graph if s not in schema_subjects),
                     key=lambda row: tuple(str(x) for x in row))
    if not triples:
        raise RuntimeError('No instance records available to replicate')
    # Approximate scale multiples while adding whole coherent replica batches.
    copies = round((original * (scale-1)) / len(triples))
    for k in range(1, copies+1):
        individual_nodes = {s for s,p,o in triples}
        def remap(term):
            if term not in individual_nodes: return term
            if isinstance(term, BNode): return BNode(f'synthetic_{k}_{str(term)}')
            return URIRef(f'https://example.org/irccf-scalability/synthetic/{k}/' + str(term).replace('%','%25').replace('#','%23').replace('/','%2F'))
        for s,p,o in triples:
            graph.add((remap(s), p, remap(o)))
    return graph, {'requested_multiplier':scale,'original_triples':original,
                   'instance_triples_per_replica':len(triples),
                   'replica_count':copies,'asserted_triples':len(graph),
                   'actual_multiplier':round(len(graph)/original,3),
                   'synthetic_added_triples':len(graph)-original}


def worker(source, multiplier, profile, output):
    import psutil
    from rdflib import RDFS, RDF, OWL
    from owlrl import DeductiveClosure, RDFS_Semantics, OWLRL_Semantics
    proc=psutil.Process()
    t0=time.perf_counter()
    graph, meta=construct(source,multiplier)
    tload=time.perf_counter()-t0
    base=set(graph)
    t1=time.perf_counter()
    sem=RDFS_Semantics if profile=='RDFS' else OWLRL_Semantics
    DeductiveClosure(sem,axiomatic_triples=False,datatype_axioms=False).expand(graph)
    elapsed=time.perf_counter()-t1
    inferred=set(graph)-base
    out={**meta,'profile':profile,'status':'ok', 'construction_seconds':round(tload,5),
         'reasoning_seconds':round(elapsed,5),'new_triples':len(inferred),
         'closure_triples':len(graph),'inferred_types':sum(p==RDF.type for s,p,o in inferred),
         'inferred_subclasses':sum(p==RDFS.subClassOf for s,p,o in inferred),
         'inferred_sameas':sum(p==OWL.sameAs for s,p,o in inferred),
         'final_rss_mb':round(proc.memory_info().rss/1048576,2),
         'python':platform.python_version(),'platform':platform.platform()}
    Path(output).write_text(json.dumps(out,indent=2),encoding='utf8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ontology',type=Path,default=HERE/'ontology'/'releases'/FILENAME)
    p.add_argument('--runs',type=int,default=1)
    p.add_argument('--scales',type=int,nargs='+',default=list(SCALES))
    p.add_argument('--timeout',type=int,default=180,help='Hard per-run timeout (seconds)')
    p.add_argument('--max-memory-mb',type=int,default=2500)
    p.add_argument('--output',type=Path,default=HERE/'results'/'verification'/'scalability')
    p.add_argument('--_worker',nargs=4,metavar=('TTL','MULTIPLIER','PROFILE','OUTPUT'))
    a=p.parse_args()
    if a._worker:
        source,mult,prof,dest=a._worker
        worker(Path(source),int(mult),prof,Path(dest))
        return
    if a.runs<1 or any(s<1 for s in a.scales):p.error('runs and scales must be positive')
    try:
        import rdflib, owlrl, psutil
    except ImportError:
        p.error('Install dependencies: py -m pip install rdflib owlrl psutil')
    if not a.ontology.exists():p.error(f'Ontology not found: {a.ontology}')
    a.output.mkdir(exist_ok=True,parents=True)
    rows=[]
    for mult in a.scales:
      for prof in PROFILES:
       for i in range(1,a.runs+1):
        dest=a.output/f'{prof}_{mult}x_run{i}.json'
        cmd=[sys.executable,str(Path(__file__).resolve()),'--_worker',str(a.ontology.resolve()),str(mult),prof,str(dest.resolve())]
        task=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        started=time.monotonic(); peak=0.; status=None
        while task.poll() is None:
            if time.monotonic()-started>a.timeout:
                status='timeout';task.kill();break
            try:
                process=psutil.Process(task.pid)
                rss=process.memory_info().rss/1048576
                peak=max(peak,rss)
                if rss>a.max_memory_mb:
                    status='memory_limit';task.kill();break
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            time.sleep(.15)
        stdout,stderr=task.communicate()
        if status is None and task.returncode != 0:status='error'
        if status is None:
            row=json.loads(dest.read_text(encoding='utf8'))
            row.update(run=i,peak_rss_mb=round(peak,2))
            print(f"{mult}x {prof} run {i}: {row['asserted_triples']} triples; "
                  f"{row['new_triples']} inferred; {row['reasoning_seconds']:.3f}s; "
                  f"peak RSS {peak:.1f} MB",flush=True)
        else:
            row={'requested_multiplier':mult,'profile':prof,'run':i,'status':status,'peak_rss_mb':round(peak,2),'error':stderr[-1500:]}
            print(f'{mult}x {prof} run {i}: {status}. {stderr[-200:]}',flush=True)
        rows.append(row)
        with (a.output/'runs.csv').open('w',newline='',encoding='utf8') as f:
            cols=sorted({key for r in rows for key in r})
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    summary=[]
    for mult in a.scales:
      for prof in PROFILES:
        group=[r for r in rows if r.get('requested_multiplier')==mult and r['profile']==prof and r['status']=='ok']
        if group:
            summary.append({'scale':mult,'profile':prof,'runs_completed':len(group),
                'asserted_triples':group[0]['asserted_triples'],'actual_multiplier':group[0]['actual_multiplier'],
                'inferred_triples':group[0]['new_triples'],
                'mean_seconds':round(statistics.mean(r['reasoning_seconds'] for r in group),5),
                'sample_sd_seconds':round(statistics.stdev(r['reasoning_seconds'] for r in group),5) if len(group)>1 else '',
                'max_peak_rss_mb':max(r['peak_rss_mb'] for r in group)})
    with (a.output/'summary.csv').open('w',newline='',encoding='utf8') as f:
        if summary:
            w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    (a.output/'methods.json').write_text(json.dumps({'ontology':str(a.ontology),'scales':a.scales,'runs':a.runs,
       'timeout_seconds':a.timeout,'memory_limit_mb':a.max_memory_mb,
       'rdflib':rdflib.__version__,'owlrl':getattr(owlrl,'__version__','unknown'),
       'sampling_note':'Peak RSS is sampled periodically; brief peaks might be missed',
       'design_note':'Original schema unchanged. Synthetic uniquely identified ABox replicas only. Each clone uses existing predicates/types.'},indent=2),encoding='utf8')
    print('Results:',a.output.resolve(),flush=True)

if __name__=='__main__':main()
