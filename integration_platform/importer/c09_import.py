"""Synthetic baseline bridge and pending snapshot builder; no eligibility promotion."""
import json
import c03_r1_adapter as a
import c03_staging as stage
from c04_consensus import MODELS


def baseline(db,raw,revision=1):
    stage.require(type(revision) is int and revision>0 and not db.in_transaction,'revision/transaction')
    rows=a.adapt_baseline(raw);h=stage.sha(raw);blob=a.git_blob(raw)
    with db:
        db.execute('BEGIN IMMEDIATE')
        stage.require(db.execute('SELECT event_id FROM event WHERE queue_id=?',(a.CORE_Q,)).fetchone()==(a.EVENT,),'fixture master')
        old=db.execute("SELECT id FROM submission WHERE event=? AND model='CHATGPT' AND revision=?",(a.CORE_Q,revision)).fetchone()
        if old:
            found=db.execute('SELECT a.path,a.sha256 FROM artifact a JOIN submission_artifact l ON a.id=l.artifact WHERE l.submission=?',(old[0],)).fetchall()
            if found==[('baseline.csv',h)]:return 'NOOP'
            db.execute("INSERT INTO audit_event(actor,action,target,at,reason) VALUES('fixture','CONFLICT',?,'2000-01-01',?)",(str(old[0]),h))
            return 'CONFLICT_QUARANTINED'
        src=db.execute("INSERT INTO source_revision(event,locator,verification) VALUES(?,'SYNTHETIC_ONLY','UNVERIFIED')",(a.CORE_Q,)).lastrowid
        sub=db.execute("INSERT INTO submission(event,version,model,revision,source,limitations) VALUES(?,?,'CHATGPT',?,?,?)",(a.CORE_Q,a.VERSION,revision,src,'baseline has no rationale or evidence')).lastrowid
        db.execute("INSERT OR IGNORE INTO artifact(git_ref,path,blob,sha256,kind,parent) VALUES(?,'baseline.csv',?,?,'ORIGINAL',NULL)",('0'*40,blob,h))
        aid,observed=db.execute("SELECT id,sha256 FROM artifact WHERE git_ref=? AND path='baseline.csv' AND blob=?",('0'*40,blob)).fetchone();stage.require(observed==h,'artifact conflict')
        db.execute('INSERT INTO submission_artifact VALUES(?,?)',(sub,aid))
        db.executemany('INSERT INTO ai_review VALUES(?,?,?,?,?,?,NULL,NULL)',[(sub,r['key'],a.CORE_Q,a.VERSION,r['role'],r['result']) for r in rows])
        run=db.execute("INSERT INTO validation_run(submission,validator_version,actor,at) VALUES(?,'C09-C','fixture','2000-01-01')",(sub,)).lastrowid
        db.executemany('INSERT INTO validation_check VALUES(?,?,?,?)',[(run,k,v,'synthetic baseline') for k,v in [('SCHEMA','PASS'),('IDENTITY','NOT_EXECUTED'),('INDEPENDENCE','NOT_EXECUTED'),('EVIDENCE','HOLD')]])
        db.execute("INSERT INTO audit_event(actor,action,target,at,reason) VALUES('fixture','STAGED',?,'2000-01-01','NOT_ELIGIBLE')",(str(sub),))
    return 'STAGED_NOT_ELIGIBLE'


def seal_pending(db):
    stage.require(not db.in_transaction,'transaction')
    with db:
        db.execute('BEGIN IMMEDIATE')
        stage.require(db.execute('SELECT queue_id,event_id FROM event').fetchall()==[(a.CORE_Q,a.EVENT)],'synthetic master only')
        stage.require(db.execute('SELECT count(*) FROM eligibility').fetchone()[0]==0,'decisions not supported by pending builder')
        sid=db.execute('INSERT INTO snapshot(version,fingerprint,sealed) VALUES(?,?,0)',(a.VERSION,'draft')).lastrowid
        for model in MODELS:
            sub=db.execute('SELECT id FROM submission WHERE event=? AND version=? AND model=? ORDER BY revision DESC LIMIT 1',(a.CORE_Q,a.VERSION,model)).fetchone()
            state='INCOMPLETE' if sub else 'MISSING'
            db.execute('INSERT INTO snapshot_slot SELECT ?,event,version,id,?,?,NULL,NULL,NULL FROM review_key WHERE event=?',(sid,model,state,a.CORE_Q))
            if sub:db.execute('INSERT INTO pending_trace VALUES(?,?,?,?,?,?,NULL,NULL)',(sid,a.CORE_Q,a.VERSION,model,state,sub[0]))
        db.execute('UPDATE snapshot SET fingerprint=snapshot_digest(id),sealed=1 WHERE id=?',(sid,))
    return sid
