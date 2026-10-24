import csv, json, collections
from pathlib import Path
from artifact_tool import Workbook, SpreadsheetFile
P=Path('/mnt/data')
def load(fn):
 with open(P/fn,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
tactics=load('ics_v19_2_extract/tactics.csv'); techniques=load('ics_v19_2_extract/techniques.csv'); evidence=load('csf_evidence_paths.csv')
functions=['GV','ID','PR','DE','RS','RC']; names={'GV':'Govern','ID':'Identify','PR':'Protect','DE':'Detect','RS':'Respond','RC':'Recover'}
by_tactic=collections.defaultdict(set); detail={}
for r in techniques:
 for tid in r['Tactic IDs'].split(';'):
  tid=tid.strip()
  if tid:by_tactic[tid].add(r['Technique ID']); detail[(tid,r['Technique ID'])]=r
supported=collections.defaultdict(set); paths=collections.Counter()
for r in evidence:
 key=(r['Tactic ID'],r['CSF Function'])
 assert r['Technique ID'] in by_tactic[r['Tactic ID']],(r['Tactic ID'],r['Technique ID'])
 supported[key].add(r['Technique ID']);paths[key]+=1
thresholds=[0.25,0.50,0.75]
orders=['TA0108','TA0104','TA0110','TA0111','TA0103','TA0102','TA0109','TA0100','TA0101','TA0107','TA0106','TA0105']
tactic_names={r['Tactic ID']:r['Tactic Name'] for r in tactics}
coverage=[]; assigned=[]; missing=[]; summary=[]; matrix=[]
for t in orders:
 population=by_tactic[t]; n=len(population); observed=set().union(*(supported[t,f] for f in functions));
 matrix.append([t,tactic_names[t],n,len(observed),len(population-observed)]+[round(100*len(supported[t,f])/n,2) for f in functions])
 for f in functions:
  count=len(supported[t,f]); coverage.append([t,tactic_names[t],f,n,count,n-count,round(100*count/n,4),paths[t,f],len(observed)])
 for th in thresholds:
  fs=[f for f in functions if len(supported[t,f])/n>=th]
  assigned.append([t,tactic_names[t],f'{int(th*100)}%',', '.join(fs) if fs else '(none)', ', '.join(names[f] for f in fs) if fs else '(none)',len(fs)])
 for technique in sorted(population-observed):
  missing.append([t,tactic_names[t],technique,detail[t,technique]['Technique Name'],detail[t,technique]['Is Sub-technique']])
 summary.append([t,tactic_names[t],n,len(observed),len(population-observed),*[int(len(supported[t,f])/n>=0.25) for f in functions]])
counts={int(th*100):sum(a[-1] for a in assigned if a[2]==f'{int(th*100)}%') for th in thresholds}
print('Coverage matrix:');print('Tactic, denominator, mapped union, '+','.join(functions))
for r in matrix:print(r[1],r[2],r[3],r[5:])
print('threshold assignment counts',counts)
print('missing',len(missing),missing)
print('Assignments')
for t in orders:print(t,[(a[2],a[3]) for a in assigned if a[0]==t])
with open(P/'ICS_CSF2_Function_Coverage_Matrix.csv','w',newline='',encoding='utf-8-sig') as fh:
 w=csv.writer(fh);w.writerow(['Tactic ID','Tactic','Total technique memberships','Mapped technique memberships','Unmapped technique memberships']+functions);w.writerows(matrix)
with open(P/'ICS_CSF2_Threshold_Sensitivity.csv','w',newline='',encoding='utf-8-sig') as fh:
 w=csv.writer(fh);w.writerow(['Tactic ID','Tactic','Threshold','Function codes assigned','Function names assigned','Number assigned']);w.writerows(assigned)
with open(P/'ICS_CSF2_Function_Coverage_Detail.csv','w',newline='',encoding='utf-8-sig') as fh:
 w=csv.writer(fh);w.writerow(['Tactic ID','Tactic','Function','Total techniques in tactic','Distinct mapped techniques','Not linked to this Function','Percent coverage','Evidence path count','Distinct mapped techniques any Function']);w.writerows(coverage)
with open(P/'ICS_CSF2_Unmapped_Techniques.csv','w',newline='',encoding='utf-8-sig') as fh:
 w=csv.writer(fh);w.writerow(['Tactic ID','Tactic','Technique ID','Technique','Is sub-technique']);w.writerows(missing)
wb=Workbook.create()
def sheet(name,headers,rows,widths=None):
 sh=wb.worksheets.add(name)
 sh.get_range_by_indexes(0,0,len(rows)+1,len(headers)).values=[headers]+rows
 sh.get_range_by_indexes(0,0,1,len(headers)).format={'fill':'#15344B','font':{'bold':True,'color':'#FFFFFF'},'row_height':33,'wrap_text':True}
 sh.freeze_panes.freeze_rows(1)
 if widths:
  for j,wd in enumerate(widths):sh.get_range_by_indexes(0,j,len(rows)+1,1).format.column_width=wd
 return sh
s=sheet('Coverage Matrix',['Tactic ID','Tactic','Total techniques','Mapped any Function','Unmapped']+[f+' (%)' for f in functions],matrix,[15,28,18,18,15]+[14]*6)
s.get_range('F2:K13').conditional_formats.add_color_scale({'minColor':'#FBE7E5','midColor':'#FCF3D3','maxColor':'#CFEBE0'})
s=sheet('Threshold Sensitivity',['Tactic ID','Tactic','Threshold','Selected Function codes','Selected Function names','Count'],assigned,[15,28,15,35,52,12])
s=sheet('Function Details',['Tactic ID','Tactic','Function','Tactic population','Distinct linked','Not linked','Coverage (%)','Evidence paths','Mapped any Function'],coverage,[15,28,14,18,17,15,17,17,20])
s=sheet('Unmapped Techniques',['Tactic ID','Tactic','Technique ID','Technique','Sub-technique?'],missing,[15,28,18,45,17])
s=sheet('Methods & Audit',['Field','Value'],[
 ['Input ATT&CK','ICS STIX v19.2; prior extraction techniques.csv'],
 ['Input mappings','csf_evidence_paths.csv generated from MITRE mitigation labels and uploaded NIST draft crosswalk'],
 ['Distinct techniques',len(techniques)],['Distinct tactic-technique memberships',sum(map(len,by_tactic.values()))],
 ['Evidence path rows',len(evidence)],['Unique mapped tactic-technique memberships',len(set((r['Tactic ID'],r['Technique ID']) for r in evidence))],
 ['CSF functions with no mapped evidence','RS (Respond)'],
 ['Coverage formula','Distinct technique IDs linked to a Function / all technique IDs belonging to tactic'],
 ['Denominator policy','All active parent and sub-technique records; multi-tactic techniques counted in each tactic'],
 ['Numerator policy','A technique is counted once per tactic and Function, regardless of number of evidence paths'],
 ['Missing evidence','No eligible evidence path does NOT establish absence of relevant control'],
 ['Thresholds','25%, 50%, 75%; coverage >= cutoff; no rounding used for inclusion'],
 ['Source control normalization','MITRE AC-3 normalized with crosswalk AC-03; based on prior bridge script'],
 ['Rev 4','Not converted in existing evidence file; unmatched mappings not assigned'],
 ['Crosswalk quality','NIST crosswalk filename marked DRAFT; verify publication authority'],
 ['IEC','Not used to generate these numbers; independent completeness audit pending'],
 ['Interpretation','Association coverage, NOT proven mitigation efficacy, regulatory obligations, or ontology validation'],
 ['Parent/sub-technique dependency','Sub-techniques and parents overlap hierarchically; sensitivity check recommended'],
 ['25% assigned tactic/Function pairs',counts[25]],['50% assigned pairs',counts[50]],['75% assigned pairs',counts[75]]
 ],[39,112])
SpreadsheetFile.export_xlsx(wb).save(str(P/'ICS_v19_2_CSF2_Function_Coverage_Thresholds.xlsx'))
with open(P/'ICS_v19_2_CSF2_Function_Coverage_Audit.json','w') as fh:json.dump({'tactics':12,'unique_techniques':len(techniques),'tactic_memberships':sum(map(len,by_tactic.values())),'evidence_paths':len(evidence),'assigned_pairs_by_threshold':counts,'unmapped_tactic_technique_memberships':len(missing),'denominator':'all active parent and subtechnique tactic memberships','numerator':'distinct technique ids per tactic and function','crosswalk':'draft status not verified'},fh,indent=2)
