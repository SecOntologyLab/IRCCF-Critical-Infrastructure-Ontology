import json,csv,re,hashlib,collections,os
from pathlib import Path
from artifact_tool import Workbook,SpreadsheetFile
root=Path('/mnt/data'); data=(root/'ics-attack-19.2.json').read_bytes(); d=json.loads(data);objs=d['objects']
active=lambda x:not x.get('revoked',False) and not x.get('x_mitre_deprecated',False)
mit=sorted([x for x in objs if x['type']=='course-of-action' and active(x)],key=lambda x:next((e['external_id'] for e in x.get('external_references',[]) if e.get('source_name')=='mitre-attack'),x['name']))
getid=lambda x:next((e['external_id'] for e in x.get('external_references',[]) if e.get('source_name')=='mitre-attack'), '')
controls=[]; missing=[]; a=[]
for m in mit:
 mid=getid(m); labels=m.get('labels',[])
 for i,label in enumerate(labels,1):
  match=re.match(r'^IEC (62443-[34]-[23]):(\d{4}) - ([A-Z]+) (\d+(?:\.\d+)+)$',label)
  nm=re.match(r'^NIST SP 800-53 Rev\. (\d+) - (.+)$',label)
  if match:
   series,year,kind,number=match.groups(); controls.append([mid,m['name'],'IEC',series,year,kind,number,label,m['id'],i,'source label',''])
  elif nm:
   rev,ids=nm.groups()
   for control in re.split(r'\s*[;,]\s*',ids):
    controls.append([mid,m['name'],'NIST SP 800-53','SP 800-53',f'Rev. {rev}','Control',control,label,m['id'],i,'source label',''])
  else:
   missing.append([mid,m['name'],label])
iec=[r for r in controls if r[2]=='IEC']; nist=[r for r in controls if r[2]=='NIST SP 800-53']
sr=[r for r in iec if r[3]=='62443-3-3' and r[5]=='SR']; unique_sr=sorted({r[6] for r in sr},key=lambda v:[int(x) for x in v.split('.')]); srrow=[]
for rid in unique_sr:
 links=[r for r in sr if r[6]==rid]; srrow.append([f'SR {rid}',len(set(r[0] for r in links)),', '.join(sorted(set(r[0] for r in links))), 'Observed in MITRE only; IEC catalogue completeness unverified'])
for m in mit:
 mid=getid(m); mm=[r for r in controls if r[0]==mid]; i=[r for r in mm if r[2]=='IEC']; n=[r for r in mm if r[2]=='NIST SP 800-53']; rev5=[r for r in n if r[4]=='Rev. 5'];rev4=[r for r in n if r[4]=='Rev. 4'];
 a.append([mid,m['name'],len(i),len({(r[3],r[5],r[6]) for r in i}),len(n),len({(r[4],r[6]) for r in n}),', '.join(sorted({r[6] for r in rev5})),', '.join(sorted({r[6] for r in rev4})), 'Ready: Rev5 control ID; CSF crosswalk pending' if rev5 else ('Needs rev4→rev5 crosswalk' if rev4 else 'No NIST control reference'),len([r for r in i if r[3]=='62443-3-3'])])
# Count independent active technique relationships from source
rels=[x for x in objs if x['type']=='relationship' and x.get('relationship_type')=='mitigates' and active(x)]; byid={x['id']:getid(x) for x in mit};tech={x['id']:getid(x) for x in objs if x['type']=='attack-pattern' and active(x)}
edge=sorted({(tech[x['target_ref']],byid[x['source_ref']],x['id']) for x in rels if x.get('source_ref') in byid and x.get('target_ref') in tech})
meta=[['Source filename','ics-attack-19.2.json'],['Source SHA-256',hashlib.sha256(data).hexdigest()],['Source release','ICS ATT&CK 19.2'],['Mitigations',len(mit)],['Mitigation–technique links',len(edge)],['IEC source references',len(iec)],['IEC SR distinct identifiers',len(unique_sr)],['NIST control refs (split semicolon/comma)',len(nist)],['Mitigations with IEC refs',len(set(r[0] for r in iec))],['Mitigations with NIST refs',len(set(r[0] for r in nist))],['NIST CSF mapping status','NOT MAPPED — official NIST crosswalk not obtained'],['IEC completeness','NOT VERIFIED — independent normative catalogue absent']]
headers={
 'MITRE_Controls':['Mitigation ID','Mitigation name','Framework','Standard','Edition','Requirement type','Control ID','Original MITRE label','STIX mitigation ID','Original label ordinal','Evidence type','CSF 2.0 mapping (pending)'],
 'Mitigation_Coverage':['Mitigation ID','Mitigation name','IEC labels','IEC unique references','NIST control IDs','NIST unique refs','Rev5 controls','Rev4 controls','Crosswalk status','IEC 62443-3-3 SR labels'],
 'Observed_IEC_SR':['IEC SR','Mitigation count','MITRE mitigation IDs','Completeness qualification'],
 'MITRE_Tech_Mitigation':['Technique ID','Mitigation ID','STIX relationship ID'],
 'Audit':['Check','Result']}
rows={'MITRE_Controls':controls,'Mitigation_Coverage':a,'Observed_IEC_SR':srrow,'MITRE_Tech_Mitigation':[list(x) for x in edge],'Audit':meta}
for name in rows:
 with open(root/(name+'.csv'),'w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(headers[name]);w.writerows(rows[name])
w=Workbook.create()
for name in rows:
 sh=w.worksheets.add(name);matrix=[headers[name]]+rows[name];sh.get_range_by_indexes(0,0,len(matrix),len(headers[name])).values=matrix
 sh.get_range_by_indexes(0,0,1,len(headers[name])).format={'fill':'#123650','font':{'bold':True,'color':'#FFFFFF'},'row_height':30}
 sh.freeze_panes.freeze_rows(1)
 for j in range(len(headers[name])):
  sh.get_range_by_indexes(0,j,len(matrix),1).format.column_width= min(52,max(15,len(headers[name][j])+3))
 # no tables if too slow
SpreadsheetFile.export_xlsx(w).save(str(root/'ICS_19_2_Standards_Bridge_Audit.xlsx'))
print('Summary',dict(meta));print('unique SR',len(unique_sr),unique_sr);print('MITRE controls',len(controls),'IEC refs',len(iec),'NIST refs',len(nist),'edges',len(edge));print('IEC types',collections.Counter((r[3],r[5]) for r in iec));print('NIST rev',collections.Counter(r[4] for r in nist));print('Nonstandard labels',missing[:10]);print('output exists', (root/'ICS_19_2_Standards_Bridge_Audit.xlsx').stat().st_size)
