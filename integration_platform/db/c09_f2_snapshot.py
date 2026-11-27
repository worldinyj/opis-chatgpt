"""F2 synthetic explicit HOLD/REJECT decisions and mixed snapshot builder."""
import re
import c02_r2 as core
from c04_consensus import MODELS,CODES,require

V='SYNTHETIC-V1'


def decide(db,sub,role,actor,status,reason):
    if role!='QA':raise PermissionError('QA only')
    require(type(actor) is str and re.fullmatch(r'fixture:[A-Za-z0-9_-]+',actor) and type(reason) is str and 0<len(reason.strip())<=4000,'fixture decision')
    require(status in ('HOLD','REJECTED') and not db.in_transaction,'promotion prohibited in F2 intake')
    with db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT event,model,revision,version FROM submission WHERE id=?',(sub,)).fetchone()
        require(row and re.fullmatch(r'SYNTHETIC-\d{3}',row[0]) and row[3]==V,'synthetic submission')
        require(row[2]==db.execute('SELECT max(revision) FROM submission WHERE event=? AND model=?',(row[0],row[1])).fetchone()[0],'superseded revision')
        run=db.execute('SELECT max(id) FROM validation_run WHERE submission=?',(sub,)).fetchone()[0];require(run is not None,'validation required')
        old=db.execute('SELECT id,validation_run,status,reason,actor FROM eligibility WHERE submission=? ORDER BY id DESC LIMIT 1',(sub,)).fetchone()
        if old and old[1:]==(run,status,reason.strip(),actor):return old[0]
        did=db.execute("INSERT INTO eligibility(submission,validation_run,status,reason,actor,at) VALUES(?,?,?,?,?,'2000-01-01')",(sub,run,status,reason.strip(),actor)).lastrowid
        db.execute("INSERT INTO audit_event(actor,action,target,at,reason) VALUES(?,'ELIGIBILITY_DECISION',?,'2000-01-01',?)",(actor,str(did),reason.strip()))
    return did


def seal(db):
    require(not db.in_transaction,'transaction')
    with db:
        db.execute('BEGIN IMMEDIATE')
        events=db.execute('SELECT queue_id FROM event ORDER BY queue_id').fetchall();require(events and all(re.fullmatch(r'SYNTHETIC-\d{3}',e) for e, in events),'fixture master')
        sid=db.execute('INSERT INTO snapshot(version,fingerprint,sealed) VALUES(?,?,0)',(V,'draft')).lastrowid
        for e, in events:
            require({r[0] for r in db.execute('SELECT code FROM review_key WHERE event=? AND version=?',(e,V))}==set(CODES),'attribute grid')
            for m in MODELS:
                sub=db.execute('SELECT id FROM submission WHERE event=? AND version=? AND model=? ORDER BY revision DESC LIMIT 1',(e,V,m)).fetchone()
                dec=db.execute('SELECT id,status FROM eligibility WHERE submission=? ORDER BY id DESC LIMIT 1',sub).fetchone() if sub else None
                state='MISSING' if sub is None else 'INCOMPLETE' if dec is None else 'ELIGIBLE' if dec[1]=='ELIGIBLE' else 'HOLD'
                if state=='ELIGIBLE':
                    db.execute("INSERT INTO snapshot_slot SELECT ?,event,version,id,?,'ELIGIBLE',?,?,'ELIGIBLE' FROM review_key WHERE event=? AND version=?",(sid,m,sub[0],dec[0],e,V))
                else:
                    db.execute('INSERT INTO snapshot_slot SELECT ?,event,version,id,?,?,NULL,NULL,NULL FROM review_key WHERE event=? AND version=?',(sid,m,state,e,V))
                    if sub:db.execute('INSERT INTO pending_trace VALUES(?,?,?,?,?,?,?,?)',(sid,e,V,m,state,sub[0],dec[0] if dec else None,dec[1] if dec else None))
        fp=core.digest(db,sid);old=db.execute('SELECT id FROM snapshot WHERE fingerprint=? AND sealed=1',(fp,)).fetchone()
        if old:
            require(old[0]==db.execute('SELECT max(id) FROM snapshot WHERE sealed=1').fetchone()[0],'historical reactivation forbidden')
            db.execute('DELETE FROM pending_trace WHERE snapshot=?',(sid,));db.execute('DELETE FROM snapshot_slot WHERE snapshot=?',(sid,));db.execute('DELETE FROM snapshot WHERE id=?',(sid,));return old[0],'NOOP'
        db.execute('UPDATE snapshot SET fingerprint=?,sealed=1 WHERE id=?',(fp,sid))
        db.execute("INSERT INTO audit_event(actor,action,target,at,reason) VALUES('fixture','SNAPSHOT_SEALED',?,'2000-01-01',?)",(str(sid),fp))
        return sid,'SEALED'
