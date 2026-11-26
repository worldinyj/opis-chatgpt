"""C02 synthetic-only SQLite prototype. Run: python c02_sqlite.py"""
import sqlite3

DDL = """
PRAGMA foreign_keys=ON;
CREATE TABLE event(queue_id TEXT PRIMARY KEY NOT NULL, event_id TEXT NOT NULL UNIQUE, event_year INTEGER NOT NULL, CHECK(queue_id LIKE 'SYNTHETIC-%'));
CREATE TABLE standard(version TEXT PRIMARY KEY NOT NULL);
CREATE TABLE principle(version TEXT NOT NULL REFERENCES standard, code TEXT NOT NULL, name TEXT NOT NULL, PRIMARY KEY(version,code));
CREATE TABLE attribute(version TEXT NOT NULL, code TEXT NOT NULL, principle_code TEXT NOT NULL, name TEXT NOT NULL, definition TEXT NOT NULL, PRIMARY KEY(version,code), FOREIGN KEY(version,principle_code) REFERENCES principle(version,code));
CREATE TABLE review_key(id TEXT PRIMARY KEY NOT NULL, event TEXT NOT NULL REFERENCES event, version TEXT NOT NULL, code TEXT NOT NULL, UNIQUE(event,version,code), UNIQUE(id,event,version), FOREIGN KEY(version,code) REFERENCES attribute(version,code));
CREATE TABLE source_revision(id INTEGER PRIMARY KEY, event TEXT NOT NULL REFERENCES event, expected_sha256 TEXT, observed_sha256 TEXT, expected_pages INTEGER CHECK(expected_pages>0), observed_pages INTEGER CHECK(observed_pages>0), locator TEXT, verification TEXT NOT NULL CHECK(verification IN ('UNVERIFIED','VERIFIED','HOLD')), UNIQUE(id,event), CHECK(verification!='VERIFIED' OR (expected_sha256 IS NOT NULL AND expected_sha256=observed_sha256 AND expected_pages IS NOT NULL AND expected_pages=observed_pages)));
CREATE TABLE artifact(id INTEGER PRIMARY KEY, git_ref TEXT NOT NULL, path TEXT NOT NULL, blob TEXT NOT NULL, sha256 TEXT NOT NULL, kind TEXT NOT NULL, parent INTEGER REFERENCES artifact, UNIQUE(git_ref,path,blob), CHECK(length(blob)=40 AND length(sha256)=64));
CREATE TABLE submission(id INTEGER PRIMARY KEY, event TEXT NOT NULL REFERENCES event, version TEXT NOT NULL REFERENCES standard, model TEXT NOT NULL CHECK(model IN ('CHATGPT','GEMINI','CLAUDE')), revision INTEGER NOT NULL CHECK(revision>0), source INTEGER NOT NULL, provider_version TEXT, run_date TEXT, independence_notes TEXT, limitations TEXT, UNIQUE(event,model,revision), UNIQUE(id,event,version), UNIQUE(id,event,model,version), FOREIGN KEY(source,event) REFERENCES source_revision(id,event));
CREATE TABLE submission_artifact(submission INTEGER NOT NULL REFERENCES submission, artifact INTEGER NOT NULL REFERENCES artifact, PRIMARY KEY(submission,artifact));
CREATE TABLE ai_review(submission INTEGER NOT NULL, key TEXT NOT NULL, event TEXT NOT NULL, version TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('D','I','A','H','P','N')), result TEXT NOT NULL CHECK(result=CASE WHEN role IN ('D','I') THEN '선정' WHEN role='A' THEN '판단보류' ELSE '미선정' END), rationale TEXT, counterevidence TEXT, PRIMARY KEY(submission,key), FOREIGN KEY(submission,event,version) REFERENCES submission(id,event,version), FOREIGN KEY(key,event,version) REFERENCES review_key(id,event,version));
CREATE TABLE fact(submission INTEGER NOT NULL REFERENCES submission, local_id TEXT NOT NULL, summary TEXT NOT NULL, kind TEXT NOT NULL, limitation TEXT, PRIMARY KEY(submission,local_id));
CREATE TABLE review_fact(submission INTEGER NOT NULL, key TEXT NOT NULL, fact_id TEXT NOT NULL, PRIMARY KEY(submission,key,fact_id), FOREIGN KEY(submission,key) REFERENCES ai_review, FOREIGN KEY(submission,fact_id) REFERENCES fact);
CREATE TABLE fact_source(submission INTEGER NOT NULL, fact_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal>0), section TEXT, printed_pages TEXT, pdf_pages TEXT, summary TEXT NOT NULL, PRIMARY KEY(submission,fact_id,ordinal), FOREIGN KEY(submission,fact_id) REFERENCES fact);
CREATE TABLE review_source(submission INTEGER NOT NULL, key TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal>0), section TEXT, printed_pages TEXT, pdf_pages TEXT, summary TEXT NOT NULL, PRIMARY KEY(submission,key,ordinal), FOREIGN KEY(submission,key) REFERENCES ai_review);
CREATE TABLE validation_run(id INTEGER PRIMARY KEY, submission INTEGER NOT NULL REFERENCES submission, validator_version TEXT NOT NULL, actor TEXT NOT NULL, at TEXT NOT NULL, UNIQUE(id,submission));
CREATE TABLE validation_check(run INTEGER NOT NULL REFERENCES validation_run, name TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('PASS','FAIL','HOLD','NOT_EXECUTED')), details TEXT, PRIMARY KEY(run,name));
CREATE TABLE eligibility(id INTEGER PRIMARY KEY, submission INTEGER NOT NULL REFERENCES submission, validation_run INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('ELIGIBLE','HOLD','REJECTED')), reason TEXT NOT NULL, actor TEXT NOT NULL, at TEXT NOT NULL, UNIQUE(id,submission,status), FOREIGN KEY(validation_run,submission) REFERENCES validation_run(id,submission));
CREATE TABLE snapshot(id INTEGER PRIMARY KEY, version TEXT NOT NULL REFERENCES standard, fingerprint TEXT NOT NULL UNIQUE, sealed INTEGER NOT NULL DEFAULT 0 CHECK(sealed IN (0,1)), UNIQUE(id,version));
CREATE TABLE snapshot_slot(snapshot INTEGER NOT NULL, event TEXT NOT NULL, version TEXT NOT NULL, key TEXT NOT NULL, model TEXT NOT NULL CHECK(model IN ('CHATGPT','GEMINI','CLAUDE')), availability TEXT NOT NULL CHECK(availability IN ('MISSING','HOLD','ELIGIBLE','INCOMPLETE')), submission INTEGER, eligibility_id INTEGER, eligible_status TEXT, PRIMARY KEY(snapshot,key,model), FOREIGN KEY(snapshot,version) REFERENCES snapshot(id,version), FOREIGN KEY(key,event,version) REFERENCES review_key(id,event,version), FOREIGN KEY(submission,event,model,version) REFERENCES submission(id,event,model,version), FOREIGN KEY(submission,key) REFERENCES ai_review, FOREIGN KEY(eligibility_id,submission,eligible_status) REFERENCES eligibility(id,submission,status), CHECK((availability='ELIGIBLE' AND submission IS NOT NULL AND eligibility_id IS NOT NULL AND eligible_status='ELIGIBLE' AND eligible_status IS NOT NULL) OR (availability!='ELIGIBLE' AND submission IS NULL AND eligibility_id IS NULL AND eligible_status IS NULL)));
CREATE TABLE consensus(snapshot INTEGER NOT NULL REFERENCES snapshot, key TEXT NOT NULL REFERENCES review_key, rule_version TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('PENDING_INPUT','INTERNAL_CONSENSUS_SELECTED','EXPERT_REVIEW_REQUIRED')), selected_count INTEGER CHECK(selected_count BETWEEN 0 AND 3), responded_count INTEGER NOT NULL CHECK(responded_count BETWEEN 0 AND 3), reason TEXT NOT NULL, PRIMARY KEY(snapshot,key,rule_version), CHECK(selected_count IS NULL OR selected_count<=responded_count));
CREATE TABLE expert_review(id INTEGER PRIMARY KEY, snapshot INTEGER NOT NULL REFERENCES snapshot, key TEXT NOT NULL REFERENCES review_key, revision INTEGER NOT NULL CHECK(revision>0), decision TEXT NOT NULL CHECK(decision IN ('SELECTED','NOT_SELECTED','DEFERRED')), rationale TEXT NOT NULL, actor TEXT NOT NULL, at TEXT NOT NULL, supersedes INTEGER REFERENCES expert_review, approval_state TEXT NOT NULL CHECK(approval_state='DRAFT'), UNIQUE(snapshot,key,revision));
CREATE TABLE audit_event(id INTEGER PRIMARY KEY, actor TEXT NOT NULL, action TEXT NOT NULL, target TEXT NOT NULL, at TEXT NOT NULL, reason TEXT NOT NULL);
CREATE TRIGGER eligibility_complete BEFORE INSERT ON eligibility WHEN NEW.status='ELIGIBLE' BEGIN
 SELECT CASE WHEN (SELECT count(*) FROM ai_review WHERE submission=NEW.submission)!=40 THEN RAISE(ABORT,'incomplete submission') END;
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM validation_check WHERE run=NEW.validation_run AND status='PASS') OR EXISTS(SELECT 1 FROM validation_check WHERE run=NEW.validation_run AND status!='PASS') THEN RAISE(ABORT,'validation not passed') END;
END;
CREATE TRIGGER seal_snapshot BEFORE UPDATE OF sealed ON snapshot WHEN OLD.sealed=0 AND NEW.sealed=1 BEGIN
 SELECT CASE WHEN (SELECT count(*) FROM snapshot_slot WHERE snapshot=OLD.id)!=3*(SELECT count(*) FROM review_key WHERE version=OLD.version) THEN RAISE(ABORT,'incomplete slot grid') END;
END;
CREATE TRIGGER immutable_snapshot_update BEFORE UPDATE ON snapshot WHEN OLD.sealed=1 BEGIN SELECT RAISE(ABORT,'sealed snapshot'); END;
CREATE TRIGGER immutable_snapshot_delete BEFORE DELETE ON snapshot WHEN OLD.sealed=1 BEGIN SELECT RAISE(ABORT,'sealed snapshot'); END;
"""


def connect():
    db = sqlite3.connect(':memory:')
    db.executescript(DDL)
    for action in ('INSERT', 'UPDATE', 'DELETE'):
        refs = ['NEW'] if action == 'INSERT' else ['OLD'] if action == 'DELETE' else ['OLD', 'NEW']
        condition = ' OR '.join(f'(SELECT sealed FROM snapshot WHERE id={ref}.snapshot)=1' for ref in refs)
        db.execute(f"CREATE TRIGGER slot_{action.lower()} BEFORE {action} ON snapshot_slot WHEN {condition} BEGIN SELECT RAISE(ABORT,'sealed slots'); END")
    for table in ('artifact','ai_review','fact','review_fact','fact_source','review_source','validation_run','validation_check','eligibility','expert_review','audit_event'):
        for action in ('UPDATE','DELETE'):
            db.execute(f"CREATE TRIGGER {table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'append-only'); END")
    return db


def selftest():
    db = connect()
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    def reject(name, sql, params=()):
        try:
            with db:
                db.execute(sql, params)
        except sqlite3.IntegrityError:
            checks.append(name)
        else:
            raise AssertionError(name)
    def scalar(sql):
        return db.execute(sql).fetchone()[0]
    with db:
        db.execute("INSERT INTO standard VALUES('SYNTHETIC-V1')")
        db.executemany('INSERT INTO principle VALUES(?,?,?)', [('SYNTHETIC-V1',f'P{i}',f'Synthetic principle {i}') for i in range(10)])
        db.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)', [('SYNTHETIC-V1',f'X{i:02}',f'P{i//4}',f'Synthetic attribute {i}','Fixture only') for i in range(40)])
        db.executemany('INSERT INTO event VALUES(?,?,?)', [(f'SYNTHETIC-{i:03}',f'SYNTHETIC-E{i:03}',2000) for i in range(38)])
        db.execute("INSERT INTO review_key SELECT queue_id||'-'||code,queue_id,version,code FROM event CROSS JOIN attribute")
        db.execute("INSERT INTO snapshot VALUES(1,'SYNTHETIC-V1','fixture-1',0)")
    check('38 events',scalar('SELECT count(*) FROM event')==38)
    check('40 attributes',scalar('SELECT count(*) FROM attribute')==40)
    check('1520 review keys',scalar('SELECT count(*) FROM review_key')==1520)
    reject('real event rejected',"INSERT INTO event VALUES('ROOT-001','123',2000)")
    reject('duplicate event',"INSERT INTO event VALUES('SYNTHETIC-000','new',2000)")
    reject('foreign key',"INSERT INTO source_revision(id,event,verification) VALUES(1,'missing','UNVERIFIED')")
    reject('unverified identity',"INSERT INTO source_revision(id,event,verification) VALUES(1,'SYNTHETIC-000','VERIFIED')")
    reject('premature seal',"UPDATE snapshot SET sealed=1 WHERE id=1")
    with db:
        db.execute("INSERT INTO source_revision(id,event,verification) VALUES(1,'SYNTHETIC-000','UNVERIFIED')")
        db.execute("INSERT INTO submission(id,event,version,model,revision,source) VALUES(1,'SYNTHETIC-000','SYNTHETIC-V1','CHATGPT',1,1)")
        db.execute("INSERT INTO validation_run VALUES(1,1,'fixture','fixture','2000-01-01')")
        db.execute("INSERT INTO validation_check VALUES(1,'fixture','PASS',NULL)")
    reject('incomplete eligibility',"INSERT INTO eligibility VALUES(1,1,1,'ELIGIBLE','fixture','fixture','2000-01-01')")
    reject('role mismatch',"INSERT INTO ai_review VALUES(1,'SYNTHETIC-000-X00','SYNTHETIC-000','SYNTHETIC-V1','D','미선정',NULL,NULL)")
    reject('cross-event review',"INSERT INTO ai_review VALUES(1,'SYNTHETIC-001-X00','SYNTHETIC-001','SYNTHETIC-V1','N','미선정',NULL,NULL)")
    try:
        with db:
            db.execute("INSERT INTO ai_review VALUES(1,'SYNTHETIC-000-X00','SYNTHETIC-000','SYNTHETIC-V1','N','미선정',NULL,NULL)")
            db.execute("INSERT INTO ai_review VALUES(1,'SYNTHETIC-000-X00','SYNTHETIC-000','SYNTHETIC-V1','N','미선정',NULL,NULL)")
    except sqlite3.IntegrityError:
        pass
    check('atomic rollback',scalar('SELECT count(*) FROM ai_review')==0)
    with db:
        db.execute("INSERT INTO ai_review SELECT 1,id,event,version,'N','미선정',NULL,NULL FROM review_key WHERE event='SYNTHETIC-000'")
    reject('fact cross-reference',"INSERT INTO review_fact VALUES(1,'SYNTHETIC-000-X00','absent')")
    reject('append-only review',"UPDATE ai_review SET rationale='changed'")
    with db:
        for model in ('CHATGPT','GEMINI','CLAUDE'):
            db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,?,'MISSING',NULL,NULL,NULL FROM review_key",(model,))
    check('4560 explicit slots',scalar('SELECT count(*) FROM snapshot_slot')==4560)
    reject('missing cannot vote',"UPDATE snapshot_slot SET availability='ELIGIBLE' WHERE key='SYNTHETIC-000-X00'")
    with db:
        db.execute('UPDATE snapshot SET sealed=1 WHERE id=1')
    reject('sealed slots immutable',"DELETE FROM snapshot_slot WHERE snapshot=1")
    reject('sealed snapshot immutable',"UPDATE snapshot SET sealed=0 WHERE id=1")
    check('foreign key check',not db.execute('PRAGMA foreign_key_check').fetchall())
    check('integrity check',scalar('PRAGMA integrity_check')=='ok')
    print(f'PASS {len(checks)} checks; SQLite {sqlite3.sqlite_version}; synthetic only')
    for name in checks:
        print('PASS',name)
    db.close()


if __name__ == '__main__':
    selftest()
