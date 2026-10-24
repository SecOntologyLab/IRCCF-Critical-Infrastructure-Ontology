#!/usr/bin/env python3
"""Reproducible extraction of MITRE ATT&CK ICS 19.2 STIX 2.1.

Usage: python extract_ics_v19_2.py ics-attack-19.2.json [output_directory]
Requires artifact_tool only for XLSX export. Always writes CSV and audit JSON.
"""
import collections, csv, hashlib, json, pathlib, sys


def external_id(obj, prefix=None):
    ids = [r.get('external_id', '') for r in obj.get('external_references', [])]
    return next((x for x in ids if (not prefix or x.startswith(prefix))), '')


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python extract_ics_v19_2.py ics-attack-19.2.json [output_dir]')
    source = pathlib.Path(sys.argv[1]); dest = pathlib.Path(sys.argv[2] if len(sys.argv)>2 else source.parent)
    dest.mkdir(parents=True, exist_ok=True)
    raw = source.read_bytes(); data = json.loads(raw)
    objects = data['objects']; by_id = {o['id']: o for o in objects if 'id' in o}
    coll = next((o for o in objects if o.get('type') == 'x-mitre-collection' and o.get('name') == 'ICS ATT&CK'), None)
    if not coll or coll.get('x_mitre_version') != '19.2':
        raise ValueError('Expected ICS ATT&CK collection v19.2; found '+str(coll and coll.get('x_mitre_version')))
    member_refs = {v['object_ref'] for v in coll.get('x_mitre_contents', [])}
    # The collection membership is the versioned scope; exclude revoked and deprecated content.
    eligible = {k: v for k, v in by_id.items() if k in member_refs and not v.get('revoked') and not v.get('x_mitre_deprecated')}
    tactics = [o for o in eligible.values() if o.get('type') == 'x-mitre-tactic']
    techniques = [o for o in eligible.values() if o.get('type') == 'attack-pattern']
    mitigations = [o for o in eligible.values() if o.get('type') == 'course-of-action']
    tactic_by_short = {o.get('x_mitre_shortname'): o for o in tactics}
    tactic_rows = sorted([[external_id(t,'TA'), t.get('name',''), t.get('x_mitre_shortname',''), t['id'], t.get('description',''), t.get('modified','')] for t in tactics])
    tactic_ids = {r[0] for r in tactic_rows}
    technique_rows=[]; technique_tactics={}
    for t in techniques:
        slots=[]
        for k in t.get('kill_chain_phases',[]):
            if k.get('kill_chain_name')=='mitre-ics-attack':
                tt=tactic_by_short.get(k.get('phase_name'))
                if tt: slots.append((external_id(tt,'TA'),tt['name']))
        slots=sorted(set(slots)); technique_tactics[t['id']]=[x[0] for x in slots]
        technique_rows.append([external_id(t,'T'),t.get('name',''), 'Yes' if t.get('x_mitre_is_subtechnique') else 'No', '; '.join(x[0] for x in slots), '; '.join(x[1] for x in slots), t['id'], t.get('description',''),t.get('modified','')])
    technique_rows.sort()
    mitigation_rows=sorted([[external_id(m,'M'),m.get('name',''),m['id'],m.get('description',''),m.get('modified','')] for m in mitigations])
    # STIX mitigates edges are directed mitigation -> technique.
    edge_rows=[]; skipped_edges=[]; edges=set()
    for r in objects:
        if r.get('type')!='relationship' or r.get('relationship_type')!='mitigates':continue
        src=r.get('source_ref'); tgt=r.get('target_ref')
        if src in eligible and tgt in eligible and eligible[src].get('type')=='course-of-action' and eligible[tgt].get('type')=='attack-pattern':
            m,t=eligible[src],eligible[tgt]; key=(src,tgt)
            if key in edges: continue
            edges.add(key)
            edge_rows.append([external_id(t,'T'),t.get('name',''),external_id(m,'M'),m.get('name',''), '; '.join(technique_tactics[tgt]), r['id'],src,tgt,r.get('description',''),r.get('modified','')])
        else: skipped_edges.append(r.get('id',''))
    edge_rows.sort()
    def write_csv(name, headers, rows):
        with (dest/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(headers);w.writerows(rows)
    tables={
       'Tactics':(['Tactic ID','Tactic Name','MITRE shortname','STIX ID','Description','Modified'],tactic_rows),
       'Techniques':(['Technique ID','Technique Name','Is Sub-technique','Tactic IDs','Tactic Names','STIX ID','Description','Modified'],technique_rows),
       'Mitigations':(['Mitigation ID','Mitigation Name','STIX ID','Description','Modified'],mitigation_rows),
       'Relationships':(['Technique ID','Technique Name','Mitigation ID','Mitigation Name','Tactic IDs','Relationship STIX ID','Mitigation STIX ID','Technique STIX ID','Relationship description','Modified'],edge_rows)}
    for name,(headers,rows) in tables.items():write_csv(name.lower()+'.csv',headers,rows)
    mapped_techniques={r[0] for r in edge_rows}
    audit={
       'source_filename':source.name,'sha256':hashlib.sha256(raw).hexdigest(),
       'collection_version':coll['x_mitre_version'],'collection_stix_id':coll['id'],
       'collection_modified':coll.get('modified'),'bundle_id':data.get('id'),
       'selection':'Only objects listed under x_mitre_contents, excluding revoked/deprecated; edges with both endpoints in scope.',
       'counts':{'tactics':len(tactic_rows),'techniques_and_subtechniques':len(technique_rows),
           'parent_techniques':sum(r[2]=='No' for r in technique_rows),
           'subtechniques':sum(r[2]=='Yes' for r in technique_rows),
           'mitigations':len(mitigation_rows),'unique_mitigation_technique_relationships':len(edge_rows),
           'techniques_with_mitigation':len(mapped_techniques),
           'techniques_without_mitigation':len(technique_rows)-len(mapped_techniques),
           'excluded_relationships':len(skipped_edges)},
       'validation':{'twelve_tactics':len(tactic_rows)==12,
            'unique_tactic_ids':len(tactic_ids)==len(tactic_rows),
            'unique_technique_ids':len({r[0] for r in technique_rows})==len(technique_rows),
            'unique_mitigation_ids':len({r[0] for r in mitigation_rows})==len(mitigation_rows),
            'all_technique_tactics_resolve':all(x in tactic_ids for r in technique_rows for x in r[3].split('; ') if x),
            'all_relationship_endpoints_resolve':all(r[0] in {t[0] for t in technique_rows} and r[2] in {m[0] for m in mitigation_rows} for r in edge_rows)},
       'techniques_without_mitigation_ids':sorted({r[0] for r in technique_rows}-mapped_techniques),
       'note':'Mitigation links are not CSF mappings; unmapped technique means no in-scope MITRE mitigates edge, not lack of possible defenses.'}
    (dest/'extraction_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    try:
        from artifact_tool import Workbook, SpreadsheetFile
        wb=Workbook.create()
        for name,(headers,rows) in tables.items():
            sh=wb.worksheets.add(name)
            sh.get_range_by_indexes(0,0,len(rows)+1,len(headers)).values=[headers]+rows
            sh.get_range_by_indexes(0,0,1,len(headers)).format={'fill':'#17365D','font':{'bold':True,'color':'#FFFFFF'},'row_height':28}
            sh.freeze_panes.freeze_rows(1)
            for i in range(len(headers)):
                sh.get_range_by_indexes(0,i,len(rows)+1,1).format.column_width= 46 if ('Description' in headers[i]) else (30 if 'Name' in headers[i] else 23)
        a=wb.worksheets.add('Audit')
        entries=[['Field','Value']]+[[k,str(v)] for k,v in audit.items() if k not in ('techniques_without_mitigation_ids','validation','counts')]
        entries += [[k,str(v)] for k,v in audit['counts'].items()]
        entries += [['Check: '+k, str(v)] for k,v in audit['validation'].items()]
        a.get_range_by_indexes(0,0,len(entries),2).values=entries
        a.get_range('A1:B1').format={'fill':'#17365D','font':{'bold':True,'color':'#FFFFFF'}}
        a.get_range('A:A').format.column_width=42;a.get_range('B:B').format.column_width=80
        SpreadsheetFile.export_xlsx(wb).save(str(dest/'ics_19_2_evidence_inventory.xlsx'))
        audit['workbook_created']=True
    except ImportError:
        audit['workbook_created']=False
        (dest/'extraction_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps(audit,indent=2))

if __name__=='__main__':main()
