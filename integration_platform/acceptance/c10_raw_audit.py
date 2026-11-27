"""Read-only C10-PRE-R1 audit of pinned registration artifacts; never imports votes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCE='8775c5ae6249cf0f8bcd70d513e3296cbb46343e'
CENSUS='65f0a7d2ca937593854f9dced404401bc579b23d'
SUMMARY='integration_platform/acceptance/C10_PRE_METADATA_CENSUS_V1.json'
NAMES=('report.md','review.json','excel_import.csv','validation.md')
LIMIT=8*1024*1024


def require(ok,message):
    if not ok: raise ValueError(message)


def sha256(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def unique(pairs):
    result={}
    for k,v in pairs:
        require(k not in result,'duplicate JSON key')
        result[k]=v
    return result


def read_json(raw):
    def invalid(_):raise ValueError('nonfinite JSON number')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=unique,parse_constant=invalid)


def git(repo,*args):
    return subprocess.check_output(['git','--no-replace-objects','--literal-pathspecs','-C',str(repo),*args],stderr=subprocess.PIPE,timeout=60)


def read_blob(repo,ref,path,expected=None):
    require(re.fullmatch(r'[0-9a-f]{40}',ref) is not None,'fixed commit required')
    require(type(path) is str and re.fullmatch(r'[A-Za-z0-9_./-]+',path) and not path.startswith('/') and all(p not in ('','.','..') for p in path.split('/')),'invalid path')
    entries=git(repo,'ls-tree','-z',ref,'--',path).split(b'\0')
    require(len(entries)==2 and entries[-1]==b'','missing or ambiguous tree path')
    metadata,name=entries[0].split(b'\t',1);mode,kind,ident=metadata.decode('ascii').split()
    require(name.decode('utf-8')==path and mode=='100644' and kind=='blob','not a regular pinned file')
    require(expected is None or ident==expected,'pinned blob mismatch')
    require(0<=int(git(repo,'cat-file','-s',ident))<=LIMIT,'file size limit')
    raw=git(repo,'cat-file','blob',ident)
    require(len(raw)<=LIMIT and blob(raw)==ident,'raw blob hash mismatch')
    require(not raw.startswith(b'version https://git-lfs.github.com/spec/v1\n'),'LFS pointer only')
    return raw


def load_census(repo):
    summary=read_json(read_blob(repo,CENSUS,SUMMARY))
    require(summary['source_ref']==SOURCE and summary['submissions']==76 and summary['approved'] is False and summary['can_ship'] is False and summary['actual_data_import'] is False,'census scope')
    expected={f'integration_platform/acceptance/c10_pre/{m}_{i:02}.json' for m in ('gemini','claude') for i in (0,8,16,24,32)}
    shards=summary['shards'];require(len(shards)==10 and {s['path'] for s in shards}==expected,'census shard set')
    records=[]
    for shard in shards:
        j=read_json(read_blob(repo,CENSUS,shard['path'],shard['blob']))
        require(j['ref']==SOURCE and j['approved'] is False and j['can_ship'] is False and j['actual_data_import'] is False and len(j['records'])==j['n']==shard['n'],'shard scope')
        records.extend(j['records'])
    require(len(records)==76 and {(r['model'],r['queue_id']) for r in records}=={(m,f'ROOT-{i:03}') for m in ('GEMINI','CLAUDE') for i in range(1,39)},'census grid')
    for model in ('GEMINI','CLAUDE'):
        require(len({r['event_id'] for r in records if r['model']==model})==38,'event uniqueness')
    require({r['queue_id']:r['event_id'] for r in records if r['model']=='GEMINI'}=={r['queue_id']:r['event_id'] for r in records if r['model']=='CLAUDE'},'cross-model identity')
    return records


def audit_record(repo,row,ref=SOURCE):
    m,q,e,rev=row['model'],row['queue_id'],row['event_id'],row['revision_path']
    require(m in ('GEMINI','CLAUDE') and re.fullmatch(r'ROOT-(?:00[1-9]|0[12][0-9]|03[0-8])',q) and re.fullmatch(r'[A-Za-z0-9-]+',e) and re.fullmatch(r'v[1-9][0-9]*',rev),'record identity')
    path=row['path'];pattern=rf'{m.lower()}/cases/[0-9]{{4}}/{re.escape(e)}/{rev}/INTAKE_STATUS\.json'
    require(re.fullmatch(pattern,path) and row['eligible'] is False and not row['issues'],'census record scope')
    raw=read_blob(repo,ref,path,row['status_blob']);status=read_json(raw)
    require((status['model'],status['queue_id'],status['event_id'],status['artifact_status'],status['integration_status'])==(m,q,e,'STORED',row['declared_integration']),'sidecar identity')
    require(all(status.get(k) is False for k in ('approved','can_ship','eligible_for_three_ai_consensus')),'sidecar flags')
    files=status['files'];pins=row['artifacts']
    require(len(files)==len(pins)==4 and {x['name'] for x in files}=={x['name'] for x in pins}==set(NAMES),'artifact set')
    records=[];base=path.rsplit('/',1)[0]
    for name in NAMES:
        item=next(x for x in files if x['name']==name);pin=next(x for x in pins if x['name']==name)
        require(pin['blob_match'] is True and item['blob']==pin['tree_blob']==pin['declared_blob'],'artifact pin')
        data=read_blob(repo,ref,base+'/'+name,pin['tree_blob']);declared=item.get('sha256');observed=sha256(data)
        state='NEW_MEASUREMENT_NO_DECLARATION' if declared is None else 'MATCH' if declared==observed else 'MISMATCH'
        records.append(dict(name=name,bytes=len(data),observed_blob=blob(data),expected_blob=pin['tree_blob'],blob_match=True,declared_sha256=declared,observed_sha256=observed,sha256_status=state))
    return dict(model=m,queue_id=q,event_id=e,status_path=path,status_blob=blob(raw),status_sha256=sha256(raw),status_bytes=len(raw),artifacts=records,eligible=False)


def summarize(records,errors):
    a=[a for r in records for a in r['artifacts']]
    result=dict(verified_submissions=len(records),artifact_blob_matches=sum(x['blob_match'] for x in a),sha256_matches=sum(x['sha256_status']=='MATCH' for x in a),sha256_new_measurements=sum(x['sha256_status']=='NEW_MEASUREMENT_NO_DECLARATION' for x in a),sha256_mismatches=sum(x['sha256_status']=='MISMATCH' for x in a),failed_submissions=len(errors))
    grid={(m,f'ROOT-{i:03}') for m in ('GEMINI','CLAUDE') for i in range(1,39)}
    complete=len(records)==76 and {(r['model'],r['queue_id']) for r in records}==grid and len(a)==304 and result['artifact_blob_matches']==304 and result['sha256_matches']+result['sha256_new_measurements']==304
    result['status']='INCOMPLETE_OR_MISMATCH' if errors or not complete else 'RAW_BYTES_MATCH_WITH_DECLARATION_GAPS' if result['sha256_new_measurements'] else 'RAW_BYTES_MATCH'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--report',type=Path,required=True);args=p.parse_args()
    repo=args.repo.resolve();out=args.report.resolve()
    require(out!=repo and repo not in out.parents and not out.exists(),'new report outside repository required')
    records=[];errors=[]
    try:
        for row in load_census(repo):
            try:records.append(audit_record(repo,row))
            except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as ex:errors.append(dict(model=row['model'],queue_id=row['queue_id'],error_type=type(ex).__name__,error=str(ex)[:500]))
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as ex:errors.append(dict(stage='CENSUS_PREFLIGHT',error_type=type(ex).__name__,error=str(ex)[:500]))
    summary=summarize(records,errors)
    report=dict(source_ref=SOURCE,census_ref=CENSUS,method='GIT_CAT_FILE_RAW_BYTES_SHA1_AND_SHA256',summary=summary,records=records,errors=errors,approved=False,can_ship=False,actual_data_import=False,acceptance_go=False)
    with out.open('x',encoding='utf-8') as file:json.dump(report,file,ensure_ascii=False,indent=2);file.write('\n')
    print(summary)
    return int(summary['status']=='INCOMPLETE_OR_MISMATCH')

if __name__=='__main__':raise SystemExit(main())
