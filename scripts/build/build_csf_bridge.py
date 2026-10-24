import csv,re,json,hashlib,collections
from pathlib import Path
from artifact_tool import Blob,SpreadsheetFile,Workbook
P=Path('/mnt/data'); OUT=P/'ICS_v19_2_to_CSF2_Evidence_Bridge.xlsx'
def loadcsv(p):
 with open(P/p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(x):
 x=str(x or '').strip().upper()
 m=re.fullmatch(r'([A-Z]{2})-0*(\d+)(.*)',x)
 return f'{m.group(1)}-{int(m.group(2))}{m.group(3)}' if m else x
src=SpreadsheetFile.import_xlsx(Blob.load(str(P/'Cybersecurity_Framework_v2-0_Concept_Crosswalk_800-53_5_2_0_draft.xlsx')))
raw=src.worksheets.get_item_at(0).get_range('A1:F800').values
csf=[]
for i,r in enumerate(raw[1:],2):
 code=str(r[0] or '').strip(); ctl=str(r[2] or '').strip()
 if re.fullmatch(r'(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}',code) and ctl:
  for item in re.split(r'[,;\n]+',ctl):
   item=item.strip()
   if item:csf.append({'CSF Subcategory':code,'CSF Function':code[:2],'CSF Text':str(r[1] or '').strip(),'NIST Source ID':item,'Normalized Control':norm(item),'Crosswalk row':i})
controls=loadcsv('MITRE_Controls.csv'); links=loadcsv('MITRE_Tech_Mitigation.csv'); techs=loadcsv('ics_v19_2_extract/techniques.csv')
index=collections.defaultdict(list)
for c in csf:index[c['Normalized Control']].append(c)
nist=[r for r in controls if r['Framework']=='NIST SP 800-53']
bridge=[]; missed=[]
for r in nist:
 if r['Edition']!='Rev. 5':
  missed.append({'Mitigation':r['Mitigation ID'],'Control':r['Control ID'],'Edition':r['Edition'],'Reason':'Rev.4 reference: NOT converted without an authoritative revision crosswalk'})
  continue
 hits=index[norm(r['Control ID'])]
 if not hits:missed.append({'Mitigation':r['Mitigation ID'],'Control':r['Control ID'],'Edition':r['Edition'],'Reason':'No exact normalized Rev.5 control in supplied draft CSF crosswalk'})
 for h in hits:
  bridge.append({'Mitigation ID':r['Mitigation ID'],'Mitigation name':r['Mitigation name'],'SP800-53 MITRE ID':r['Control ID'],'SP800-53 Join Key':norm(r['Control ID']),'CSF Subcategory':h['CSF Subcategory'],'CSF Function':h['CSF Function'],'CSF Description':h['CSF Text'],'MITRE Label':r['Original MITRE label'],'STIX mitigation ID':r['STIX mitigation ID'],'MITRE label ordinal':r['Original label ordinal'],'Crosswalk row':h['Crosswalk row'],'Mapping status':'Published MITRE control label + supplied NIST crosswalk (draft)'})
by_m=collections.defaultdict(list)
for b in bridge:by_m[b['Mitigation ID']].append(b)
t_by_id={x['Technique ID']:x for x in techs}
paths=[]
for link in links:
 t=t_by_id.get(link['Technique ID'])
 if not t:continue
 for b in by_m[link['Mitigation ID']]:
  for tactic in (t['Tactic IDs'] or '').split(';'):
   if tactic.strip():
    paths.append({'Tactic ID':tactic.strip(),'Tactic Name':t['Tactic Names'].strip().strip(),'Technique ID':link['Technique ID'],'Technique Name':t['Technique Name'],'Mitigation ID':link['Mitigation ID'],'SP800-53 Control':b['SP800-53 Join Key'],'CSF Subcategory':b['CSF Subcategory'],'CSF Function':b['CSF Function'],'MITRE Relation ID':link['STIX relationship ID'],'MITRE Label':b['MITRE Label'],'NIST Crosswalk Row':b['Crosswalk row']})
# de-duplicate exact evidence paths, retaining relationship provenance
seen=set(); unique=[]
for p in paths:
 k=(p['Tactic ID'],p['Technique ID'],p['Mitigation ID'],p['SP800-53 Control'],p['CSF Subcategory'],p['MITRE Relation ID'])
 if k not in seen: seen.add(k);unique.append(p)
aggregate=collections.defaultdict(lambda:{'tech':set(),'mit':set(),'control':set(),'subcat':set(),'paths':0})
for p in unique:
 k=(p['Tactic ID'],p['Tactic Name'],p['CSF Function']);a=aggregate[k];a['tech'].add(p['Technique ID']);a['mit'].add(p['Mitigation ID']);a['control'].add(p['SP800-53 Control']);a['subcat'].add(p['CSF Subcategory']);a['paths']+=1
agg=[]
for (tid,tname,fn),a in sorted(aggregate.items()):agg.append({'Tactic ID':tid,'Tactic Name':tname,'CSF Function':fn,'Distinct Techniques':len(a['tech']),'Distinct Mitigations':len(a['mit']),'Distinct SP800-53 Controls':len(a['control']),'Distinct CSF Subcategories':len(a['subcat']),'Distinct Evidence Paths':a['paths']})
all_tactics={}
for t in techs:
 for tid,tname in zip((t['Tactic IDs'] or '').split(';'),(t['Tactic Names'] or '').split(';')):
  if tid.strip():all_tactics[tid.strip()]=tname.strip()
function_names={'GV':'Govern','ID':'Identify','PR':'Protect','DE':'Detect','RS':'Respond','RC':'Recover'}
table=[]
for tid,tname in sorted(all_tactics.items()):
 rows=[r for r in agg if r['Tactic ID']==tid]
 funcs=[function_names[f] for f in function_names if any(r['CSF Function']==f for r in rows)]
 table.append({'Tactic ID':tid,'MITRE ICS Tactic':tname,'Supported CSF Functions':', '.join(funcs) or 'None established','Distinct matched techniques':len({p['Technique ID'] for p in unique if p['Tactic ID']==tid}),'Evidence path count':sum(r['Distinct Evidence Paths'] for r in rows),'Regulatory triggers':'NOT ASSESSED','Status':'Provisional: Rev.5 only; crosswalk filename marked draft'})
source_checks=[['ATT&CK data version','19.2'],['Crosswalk filename','Cybersecurity_Framework_v2-0_Concept_Crosswalk_800-53_5_2_0_draft.xlsx'],['Crosswalk SHA256',hashlib.sha256((P/'Cybersecurity_Framework_v2-0_Concept_Crosswalk_800-53_5_2_0_draft.xlsx').read_bytes()).hexdigest()],['Crosswalk exact record count',len(csf)],['Distinct crosswalk CSF subcategories',len({x['CSF Subcategory'] for x in csf})],['Distinct normalized crosswalk NIST controls',len({x['Normalized Control'] for x in csf})],['MITRE NIST control label records',len(nist)],['MITRE Rev.5 NIST control labels',sum(x['Edition']=='Rev. 5' for x in nist)],['MITRE Rev.4 NIST control labels',sum(x['Edition']=='Rev. 4' for x in nist)],['Matched Rev.5 label records',sum(bool(index[norm(x['Control ID'])]) for x in nist if x['Edition']=='Rev. 5')],['Unique control to CSF subcategory hits',len({(x['SP800-53 Join Key'],x['CSF Subcategory']) for x in bridge})],['Distinct mitigations matched',len({x['Mitigation ID'] for x in bridge})],['Source-side relationship records',len(links)],['Unique technique → mitigation → control → CSF evidence paths',len(unique)],['Distinct techniques with joined paths',len({p['Technique ID'] for p in unique})],['Tactics with paths',len({p['Tactic ID'] for p in unique})],['Notice','Control matches are topical reference associations, not regulatory compliance or validated semantic equivalence.']]
wb=Workbook.create()
def sheet(name,rows):
 s=wb.worksheets.add(name)
 if not rows:return
 if isinstance(rows[0],dict):
  columns=list(rows[0]);data=[columns]+[[str(r.get(c,'')) if r.get(c,'') is not None else '' for c in columns] for r in rows]
 else:data=rows
 n=len(data);m=len(data[0]);
 # chunks to avoid large remote payloads
 for i in range(0,n,250):s.get_range_by_indexes(i,0,min(250,n-i),m).values=data[i:i+250]
 s.get_range_by_indexes(0,0,1,m).format={'fill':'#17365D','font':{'bold':True,'color':'#FFFFFF'},'row_height':28}
 s.freeze_panes.freeze_rows(1)
 for j in range(m):s.get_range_by_indexes(0,j,n,1).format.column_width=min(38,max(15,len(str(data[0][j]))+4))
 return s
sheet('Readme Audit', [['Metric','Value']]+source_checks)
sheet('Provisional Table III',table)
sheet('Tactic Function Evidence',agg)
sheet('Technique Evidence Paths',unique)
sheet('Mitigation CSF Links',bridge)
sheet('Unmapped NIST Labels',missed)
sheet('NIST CSF Source Rows',csf)
SpreadsheetFile.export_xlsx(wb).save(str(OUT))
for name,rows in [('provisional_table_III.csv',table),('csf_evidence_paths.csv',unique),('unmapped_nist_references.csv',missed)]:
 if rows:
  with open(P/name,'w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'audit':source_checks,'tactics':table,'unmatched':missed},indent=2))
