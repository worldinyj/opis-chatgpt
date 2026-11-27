"""C03-R1: synthetic-only production-shape adapter and atomic pending DB bridge."""
import hashlib
import json
import re
import subprocess
import sqlite3
import csv
import io
from jsonschema import Draft202012Validator, FormatChecker
import c03_staging as stage

REF = 'fa145c17aff92e3ccf21ded05d0e85f545b0ab22'
PINS = {'standards/independent_ai_review_v1.schema.json':'01041a91f7fd2ca08806c0aa3ac84048f0747de3',
        'standards/safety_culture_40.json':'8dd238647998d31c2fa872968fe519925cd12670',
        'index/independent_source_queue_v1.json':'8336cf23bcfda080d1856d6ef5143b70e18e8235'}
Q = 'ROOT-999'  # outside the 38-case neutral queue
EVENT = 'FIXTURE-E999'
CORE_Q = 'SYNTHETIC-999'
VERSION = 'SYNTHETIC-V1'
MARKER = 'SYNTHETIC_ONLY\n'


def read_contract(repo):
    """Use actual immutable Git blobs, never working-tree files."""
    result = {}
    for path, blob in PINS.items():
        def git(*args): return subprocess.check_output(['git','-C',str(repo),*args])
        if git('rev-parse',REF+':'+path).decode().strip()!=blob:
            raise ValueError('contract pin mismatch')
        raw=git('cat-file','blob',blob)
        if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=blob:
            raise ValueError('contract byte mismatch')
        result[path]=json.loads(raw.decode('utf-8'),object_pairs_hook=stage.unique)
    return result


def names(standard):
    result={a['code']:a['name'] for p in standard['principles'] for a in p['attributes']}
    stage.require(set(result)==set(stage.CODES),'standard codes')
    return result


def render_source(a, report):
    if not a['fact_ids'] and not a['source_refs']: return stage.EMPTY
    parts=[f'보고서 {report}'] if report else []
    for loc in a['source_refs']:
        fields=[]
        if loc['section']: fields.append('절 '+loc['section'])
        if loc['printed_pages']: fields.append('인쇄쪽 '+','.join(map(str,loc['printed_pages'])))
        if loc['pdf_pages']: fields.append('PDF 물리쪽 '+','.join(map(str,loc['pdf_pages'])))
        parts.append(' / '.join(fields))
    parts.append('['+','.join(a['fact_ids'])+']')
    return '; '.join(parts)


def adapt_external(data, schema, standard):
    files=stage.unpack(data)
    j=json.loads(files['review.json'].decode('utf-8'),object_pairs_hook=stage.unique)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(j)
    # A synthetic marker alone is not sufficient: reserve an impossible queue ID and event ID.
    stage.require(j['queue_id']==Q and j['event_id']==EVENT and j['source']['filename']=='SYNTHETIC_ONLY.pdf','synthetic only')
    stage.require(j['source']['report_number']=='FIXTURE-999' and j['source']['reading_scope']=='SYNTHETIC_ONLY','fixture source')
    stage.require(j['source']['verification']=='PDF_READ_HASH_UNAVAILABLE' and j['source']['sha256'] is None and j['source']['pdf_page_count'] is None,'no PDF verification claim')
    for name in ('report.md','validation.md'):
        stage.require(files[name].decode('utf-8').startswith(MARKER),'fixture marker')
    expected=names(standard); attrs={a['review_key']:a for a in j['attributes']}; ledger={f['id']:f for f in j['facts']}
    stage.require(len(attrs)==40 and {a['code'] for a in attrs.values()}==set(expected),'40 keys')
    stage.require(len(ledger)==len(j['facts']) and all(f.startswith(j['model']['provider']+'-F') for f in ledger),'fact identity')
    seen=set()
    for key,q,e,code,result,rationale,source in stage.parse_csv(files['excel_import.csv']):
        a=attrs.get(key)
        stage.require(a is not None and key not in seen and key==Q+'-'+a['code'] and a['name']==expected[a['code']],'key/name')
        stage.require((q,e,code,result,rationale)==(Q,EVENT,a['code'],a['review_result'],a['rationale']),'CSV decision/rationale')
        stage.require(all(not stage.unsafe(v) for v in (key,q,e,code,result,rationale,source)),'formula prefix')
        ids,refs=a['fact_ids'],a['source_refs']
        stage.require(bool(ids)==bool(refs) and all(f in ledger for f in ids),'fact links')
        for field in ('printed_pages','pdf_pages'):
            linked={p for f in ids for loc in ledger[f]['source_refs'] for p in loc[field]}
            stage.require(all(p in linked for loc in refs for p in loc[field]),'ledger gap')
        sections={loc['section'] for f in ids for loc in ledger[f]['source_refs']}
        stage.require(all(not loc['section'] or loc['section'] in sections for loc in refs),'section mismatch')
        stage.require(source==render_source(a,j['source']['report_number']),'CSV source mismatch')
        seen.add(key)
    return j,files


def adapt_baseline(raw):
    """Synthetic baseline shape; absence of rationale remains NULL."""
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''),strict=True))
    head=['review_key','queue_id','event_id','attribute_code','role','chatgpt_review_result']
    stage.require(len(rows)==41 and rows[0]==head and all(len(r)==6 for r in rows),'baseline shape')
    seen=set(); out=[]
    for key,q,e,code,role,result in rows[1:]:
        stage.require(q==Q and e==EVENT and code in stage.CODES and key==Q+'-'+code and code not in seen and stage.ROLE.get(role)==result,'baseline key or role')
        seen.add(code);out.append({'key':CORE_Q+'-'+code,'role':role,'result':result,'rationale':None})
    return out


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def bridge_external(db, data, schema, standard, revision=1):
    """Caller supplies C02-R2 connection seeded with synthetic master. No eligibility decision."""
    stage.require(type(revision) is int and revision>0 and not db.in_transaction,'revision/transaction')
    j,files=adapt_external(data,schema,standard)
    model=j['model']['provider']; source=j['source']
    with db:
        db.execute('BEGIN IMMEDIATE')
        master=db.execute('SELECT event_id FROM event WHERE queue_id=?',(CORE_Q,)).fetchone()
        stage.require(master==(EVENT,),'fixture master missing')
        keys={r[0] for r in db.execute('SELECT code FROM review_key WHERE event=? AND version=?',(CORE_Q,VERSION))}
        stage.require(keys==set(stage.CODES),'fixture grid missing')
        old=db.execute('SELECT id FROM submission WHERE event=? AND model=? AND revision=?',(CORE_Q,model,revision)).fetchone()
        expected=sorted((n,stage.sha(v)) for n,v in files.items())
        if old:
            actual=db.execute('SELECT a.path,a.sha256 FROM submission_artifact l JOIN artifact a ON a.id=l.artifact WHERE l.submission=? ORDER BY a.path',(old[0],)).fetchall()
            if actual==expected:return 'NOOP'
            db.execute('INSERT INTO audit_event(actor,action,target,at,reason) VALUES(?,?,?,?,?)',('fixture','CONFLICT',str(old[0]),'2000-01-01',json.dumps(expected)))
            return 'CONFLICT_QUARANTINED'
        sid=db.execute('INSERT INTO source_revision(event,locator,verification) VALUES(?,?,?)',(CORE_Q,'SYNTHETIC_ONLY','UNVERIFIED')).lastrowid
        sub=db.execute('INSERT INTO submission(event,version,model,revision,source,provider_version,run_date,independence_notes,limitations) VALUES(?,?,?,?,?,?,?,?,?)',(CORE_Q,VERSION,model,revision,sid,j['model']['version'],j['model']['run_date'],j['independence']['notes'],json.dumps(j['limitations'],ensure_ascii=False))).lastrowid
        for name,raw in files.items():
            blob=git_blob(raw);h=stage.sha(raw)
            # All-zero ref is a reserved synthetic sentinel, never a real Git claim.
            db.execute('INSERT OR IGNORE INTO artifact(git_ref,path,blob,sha256,kind,parent) VALUES(?,?,?,?,?,NULL)',('0'*40,name,blob,h,'ORIGINAL'))
            aid,observed=db.execute('SELECT id,sha256 FROM artifact WHERE git_ref=? AND path=? AND blob=?',('0'*40,name,blob)).fetchone()
            stage.require(observed==h,'artifact hash conflict')
            db.execute('INSERT INTO submission_artifact VALUES(?,?)',(sub,aid))
        def locs(table,key,refs):
            for ordinal,loc in enumerate(refs,1):
                db.execute(f'INSERT INTO {table} VALUES(?,?,?,?,?,?,?)',(sub,key,ordinal,loc['section'],json.dumps(loc['printed_pages']),json.dumps(loc['pdf_pages']),loc['summary']))
        for f in j['facts']:
            db.execute('INSERT INTO fact VALUES(?,?,?,?,?)',(sub,f['id'],f['summary'],f['kind'],f['limitation']))
            locs('fact_source',f['id'],f['source_refs'])
        for a in j['attributes']:
            key=CORE_Q+'-'+a['code']
            db.execute('INSERT INTO ai_review VALUES(?,?,?,?,?,?,?,?)',(sub,key,CORE_Q,VERSION,a['role'],a['review_result'],a['rationale'],a['counterevidence_or_limitation']))
            db.executemany('INSERT INTO review_fact VALUES(?,?,?)',[(sub,key,f) for f in a['fact_ids']])
            locs('review_source',key,a['source_refs'])
        run=db.execute('INSERT INTO validation_run(submission,validator_version,actor,at) VALUES(?,?,?,?)',(sub,'C03-R1','fixture','2000-01-01')).lastrowid
        db.executemany('INSERT INTO validation_check VALUES(?,?,?,?)',[(run,'SCHEMA','PASS','synthetic production shape'),(run,'IDENTITY','NOT_EXECUTED','no real PDF'),(run,'INDEPENDENCE','NOT_EXECUTED','synthetic'),(run,'EVIDENCE','HOLD','semantic review not executed')])
        db.execute('INSERT INTO audit_event(actor,action,target,at,reason) VALUES(?,?,?,?,?)',('fixture','STAGED',str(sub),'2000-01-01','NOT_ELIGIBLE'))
    return 'STAGED_NOT_ELIGIBLE'
