"""C07 synthetic-only export prototype. Actual workbook use forbidden."""
import hashlib
import json
import re
from pathlib import Path
from artifact_tool import Blob, SpreadsheetFile

CODES=tuple(f'{p}{i}' for p,n in [('PA',3),('QA',4),('CO',4),('LA',8),('DM',3),('WE',4),('CL',4),('PI',4),('RC',2),('WP',4)] for i in range(1,n+1))
COL={'GEMINI':15,'CLAUDE':18}
ROLE=dict(D='선정',I='선정',A='판단보류',H='미선정',P='미선정',N='미선정')


def require(ok,msg):
    if not ok: raise ValueError(msg)


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def matrix(sheet,n):
    r=sheet.get_range(f'A1:AC{n+3}')
    values=r.values; formulas=r.formulas
    return [[('F',f) if isinstance(f,str) and f.startswith('=') else ('V',v) for v,f in zip(vs,fs)] for vs,fs in zip(values,formulas)]


def plan(values, records, model):
    require(model in COL,'model')
    require(len(values) in (40,1520),'fixture size')
    index={}; events={}
    for row,cells in enumerate(values,4):
        k,q,e,code=cells[0],cells[1],cells[2],cells[7]
        require(isinstance(q,str) and re.fullmatch(r'SYNTHETIC-\d{3}',q) and isinstance(e,str) and re.fullmatch(r'FIXTURE-E\d{3}',e) and code in CODES and k==q+'-'+code and k not in index,'fixture master')
        require(q not in events or events[q]==e,'event conflict');events[q]=e;index[k]=(row,q,e,code)
    require(len(set(events.values()))==len(events) and set(index)=={q+'-'+c for q in events for c in CODES},'grid completeness')
    changes=[];seen=set();groups={}
    for x in records:
        k=x['key'];require(k in index and k not in seen,'duplicate or unknown key');seen.add(k)
        row,q,e,code=index[k]
        require(x['queue_id']==q and x['event_id']==e and x['code']==code and x['model']==model,'key linkage')
        require(x['availability']=='ELIGIBLE' and isinstance(x['eligibility_ref'],str) and x['eligibility_ref'].startswith('fixture:'),'eligibility')
        groups.setdefault(q,set()).add(x['eligibility_ref'])
        require(ROLE.get(x['role'])==x['result'],'role mismatch')
        vals=[x['result'],x['rationale'],x['source']]
        require(all(type(v) is str and v.strip() and not re.match(r'^[=+\-@\t\r\n]',v.lstrip(' ')) and not re.match(r'^[=+\-@]',v.lstrip()) for v in vals),'unsafe or empty text')
        changes.append((row,k,vals))
    require(seen and all(len(refs)==1 and {q+'-'+c for c in CODES}<=seen for q,refs in groups.items()),'partial/mixed submission')
    return sorted(changes)


def export_copy(src,dest,records,model,n=1520):
    src,dest=Path(src).resolve(),Path(dest).resolve()
    require(src!=dest and not dest.exists() and src.suffix==dest.suffix=='.xlsx','new xlsx copy required')
    require(n in (40,1520),'fixture size')
    before_hash=digest(src)
    wb=SpreadsheetFile.import_xlsx(Blob.load(str(src)));sheet=wb.worksheets.get_item('통합검토')
    require(sheet.get_range('A1').values==[['SYNTHETIC_ONLY']],'fixture marker')
    before=matrix(sheet,n);changes=plan(sheet.get_range(f'A4:AC{n+3}').values,records,model)
    col=COL[model];expected=[r[:] for r in before]
    for row,key,vals in changes:
        require(all(v==('V',None) or v==('V','') for v in before[row-1][col:col+3]),'target not empty')
        sheet.get_range_by_indexes(row-1,col,1,3).values=[vals]
        expected[row-1][col:col+3]=[('V',v) for v in vals]
    require(matrix(sheet,n)==expected,'in-memory protected cells changed')
    temp=dest.with_name(dest.stem+'.partial.xlsx');require(not temp.exists(),'temporary path exists')
    try:
        SpreadsheetFile.export_xlsx(wb).save(str(temp))
        reopened=SpreadsheetFile.import_xlsx(Blob.load(str(temp)))
        require(matrix(reopened.worksheets.get_item('통합검토'),n)==expected,'roundtrip protected cells changed')
        require(digest(src)==before_hash,'source changed')
        # Publish without replacing an existing file.
        import os
        os.link(temp,dest)
    finally:
        if temp.exists(): temp.unlink()
    return dict(model=model,rows=len(changes),cells=3*len(changes),source_sha256=before_hash,copy_sha256=digest(dest),changed_keys=[k for _,k,_ in changes],approved=False,can_ship=False)
