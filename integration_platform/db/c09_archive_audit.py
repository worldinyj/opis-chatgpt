"""Read-only verification of F1 synthetic archive and its bindings."""
import hashlib, io, json, re, stat, zipfile

FILES={'report.md','review.json','excel_import.csv','validation.md'}
LIMIT=2_000_000
EVENTS={f'SYNTHETIC-{i}' for i in range(900,938)}


def sha(raw): return hashlib.sha256(raw).hexdigest()
def blob(raw): return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def require(ok,message):
    if not ok: raise ValueError(message)
def unique(pairs):
    result={}
    for k,v in pairs:
        require(k not in result,'duplicate JSON key');result[k]=v
    return result


def payload_files(scope,model,rev,payload,sidecar):
    require(type(payload) is bytes and len(payload)<=LIMIT,'payload size')
    require(type(rev) is int and rev>0,'revision')
    if model=='CHATGPT':
        require(scope=='ALL38' and sidecar is None,'baseline scope')
        return {'baseline.csv':payload}
    require(scope in EVENTS and model in ('GEMINI','CLAUDE') and type(sidecar) is bytes and len(sidecar)<=65536,'synthetic scope')
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        entries=z.infolist()
        require(len(entries)==4 and {i.filename for i in entries}==FILES and sum(i.file_size for i in entries)<=LIMIT,'ZIP set/size')
        require(all(stat.S_IFMT(i.external_attr>>16) in (0,stat.S_IFREG) and not i.is_dir() and not i.flag_bits&1 and i.compress_type in (0,8) for i in entries),'ZIP entry type')
        files={i.filename:z.read(i) for i in entries}
    expected=dict(fixture='SYNTHETIC_ONLY',queue_id='ROOT-'+scope[-3:],event_id='FIXTURE-E'+scope[-3:],model=model,revision=rev,status='STORED',artifact_sha256={k:sha(v) for k,v in files.items()})
    require(json.loads(sidecar.decode('utf-8'),object_pairs_hook=unique)==expected,'sidecar binding')
    return dict(files,**{'INTAKE_STATUS.json':sidecar})


def verify(db):
    """Caller must use a consistent read transaction; does not certify approval."""
    require(db.in_transaction,'consistent read transaction required')
    require(db.execute('PRAGMA integrity_check').fetchone()==('ok',) and not db.execute('PRAGMA foreign_key_check').fetchall(),'SQLite integrity')
    archive_count=staged=conflicts=bindings=0;seen_artifacts=set()
    for aid,scope,model,rev,digest,payload,sidecar,outcome in db.execute('SELECT id,scope,model,revision,digest,payload,sidecar,outcome FROM intake_archive ORDER BY id'):
        archive_count+=1
        require(digest==sha(canonical([sha(payload),sha(sidecar) if sidecar is not None else None])),'archive digest')
        files=payload_files(scope,model,rev,payload,sidecar)
        subs=db.execute('SELECT s.id,s.event,s.model,s.revision FROM intake_binding b JOIN submission s ON s.id=b.submission WHERE b.archive=?',(aid,)).fetchall()
        if outcome=='CONFLICT':
            require(not subs,'conflict linked to active submission')
            require(db.execute("SELECT count(*) FROM intake_archive WHERE scope=? AND model=? AND revision=? AND outcome='STAGED' AND digest<>?",(scope,model,rev,digest)).fetchone()==(1,),'conflict without distinct staged archive')
            conflicts+=1;continue
        require(outcome=='STAGED','archive outcome');staged+=1
        expected_events=EVENTS if model=='CHATGPT' else {scope}
        require(len(subs)==len(expected_events) and {r[1] for r in subs}==expected_events and all(r[2:]==(model,rev) for r in subs),'submission binding')
        for sid,event,_,_ in subs:
            bindings+=1
            rows=db.execute('SELECT a.id,a.path,a.blob,a.sha256,a.git_ref,a.kind,a.parent,b.raw FROM submission_artifact l JOIN artifact a ON a.id=l.artifact LEFT JOIN artifact_bytes b ON b.artifact=a.id WHERE l.submission=?',(sid,)).fetchall()
            prefix=f'fixture/baseline/v{rev}/' if model=='CHATGPT' else f'fixture/{model}/{event}/v{rev}/'
            require(len(rows)==len(files) and {r[1] for r in rows}=={prefix+n for n in files},'artifact set')
            for ident,path,b,h,ref,kind,parent,raw in rows:
                require(type(raw) is bytes and raw==files[path[len(prefix):]] and (b,h)==(blob(raw),sha(raw)) and ref=='0'*40 and kind=='ORIGINAL' and parent is None,'artifact bytes/provenance')
                seen_artifacts.add(ident)
    require(bindings==db.execute('SELECT count(*) FROM submission').fetchone()[0]==db.execute('SELECT count(*) FROM intake_binding').fetchone()[0],'unbound submission')
    require(seen_artifacts=={r[0] for r in db.execute('SELECT id FROM artifact')}=={r[0] for r in db.execute('SELECT artifact FROM artifact_bytes')},'unbound artifact')
    return dict(archives=archive_count,staged=staged,conflicts=conflicts,bindings=bindings,artifacts=len(seen_artifacts),approved=False,can_ship=False)
