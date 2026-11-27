"""F1: reserved synthetic 38-event intake; immutable payloads, no eligibility."""
import csv, io, json, hashlib, re
from jsonschema import Draft202012Validator, FormatChecker
import c03_staging as s
import c03_r1_adapter as a
from c09_connection import connect as guarded_connect

V='SYNTHETIC-V1'
EVENTS=tuple((f'SYNTHETIC-{i:03}',f'FIXTURE-E{i:03}') for i in range(900,938))
EXTERNAL={'GEMINI','CLAUDE'}


def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()


def identity(q,e):
    s.require(type(q) is str and re.fullmatch(r'ROOT-9[0-3][0-9]',q),'reserved queue')
    pair=('SYNTHETIC-'+q[5:],e);s.require(pair in EVENTS,'reserved event');return pair[0]


def connect(standard):
    db=guarded_connect()
    db.executescript('''
    CREATE TABLE intake_archive(id INTEGER PRIMARY KEY,scope TEXT NOT NULL,model TEXT NOT NULL,revision INTEGER NOT NULL,digest TEXT NOT NULL,payload BLOB NOT NULL,sidecar BLOB,outcome TEXT NOT NULL CHECK(outcome IN ('STAGED','CONFLICT')),UNIQUE(scope,model,revision,digest));
    CREATE TABLE artifact_bytes(artifact INTEGER PRIMARY KEY REFERENCES artifact,raw BLOB NOT NULL);
    CREATE TABLE intake_binding(submission INTEGER PRIMARY KEY REFERENCES submission,archive INTEGER NOT NULL REFERENCES intake_archive);
    ''')
    for table in ('intake_archive','artifact_bytes','intake_binding'):
        for action in ('UPDATE','DELETE'):
            db.execute(f"CREATE TRIGGER f1_{table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'append only'); END")
    with db:
        db.execute('INSERT INTO standard VALUES(?)',(V,))
        names=a.names(standard)
        db.executemany('INSERT INTO principle VALUES(?,?,?)',[(V,p,p) for p in sorted({c[:2] for c in names})])
        db.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)',[(V,c,c[:2],n,'synthetic definition') for c,n in names.items()])
        db.executemany('INSERT INTO event VALUES(?,?,2000)',EVENTS)
        db.execute("INSERT INTO review_key SELECT queue_id||'-'||code,queue_id,version,code FROM event CROSS JOIN attribute")
    return db


def validate(data,sidecar,schema,standard):
    files=s.unpack(data);s.require(type(sidecar) is bytes and len(sidecar)<=65536,'sidecar size')
    j=json.loads(files['review.json'].decode('utf-8'),object_pairs_hook=s.unique)
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(j)
    q,e=j['queue_id'],j['event_id'];key=identity(q,e);model=j['model']['provider']
    source=j['source'];s.require(model in EXTERNAL and source['filename']=='SYNTHETIC_ONLY.pdf' and source['report_number']=='FIXTURE-'+q[5:] and source['reading_scope']=='SYNTHETIC_ONLY' and source['verification']=='PDF_READ_HASH_UNAVAILABLE' and source['sha256'] is None and source['pdf_page_count'] is None,'fixture source only')
    manifest=json.loads(sidecar.decode('utf-8'),object_pairs_hook=s.unique)
    rev=manifest.get('revision');s.require(type(rev) is int and rev>0,'revision')
    s.require(manifest==dict(fixture='SYNTHETIC_ONLY',queue_id=q,event_id=e,model=model,revision=rev,status='STORED',artifact_sha256={n:s.sha(b) for n,b in files.items()}),'sidecar binding')
    for n in ('report.md','validation.md'):s.require(files[n].decode('utf-8').startswith(a.MARKER),'fixture marker')
    names=a.names(standard);attrs={x['review_key']:x for x in j['attributes']};facts={x['id']:x for x in j['facts']}
    s.require(len(attrs)==40 and {x['code'] for x in attrs.values()}==set(names),'attribute grid')
    s.require(len(facts)==len(j['facts']) and all(k.startswith(model+'-F') for k in facts),'fact identity')
    seen=set()
    for k,rq,reid,c,result,why,loc in s.parse_csv(files['excel_import.csv']):
        x=attrs.get(k);s.require(x is not None and k not in seen and k==q+'-'+c and (rq,reid,c,result,why)==(q,e,x['code'],x['review_result'],x['rationale']) and x['name']==names[c],'CSV key/role/name')
        s.require(all(not s.unsafe(v) for v in (k,rq,reid,c,result,why,loc)),'formula')
        ids,refs=x['fact_ids'],x['source_refs'];s.require(bool(ids)==bool(refs) and all(f in facts for f in ids),'fact linkage')
        linked=[r for f in ids for r in facts[f]['source_refs']]
        for field in ('printed_pages','pdf_pages'):
            s.require({p for r in refs for p in r[field]}<={p for r in linked for p in r[field]},'page gap')
        s.require(all(not r['section'] or r['section'] in {z['section'] for z in linked} for r in refs),'section gap')
        s.require(loc==a.render_source(x,source['report_number']),'CSV source');seen.add(k)
    return key,rev,j,dict(files,**{'INTAKE_STATUS.json':sidecar})


def archive(db,scope,model,rev,payload,sidecar,existing):
    h=s.sha(canonical([s.sha(payload),s.sha(sidecar) if sidecar is not None else None]))
    prior=db.execute('SELECT id,outcome FROM intake_archive WHERE scope=? AND model=? AND revision=? AND digest=?',(scope,model,rev,h)).fetchone()
    if prior:return prior[0], 'NOOP' if prior[1]=='STAGED' else 'CONFLICT_QUARANTINED'
    outcome='CONFLICT' if existing else 'STAGED'
    aid=db.execute('INSERT INTO intake_archive(scope,model,revision,digest,payload,sidecar,outcome) VALUES(?,?,?,?,?,?,?)',(scope,model,rev,h,payload,sidecar,outcome)).lastrowid
    db.execute("INSERT INTO audit_event(actor,action,target,at,reason) VALUES('fixture',?,?,'2000-01-01',?)",(outcome,str(aid),h))
    return aid,'CONFLICT_QUARANTINED' if existing else 'STAGED_NOT_ELIGIBLE'


def add_submission(db,key,model,rev,archive_id,files,j,rows):
    src=db.execute("INSERT INTO source_revision(event,locator,verification) VALUES(?,'SYNTHETIC_ONLY','UNVERIFIED')",(key,)).lastrowid
    sub=db.execute('INSERT INTO submission(event,version,model,revision,source,provider_version,run_date,independence_notes,limitations) VALUES(?,?,?,?,?,?,?,?,?)',(key,V,model,rev,src,j['model']['version'] if j else None,j['model']['run_date'] if j else None,j['independence']['notes'] if j else None,json.dumps(j['limitations'],ensure_ascii=False) if j else 'baseline rationale/evidence absent')).lastrowid
    db.execute('INSERT INTO intake_binding VALUES(?,?)',(sub,archive_id))
    for name,raw in files.items():
        path=f'fixture/{model}/{key}/v{rev}/{name}' if j else f'fixture/baseline/v{rev}/{name}'
        blob=a.git_blob(raw);h=s.sha(raw)
        db.execute("INSERT OR IGNORE INTO artifact(git_ref,path,blob,sha256,kind,parent) VALUES(?,?,?,?,'ORIGINAL',NULL)",('0'*40,path,blob,h))
        aid,observed=db.execute('SELECT id,sha256 FROM artifact WHERE git_ref=? AND path=? AND blob=?',('0'*40,path,blob)).fetchone();s.require(observed==h,'artifact collision')
        db.execute('INSERT OR IGNORE INTO artifact_bytes VALUES(?,?)',(aid,raw));s.require(db.execute('SELECT raw FROM artifact_bytes WHERE artifact=?',(aid,)).fetchone()==(raw,),'byte collision')
        db.execute('INSERT INTO submission_artifact VALUES(?,?)',(sub,aid))
    def locs(table,k,refs):
        for i,r in enumerate(refs,1):db.execute(f'INSERT INTO {table} VALUES(?,?,?,?,?,?,?)',(sub,k,i,r['section'],json.dumps(r['printed_pages']),json.dumps(r['pdf_pages']),r['summary']))
    for f in j['facts'] if j else []:
        db.execute('INSERT INTO fact VALUES(?,?,?,?,?)',(sub,f['id'],f['summary'],f['kind'],f['limitation']));locs('fact_source',f['id'],f['source_refs'])
    for x in rows:
        k=key+'-'+x['code'];db.execute('INSERT INTO ai_review VALUES(?,?,?,?,?,?,?,?)',(sub,k,key,V,x['role'],x['review_result'],x.get('rationale'),x.get('counterevidence_or_limitation')))
        db.executemany('INSERT INTO review_fact VALUES(?,?,?)',[(sub,k,f) for f in x.get('fact_ids',[])]);locs('review_source',k,x.get('source_refs',[]))
    run=db.execute("INSERT INTO validation_run(submission,validator_version,actor,at) VALUES(?,'C09-F1','fixture','2000-01-01')",(sub,)).lastrowid
    db.executemany('INSERT INTO validation_check VALUES(?,?,?,?)',[(run,k,v,'synthetic only') for k,v in [('SCHEMA','PASS'),('IDENTITY','NOT_EXECUTED'),('INDEPENDENCE','NOT_EXECUTED'),('EVIDENCE','HOLD')]])


def ingest(db,data,sidecar,schema,standard):
    s.require(not db.in_transaction,'transaction');key,rev,j,files=validate(data,sidecar,schema,standard);model=j['model']['provider']
    with db:
        db.execute('BEGIN IMMEDIATE');existing=db.execute('SELECT id FROM submission WHERE event=? AND model=? AND revision=?',(key,model,rev)).fetchone()
        aid,status=archive(db,key,model,rev,data,sidecar,existing)
        if status=='STAGED_NOT_ELIGIBLE':add_submission(db,key,model,rev,aid,files,j,j['attributes'])
        return status


def baseline(db,raw,revision=1):
    s.require(not db.in_transaction and type(revision) is int and revision>0 and len(raw)<=s.LIMIT,'baseline input')
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''),strict=True));head=['review_key','queue_id','event_id','attribute_code','role','chatgpt_review_result']
    s.require(len(rows)==1521 and rows[0]==head and all(len(r)==6 for r in rows),'baseline shape')
    groups={e:{} for e,_ in EVENTS}
    for k,q,e,c,role,result in rows[1:]:
        key=identity(q,e);s.require(c in s.CODES and k==q+'-'+c and c not in groups[key] and s.ROLE.get(role)==result,'baseline key/role')
        groups[key][c]={'code':c,'role':role,'review_result':result}
    s.require(all(set(g)==set(s.CODES) for g in groups.values()),'baseline grid')
    with db:
        db.execute('BEGIN IMMEDIATE');existing=db.execute("SELECT id FROM submission WHERE model='CHATGPT' AND revision=?",(revision,)).fetchall()
        aid,status=archive(db,'ALL38','CHATGPT',revision,raw,None,existing)
        if status=='STAGED_NOT_ELIGIBLE':
            for key,g in groups.items():add_submission(db,key,'CHATGPT',revision,aid,{'baseline.csv':raw},None,g.values())
        return status
