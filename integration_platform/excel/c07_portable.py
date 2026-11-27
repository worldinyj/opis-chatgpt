"""Read-only XLSX transfer planner. Standard library only; synthetic scope.
Does not modify or create a workbook; JSON plan is not an approval or edit.
"""
import argparse
import hashlib
import io
import json
import posixpath
import re
import stat
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
CODES=tuple(f'{p}{i}' for p,n in [('PA',3),('QA',4),('CO',4),('LA',8),('DM',3),('WE',4),('CL',4),('PI',4),('RC',2),('WP',4)] for i in range(1,n+1))
COLS={'GEMINI':('P','Q','R'),'CLAUDE':('S','T','U')}
ROLE=dict(D='선정',I='선정',A='판단보류',H='미선정',P='미선정',N='미선정')
FIELDS={'key','queue_id','event_id','code','model','availability','eligibility_ref','role','result','rationale','source'}
LIMIT=32_000_000


def require(ok,message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def canonical(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def unique(pairs):
    out={}
    for k,v in pairs:
        require(k not in out,'duplicate JSON key');out[k]=v
    return out


def xml(raw):
    # Fail closed on non-UTF8/DOCTYPE/entity declarations; no entity expansion.
    text=raw.decode('utf-8-sig')
    require('\x00' not in text and not re.search(r'<!\s*(DOCTYPE|ENTITY)',text,re.I),'unsafe XML')
    return ET.fromstring(text)


def text_of(node):
    # Support plain and rich text; phonetic annotations are not cell text.
    if node is None:return ''
    runs=node.findall(f'{{{NS}}}r')
    return ''.join(n.text or '' for r in runs for n in r.findall(f'{{{NS}}}t')) if runs else ''.join(n.text or '' for n in node.findall(f'{{{NS}}}t'))


def column(name):
    n=0
    for c in name:n=n*26+ord(c)-64
    return n


def coord(addr):
    m=re.fullmatch(r'([A-Z]{1,3})([1-9][0-9]{0,6})',addr or '')
    require(m is not None,'cell address');col=column(m[1]);row=int(m[2])
    require(col<=16384 and row<=1048576,'cell bounds');return row,col


def sheet_cells(root,shared):
    require(root.tag==f'{{{NS}}}worksheet','worksheet namespace')
    require(root.find(f'{{{NS}}}sheetProtection') is None,'protected worksheet')
    data=root.find(f'{{{NS}}}sheetData');require(data is not None,'sheetData missing')
    cells={};rows=set()
    for r in data.findall(f'{{{NS}}}row'):
        rid=int(r.get('r','0'));require(rid>0 and rid not in rows,'invalid/duplicate row');rows.add(rid)
        for c in r.findall(f'{{{NS}}}c'):
            addr=c.get('r');row,col=coord(addr);require(row==rid and addr not in cells,'duplicate/mismatched cell')
            f=c.find(f'{{{NS}}}f');v=c.find(f'{{{NS}}}v');t=c.get('t','n');raw=v.text if v is not None else None
            if f is not None:
                require(not f.attrib and bool(f.text),'unsupported shared/array formula')
                value=('F',f.text)
            elif t=='s':
                require(raw is not None and re.fullmatch(r'0|[1-9][0-9]*',raw) and int(raw)<len(shared),'invalid shared string');value=('T',shared[int(raw)])
            elif t=='inlineStr':value=('T',text_of(c.find(f'{{{NS}}}is')))
            elif raw is None:value=('B',None)
            elif t=='str':value=('T',raw)
            elif t in ('n','b','e','d'):value=(t,raw)
            else:raise ValueError('unsupported cell type')
            cells[addr]=value
    merges=[]
    for m in root.findall(f'{{{NS}}}mergeCells/{{{NS}}}mergeCell'):
        ends=m.get('ref','').split(':');require(len(ends)==2,'merge range');a,b=map(coord,ends);require(a[0]<=b[0] and a[1]<=b[1],'merge range');merges.append((a,b))
    return cells,merges


def inspect_xlsx(raw):
    """Read-only bounded package inspection, not a general Excel parser."""
    require(len(raw)<=LIMIT,'XLSX size')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        entries=z.infolist();names={i.filename for i in entries}
        require(len(entries)==len(names) and len(entries)<=1000 and sum(i.file_size for i in entries)<=LIMIT,'XLSX package limit/duplicate')
        for i in entries:
            p=i.filename
            require(not p.startswith('/') and '\\' not in p and all(c not in ('','.','..') for c in p.split('/')) and not i.is_dir() and stat.S_IFMT(i.external_attr>>16) in (0,stat.S_IFREG) and not i.flag_bits&1 and i.compress_type in (0,8),'unsafe XLSX entry')
            require(not re.search(r'(^|/)(externalLinks|vbaProject\.bin|embeddings|activeX)(/|$)',p,re.I),'unsupported external/active content')
        def part(p):require(p in names,'missing part '+p);return xml(z.read(p))
        wb=part('xl/workbook.xml');rels=part('xl/_rels/workbook.xml.rels')
        require(wb.tag==f'{{{NS}}}workbook' and rels.tag==f'{{{PKG}}}Relationships','workbook namespace')
        # No external relationships anywhere, including non-target sheets.
        for p in names:
            if p.endswith('.rels'):
                require(all(x.get('TargetMode','Internal')=='Internal' for x in part(p)),'external relationship')
        sheets=[x for x in wb.findall(f'{{{NS}}}sheets/{{{NS}}}sheet') if x.get('name')=='통합검토']
        require(len(sheets)==1 and sheets[0].get('state','visible')=='visible','target sheet')
        rid=sheets[0].get(f'{{{REL}}}id');links=[x for x in rels if x.get('Id')==rid]
        require(len(links)==1 and links[0].get('Type')==REL+'/worksheet','worksheet relationship')
        target=links[0].get('Target','');path=posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'xl/'+target)
        require(re.fullmatch(r'xl/worksheets/[^/]+\.xml',path) is not None,'worksheet path')
        shared=[]
        ss=[x for x in rels if x.get('Type')==REL+'/sharedStrings']
        if ss:
            require(len(ss)==1,'shared string relationship');t=ss[0].get('Target','');sp=posixpath.normpath(t.lstrip('/') if t.startswith('/') else 'xl/'+t);require(sp=='xl/sharedStrings.xml','shared string path');shared=[text_of(x) for x in part(sp).findall(f'{{{NS}}}si')]
        cells,merges=sheet_cells(part(path),shared)
        return cells,merges


def plan(cells,merges,records,model,n=1520):
    require(model in COLS and n in (40,1520),'model/grid size')
    require(cells.get('A1')==('T','SYNTHETIC_ONLY'),'fixture marker')
    # Header names of real workbook are unknown; synthetic header contract only.
    for c,label in {'A':'review_key','B':'queue_id','C':'event_id','H':'attribute_code','P':'Gemini result','Q':'Gemini rationale','R':'Gemini source','S':'Claude result','T':'Claude rationale','U':'Claude source'}.items():
        require(cells.get(c+'3')==('T',label),'fixture header '+c)
    index={};events={}
    for row in range(4,n+4):
        fields=[cells.get(c+str(row),('B',None)) for c in ('A','B','C','H')];require(all(t=='T' for t,_ in fields),'text key required')
        k,q,e,code=[v for _,v in fields]
        require(re.fullmatch(r'SYNTHETIC-\d{3}',q) and re.fullmatch(r'FIXTURE-E\d{3}',e) and code in CODES and k==q+'-'+code and k not in index,'fixture master')
        require(q not in events or events[q]==e,'event conflict');events[q]=e;index[k]=(row,q,e,code)
    require(len(set(events.values()))==len(events) and set(index)=={q+'-'+c for q in events for c in CODES},'grid completeness')
    require(not any(coord(a)[0]>n+3 and coord(a)[1] in (1,2,3,8) and v not in (('B',None),('T','')) for a,v in cells.items()),'extra master row')
    require(isinstance(records,list) and records,'empty records');seen=set();groups={};changes=[]
    for x in records:
        require(type(x) is dict and set(x)==FIELDS and all(type(v) is str for v in x.values()),'record shape')
        k=x['key'];require(k in index and k not in seen,'duplicate/unknown key');seen.add(k)
        row,q,e,c=index[k];require((x['queue_id'],x['event_id'],x['code'],x['model'])==(q,e,c,model),'key linkage')
        ref=x['eligibility_ref'];require(x['availability']=='ELIGIBLE' and re.fullmatch(r'fixture:[A-Za-z0-9_:-]+',ref),'eligibility');groups.setdefault(q,set()).add(ref)
        require(ROLE.get(x['role'])==x['result'],'role mismatch')
        values=[x[f] for f in ('result','rationale','source')]
        for col,value in zip(COLS[model],values):
            require(value.strip() and len(value)<=32767 and not re.match(r'^[=+\-@\t\r\n]',value.lstrip(' ')) and not re.match(r'^[=+\-@]',value.lstrip()) and not any(ord(ch)<32 and ch not in '\t\n\r' for ch in value),'unsafe/empty text')
            addr=col+str(row);require(cells.get(addr,('B',None)) in (('B',None),('T','')),'target not blank')
            r,cnum=coord(addr);require(not any(a[0]<=r<=b[0] and a[1]<=cnum<=b[1] for a,b in merges),'merged target')
            changes.append({'cell':addr,'key':k,'value':value,'type':'TEXT'})
    require(all(len(refs)==1 and {q+'-'+c for c in CODES}<=seen for q,refs in groups.items()),'partial/mixed submission')
    return sorted(changes,key=lambda x:coord(x['cell']))


def create_plan(source,records,model,n=1520):
    cells,merges=inspect_xlsx(source);changes=plan(cells,merges,records,model,n)
    result=dict(version='1.0',synthetic_only=True,source_sha256=sha(source),records_sha256=sha(canonical(records)),sheet='통합검토',model=model,rows=len(changes)//3,cells=len(changes),changes=changes,approved=False,can_ship=False,workbook_modified=False)
    result['plan_sha256']=sha(canonical(result));return result



def verify_cells(before,after,changes):
    """Exact value/formula comparison on the target sheet; blank storage may differ."""
    def normalize(cells):return {k:v for k,v in cells.items() if v not in (('B',None),('T',''))}
    expected=normalize(before)
    for change in changes:
        addr=change['cell'];require(addr not in expected,'target not blank')
        expected[addr]=('T',change['value'])
    require(normalize(after)==expected,'target/protected cell mismatch')


def verify_target_sheet_copy(source,copy,records,model,n=1520):
    """Recompute expected plan, compare all target-sheet values/formulas and merges.
    Not a certification of styles, validation, charts, other sheets or formula caches.
    """
    before,merges=inspect_xlsx(source);after,new_merges=inspect_xlsx(copy)
    changes=plan(before,merges,records,model,n)
    require(merges==new_merges,'merge structure changed')
    verify_cells(before,after,changes)
    return dict(source_sha256=sha(source),copy_sha256=sha(copy),model=model,rows=len(changes)//3,cells=len(changes),target_sheet_values_formulas_verified=True,workbook_features_verified=False,approved=False,can_ship=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('records',type=Path);p.add_argument('output',type=Path);p.add_argument('--model',choices=COLS,required=True);p.add_argument('--rows',type=int,choices=(40,1520),default=1520);p.add_argument('--verify-copy',type=Path);args=p.parse_args()
    require(args.source.suffix.lower()=='.xlsx' and args.output.suffix.lower()=='.json','read XLSX, output JSON only')
    require(args.output.resolve() not in (args.source.resolve(),args.records.resolve()),'new output required')
    require(args.source.stat().st_size<=LIMIT and args.records.stat().st_size<=LIMIT,'input size')
    raw=args.source.read_bytes();records=json.loads(args.records.read_text(encoding='utf-8'),object_pairs_hook=unique)
    if args.verify_copy:
        require(args.verify_copy.suffix.lower()=='.xlsx' and args.verify_copy.resolve()!=args.source.resolve() and args.output.resolve()!=args.verify_copy.resolve() and args.verify_copy.stat().st_size<=LIMIT,'distinct XLSX copy required')
        copy=args.verify_copy.read_bytes();result=verify_target_sheet_copy(raw,copy,records,args.model,args.rows)
        require(sha(args.verify_copy.read_bytes())==result['copy_sha256'],'copy changed')
        status='TARGET_SHEET_COPY_VERIFIED'
    else:
        result=create_plan(raw,records,args.model,args.rows);status='PLAN_ONLY'
    require(sha(args.source.read_bytes())==result['source_sha256'],'source changed')
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False)
    print(f"{status} {result['rows']} rows, {result['cells']} cells; workbook unchanged")

if __name__=='__main__':main()
