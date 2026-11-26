"""C02-R2: synthetic-only evidence, HOLD provenance and portable seal gates."""
import hashlib
import json
import sqlite3
import c02_r1 as r1


def location_ok(section, printed, physical, summary, limit):
    try:
        a, b = json.loads(printed), json.loads(physical)
        def pages(x):
            return isinstance(x, list) and all(type(i) is int and i > 0 for i in x) and len(set(x)) == len(x)
        return int(pages(a) and pages(b) and (section is None or isinstance(section, str))
                   and bool(a or b or (section or '').strip()) and isinstance(summary, str) and bool(summary.strip())
                   and (limit is None or all(i <= limit for i in b)))
    except (ValueError, TypeError):
        return 0


def digest(db, sid):
    """Natural keys and immutable evidence, not local surrogate IDs."""
    def rows(sql, params=()):
        return db.execute(sql, params).fetchall()
    version = rows('SELECT version FROM snapshot WHERE id=?', (sid,))[0][0]
    slots = rows('SELECT event,key,model,availability FROM snapshot_slot WHERE snapshot=? ORDER BY event,key,model', (sid,))
    master = [rows('SELECT queue_id,event_id,event_year FROM event ORDER BY queue_id'),
              rows('SELECT code,name FROM principle WHERE version=? ORDER BY code', (version,)),
              rows('SELECT code,principle_code,name,definition FROM attribute WHERE version=? ORDER BY code', (version,))]
    selected = rows('SELECT DISTINCT event,model,submission,eligibility_id FROM snapshot_slot WHERE snapshot=? AND availability=\'ELIGIBLE\' UNION ALL SELECT event,model,submission,decision FROM pending_trace WHERE snapshot=? ORDER BY 1,2', (sid,sid))
    records = []
    for event, model, sub, decision in selected:
        record = [event, model, rows('SELECT s.revision,s.provider_version,s.run_date,s.independence_notes,s.limitations,r.expected_sha256,r.observed_sha256,r.expected_pages,r.observed_pages,r.verification,r.locator FROM submission s JOIN source_revision r ON r.id=s.source WHERE s.id=?', (sub,)),
                  rows('SELECT a.git_ref,a.path,a.blob,a.sha256,a.kind,p.git_ref,p.path,p.blob,p.sha256 FROM submission_artifact l JOIN artifact a ON a.id=l.artifact LEFT JOIN artifact p ON p.id=a.parent WHERE l.submission=? ORDER BY a.git_ref,a.path,a.blob', (sub,))]
        for table, cols, order in [('ai_review','key,role,result,rationale,counterevidence','key'),('fact','local_id,summary,kind,limitation','local_id'),('review_fact','key,fact_id','key,fact_id'),('review_source','key,ordinal,section,printed_pages,pdf_pages,summary','key,ordinal'),('fact_source','fact_id,ordinal,section,printed_pages,pdf_pages,summary','fact_id,ordinal')]:
            record.append(rows(f'SELECT {cols} FROM {table} WHERE submission=? ORDER BY {order}', (sub,)))
        record.append(rows('SELECT e.status,e.reason,e.actor,e.at,v.validator_version,v.actor,v.at FROM eligibility e JOIN validation_run v ON v.id=e.validation_run WHERE e.id=?', (decision,)))
        record.append(rows('SELECT c.name,c.status,c.details FROM eligibility e JOIN validation_check c ON c.run=e.validation_run WHERE e.id=? ORDER BY c.name', (decision,)))
        records.append(record)
    return hashlib.sha256(json.dumps(['C02-R2',version,master,slots,records],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def connect():
    db = r1.connect()
    db.execute('PRAGMA recursive_triggers=ON')
    db.create_function('location_ok',5,location_ok)
    db.create_function('snapshot_digest',1,lambda sid:digest(db,sid))
    db.executescript("""
    CREATE TABLE pending_trace(snapshot INTEGER NOT NULL, event TEXT NOT NULL, version TEXT NOT NULL, model TEXT NOT NULL, availability TEXT NOT NULL CHECK(availability IN ('HOLD','INCOMPLETE')), submission INTEGER NOT NULL, decision INTEGER, decision_status TEXT, PRIMARY KEY(snapshot,event,model), FOREIGN KEY(snapshot,version) REFERENCES snapshot(id,version), FOREIGN KEY(submission,event,model,version) REFERENCES submission(id,event,model,version), FOREIGN KEY(decision,submission,decision_status) REFERENCES eligibility(id,submission,status), CHECK((availability='HOLD' AND decision IS NOT NULL AND decision_status IS NOT NULL AND decision_status IN ('HOLD','REJECTED')) OR (availability='INCOMPLETE' AND decision IS NULL AND decision_status IS NULL)));
    CREATE TRIGGER r2_verified BEFORE INSERT ON source_revision WHEN NEW.verification='VERIFIED' AND (NEW.expected_sha256 IS NULL OR NEW.observed_sha256 IS NULL OR NEW.expected_sha256!=NEW.observed_sha256 OR NEW.expected_pages IS NULL OR NEW.observed_pages IS NULL OR typeof(NEW.expected_pages)!='integer' OR typeof(NEW.observed_pages)!='integer' OR NEW.expected_pages!=NEW.observed_pages OR NEW.expected_pages<1) BEGIN SELECT RAISE(ABORT,'complete verified identity required'); END;
    CREATE TRIGGER r2_evidence BEFORE INSERT ON eligibility WHEN NEW.status='ELIGIBLE' BEGIN
      SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM submission_artifact l JOIN artifact a ON a.id=l.artifact WHERE l.submission=NEW.submission AND a.kind='ORIGINAL') THEN RAISE(ABORT,'original provenance missing') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM submission_artifact l JOIN artifact a ON a.id=l.artifact WHERE l.submission=NEW.submission AND a.kind='DERIVED' AND NOT EXISTS(SELECT 1 FROM submission_artifact p WHERE p.submission=l.submission AND p.artifact=a.parent)) THEN RAISE(ABORT,'derived parent not linked') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM fact f WHERE f.submission=NEW.submission AND NOT EXISTS(SELECT 1 FROM fact_source s WHERE s.submission=f.submission AND s.fact_id=f.local_id)) THEN RAISE(ABORT,'fact location missing') END;
    END;
    CREATE TRIGGER r2_seal BEFORE UPDATE OF sealed ON snapshot WHEN OLD.sealed=0 AND NEW.sealed=1 BEGIN
      SELECT CASE WHEN EXISTS(SELECT 1 FROM snapshot_slot WHERE snapshot=OLD.id GROUP BY event,model HAVING count(DISTINCT availability)>1) THEN RAISE(ABORT,'mixed availability') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM snapshot_slot s WHERE s.snapshot=OLD.id AND s.availability IN ('HOLD','INCOMPLETE') AND NOT EXISTS(SELECT 1 FROM pending_trace p WHERE p.snapshot=s.snapshot AND p.event=s.event AND p.model=s.model AND p.availability=s.availability)) THEN RAISE(ABORT,'pending provenance missing') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM pending_trace p WHERE p.snapshot=OLD.id AND (NOT EXISTS(SELECT 1 FROM snapshot_slot s WHERE s.snapshot=p.snapshot AND s.event=p.event AND s.model=p.model AND s.availability=p.availability) OR (p.availability='HOLD' AND p.decision!=(SELECT max(id) FROM eligibility WHERE submission=p.submission)) OR (p.availability='INCOMPLETE' AND EXISTS(SELECT 1 FROM eligibility WHERE submission=p.submission)))) THEN RAISE(ABORT,'stale or unmatched pending provenance') END;
    END;
    """)
    for table in ('fact_source','review_source'):
        db.execute(f"CREATE TRIGGER r2_{table}_location BEFORE INSERT ON {table} WHEN location_ok(NEW.section,NEW.printed_pages,NEW.pdf_pages,NEW.summary,(SELECT r.observed_pages FROM submission s JOIN source_revision r ON r.id=s.source WHERE s.id=NEW.submission))!=1 BEGIN SELECT RAISE(ABORT,'invalid source location'); END")
    for action in ('INSERT','UPDATE','DELETE'):
        refs = ['NEW'] if action=='INSERT' else ['OLD'] if action=='DELETE' else ['OLD','NEW']
        condition = ' OR '.join(f'(SELECT sealed FROM snapshot WHERE id={ref}.snapshot)=1' for ref in refs)
        db.execute(f"CREATE TRIGGER r2_pending_{action.lower()} BEFORE {action} ON pending_trace WHEN {condition} BEGIN SELECT RAISE(ABORT,'sealed pending trace'); END")
    # Pending INCOMPLETE submissions would otherwise be mutable after a seal.
    for table in ('ai_review','fact','review_fact','fact_source','review_source','submission_artifact'):
        db.execute(f"CREATE TRIGGER r2_{table}_pending BEFORE INSERT ON {table} WHEN EXISTS(SELECT 1 FROM pending_trace p JOIN snapshot s ON s.id=p.snapshot WHERE p.submission=NEW.submission AND s.sealed=1) BEGIN SELECT RAISE(ABORT,'sealed pending submission'); END")
    return db


def selftest():
    db=connect(); checks=[]
    def ok(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    def reject(name,sql,params=()):
        try:
            with db: db.execute(sql,params)
        except sqlite3.IntegrityError: checks.append(name)
        else: raise AssertionError(name)
    with db:
        db.execute("INSERT INTO standard VALUES('SYNTHETIC-V1')")
        db.execute("INSERT INTO principle VALUES('SYNTHETIC-V1','P','fixture')")
        db.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)',[('SYNTHETIC-V1',f'X{i:02}','P','fixture','fixture') for i in range(40)])
        db.executemany('INSERT INTO event VALUES(?,?,?)',[(f'SYNTHETIC-{i:03}',f'E{i:03}',2000) for i in range(38)])
        db.execute('INSERT INTO review_key SELECT queue_id||\'-\'||code,queue_id,version,code FROM event CROSS JOIN attribute')
        db.execute("INSERT INTO snapshot VALUES(1,'SYNTHETIC-V1','draft',0)")
    h='a'*64; key='SYNTHETIC-000-X00'
    reject('NULL observed hash',"INSERT INTO source_revision(id,event,expected_sha256,expected_pages,observed_pages,verification) VALUES(999,'SYNTHETIC-000',?,10,10,'VERIFIED')",(h,))
    reject('NULL observed page',"INSERT INTO source_revision(id,event,expected_sha256,observed_sha256,expected_pages,verification) VALUES(999,'SYNTHETIC-000',?,?,10,'VERIFIED')",(h,h))
    with db:
        for i in range(38):
            event=f'SYNTHETIC-{i:03}'; sid=i+1
            db.execute('INSERT INTO source_revision(id,event,expected_sha256,observed_sha256,expected_pages,observed_pages,verification) VALUES(?,?,?,?,10,10,\'VERIFIED\')',(sid,event,h,h))
            for j,model in enumerate(('CHATGPT','GEMINI','CLAUDE')):
                sub=i*3+j+1
                if j==2 and i==1:
                    db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,?,'MISSING',NULL,NULL,NULL FROM review_key WHERE event=?",(model,event));continue
                db.execute('INSERT INTO submission(id,event,version,model,revision,source) VALUES(?,?,\'SYNTHETIC-V1\',?,1,?)',(sub,event,model,sid))
                db.execute('INSERT INTO artifact VALUES(?,?,?,?,?,\'ORIGINAL\',NULL)',(sub,'b'*40,f'fixture/{sub}', 'c'*40,hashlib.sha256(str(sub).encode()).hexdigest()))
                if sub!=1: db.execute('INSERT INTO submission_artifact VALUES(?,?)',(sub,sub))
                db.execute("INSERT INTO ai_review SELECT ?,id,event,version,'N','미선정',NULL,NULL FROM review_key WHERE event=? AND (?!=3 OR code='X00')",(sub,event,sub))
                if sub!=3:
                    db.execute('INSERT INTO validation_run VALUES(?,?,?,?,?)',(sub,sub,'fixture','fixture','2000-01-01'))
                    for n in r1.REQUIRED: db.execute('INSERT INTO validation_check VALUES(?,?,?,NULL)',(sub,n,'PASS' if j<2 else 'HOLD'))
                if j<2:
                    if sub!=1: db.execute('INSERT INTO eligibility VALUES(?,?,?,?,?,?,?)',(sub,sub,sub,'ELIGIBLE','fixture','fixture','2000-01-01'))
                    if sub!=1: db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,?,'ELIGIBLE',?,?,'ELIGIBLE' FROM review_key WHERE event=?",(model,sub,sub,event))
                else:
                    state='INCOMPLETE' if sub==3 else 'HOLD'
                    if sub!=3: db.execute('INSERT INTO eligibility VALUES(?,?,?,?,?,?,?)',(sub,sub,sub,'HOLD','fixture','fixture','2000-01-01'))
                    db.execute('INSERT INTO snapshot_slot SELECT 1,event,version,id,?,?,NULL,NULL,NULL FROM review_key WHERE event=?',(model,state,event))
                    if sub!=3: db.execute('INSERT INTO pending_trace VALUES(1,?,\'SYNTHETIC-V1\',?,?,?,?,?)',(event,model,state,sub,sub,'HOLD'))
    reject('missing original artifact',"INSERT INTO eligibility VALUES(1,1,1,'ELIGIBLE','fixture','fixture','2000-01-01')")
    reject('invalid JSON location',"INSERT INTO review_source VALUES(1,?,1,'fixture','{}','[]','fixture')",(key,))
    reject('physical page out of range',"INSERT INTO review_source VALUES(1,?,1,'fixture','[]','[11]','fixture')",(key,))
    reject('duplicate physical pages',"INSERT INTO review_source VALUES(1,?,1,'fixture','[]','[1,1]','fixture')",(key,))
    reject('empty location',"INSERT INTO review_source VALUES(1,?,1,NULL,'[]','[]','fixture')",(key,))
    with db:
        db.execute('INSERT INTO submission_artifact VALUES(1,1)')
        db.execute("INSERT INTO fact VALUES(1,'F01','fixture','fixture',NULL)")
    reject('missing fact source',"INSERT INTO eligibility VALUES(1,1,1,'ELIGIBLE','fixture','fixture','2000-01-01')")
    with db:
        db.execute("INSERT INTO fact_source VALUES(1,'F01',1,'fixture','[1]','[2]','fixture')")
        db.execute("INSERT INTO eligibility VALUES(1,1,1,'ELIGIBLE','fixture','fixture','2000-01-01')")
        db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,'CHATGPT','ELIGIBLE',1,1,'ELIGIBLE' FROM review_key WHERE event='SYNTHETIC-000'")
    ok('4560 slots',db.execute('SELECT count(*) FROM snapshot_slot').fetchone()[0]==4560)
    reject('missing pending trace',"UPDATE snapshot SET sealed=1,fingerprint=snapshot_digest(1) WHERE id=1")
    reject('wrong pending model',"INSERT INTO pending_trace VALUES(1,'SYNTHETIC-000','SYNTHETIC-V1','CLAUDE','INCOMPLETE',1,NULL,NULL)")
    before=digest(db,1)
    with db: db.execute("INSERT INTO pending_trace VALUES(1,'SYNTHETIC-000','SYNTHETIC-V1','CLAUDE','INCOMPLETE',3,NULL,NULL)")
    ok('provenance changes digest',before!=digest(db,1))
    with db: db.execute('UPDATE snapshot SET sealed=1,fingerprint=snapshot_digest(1) WHERE id=1')
    ok('full grid seal',db.execute('SELECT sealed FROM snapshot WHERE id=1').fetchone()[0]==1)
    ok('eligible 3040',db.execute("SELECT count(*) FROM snapshot_slot WHERE availability='ELIGIBLE'").fetchone()[0]==3040)
    ok('hold 1440',db.execute("SELECT count(*) FROM snapshot_slot WHERE availability='HOLD'").fetchone()[0]==1440)
    ok('missing and incomplete 40 each',db.execute("SELECT count(*) FROM snapshot_slot WHERE availability='MISSING'").fetchone()[0]==40 and db.execute("SELECT count(*) FROM snapshot_slot WHERE availability='INCOMPLETE'").fetchone()[0]==40)
    reject('sealed pending delete',"DELETE FROM pending_trace WHERE submission=3")
    reject('sealed incomplete append',"INSERT INTO fact VALUES(3,'F01','fixture','fixture',NULL)")
    reject('replace parent',"INSERT OR REPLACE INTO event VALUES('SYNTHETIC-000','new',2000)")
    ok('digest stable',digest(db,1)==db.execute('SELECT fingerprint FROM snapshot WHERE id=1').fetchone()[0])
    ok('foreign key integrity',not db.execute('PRAGMA foreign_key_check').fetchall())
    ok('SQLite integrity',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
    print(f'PASS {len(checks)} R2 checks; SQLite {sqlite3.sqlite_version}')
    for name in checks: print('PASS',name)
    db.close()

if __name__=='__main__':
    r1.base.selftest()
    r1.selftest()
    selftest()
