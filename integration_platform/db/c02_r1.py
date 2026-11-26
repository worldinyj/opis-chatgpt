"""C02-R1 synthetic-only hardening layer; preserves original prototype."""
import hashlib, json, sqlite3
import c02_sqlite as base

REQUIRED = ('SCHEMA','IDENTITY','INDEPENDENCE','EVIDENCE')


def fingerprint(db, snapshot):
    version=db.execute('SELECT version FROM snapshot WHERE id=?',(snapshot,)).fetchone()[0]
    rows=db.execute('SELECT key,model,availability,submission,eligibility_id FROM snapshot_slot WHERE snapshot=? ORDER BY key,model',(snapshot,)).fetchall()
    return hashlib.sha256(json.dumps([version,rows],separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def connect():
    db=base.connect()
    db.create_function('snapshot_digest',1,lambda s:fingerprint(db,s))
    for table in ('event','standard','principle','attribute','review_key','source_revision','submission','submission_artifact','consensus'):
        for action in ('UPDATE','DELETE'):
            db.execute(f"CREATE TRIGGER r1_{table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'immutable parent'); END")
    for table in ('event','standard','principle','attribute','review_key'):
        db.execute(f"CREATE TRIGGER r1_{table}_insert BEFORE INSERT ON {table} WHEN EXISTS(SELECT 1 FROM snapshot WHERE sealed=1) BEGIN SELECT RAISE(ABORT,'frozen master'); END")
    for table in ('ai_review','fact','review_fact','fact_source','review_source','submission_artifact'):
        db.execute(f"CREATE TRIGGER r1_{table}_insert BEFORE INSERT ON {table} WHEN EXISTS(SELECT 1 FROM eligibility WHERE submission=NEW.submission) BEGIN SELECT RAISE(ABORT,'decided submission'); END")
    db.executescript("""
    CREATE TRIGGER r1_check_insert BEFORE INSERT ON validation_check WHEN EXISTS(SELECT 1 FROM eligibility WHERE validation_run=NEW.run) BEGIN SELECT RAISE(ABORT,'decided validation'); END;
    CREATE TRIGGER r1_snapshot_insert BEFORE INSERT ON snapshot WHEN NEW.sealed!=0 BEGIN SELECT RAISE(ABORT,'seal through update'); END;
    CREATE TRIGGER r1_artifact_insert BEFORE INSERT ON artifact WHEN length(NEW.git_ref)!=40 OR NEW.git_ref GLOB '*[^0-9a-f]*' OR NEW.blob GLOB '*[^0-9a-f]*' OR NEW.sha256 GLOB '*[^0-9a-f]*' OR NEW.kind NOT IN ('ORIGINAL','DERIVED') OR (NEW.kind='ORIGINAL' AND NEW.parent IS NOT NULL) OR (NEW.kind='DERIVED' AND NOT EXISTS(SELECT 1 FROM artifact WHERE id=NEW.parent AND kind='ORIGINAL')) BEGIN SELECT RAISE(ABORT,'invalid provenance'); END;
    CREATE TRIGGER r1_source_insert BEFORE INSERT ON source_revision WHEN (NEW.expected_sha256 IS NOT NULL AND (length(NEW.expected_sha256)!=64 OR NEW.expected_sha256 GLOB '*[^0-9a-f]*')) OR (NEW.observed_sha256 IS NOT NULL AND (length(NEW.observed_sha256)!=64 OR NEW.observed_sha256 GLOB '*[^0-9a-f]*')) BEGIN SELECT RAISE(ABORT,'invalid source hash'); END;
    CREATE TRIGGER r1_eligibility_order BEFORE INSERT ON eligibility WHEN EXISTS(SELECT 1 FROM eligibility WHERE submission=NEW.submission AND id>=NEW.id) AND NEW.id!=-1 BEGIN SELECT RAISE(ABORT,'nonmonotonic eligibility'); END;
    CREATE TRIGGER r1_eligible BEFORE INSERT ON eligibility WHEN NEW.status='ELIGIBLE' BEGIN
      SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM submission s JOIN source_revision r ON r.id=s.source WHERE s.id=NEW.submission AND r.verification='VERIFIED') THEN RAISE(ABORT,'source not verified') END;
      SELECT CASE WHEN (SELECT count(*) FROM validation_check WHERE run=NEW.validation_run AND name IN ('SCHEMA','IDENTITY','INDEPENDENCE','EVIDENCE') AND status='PASS')!=4 THEN RAISE(ABORT,'mandatory checks absent') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM ai_review a WHERE a.submission=NEW.submission AND a.role IN ('D','I') AND (NOT EXISTS(SELECT 1 FROM review_fact f WHERE f.submission=a.submission AND f.key=a.key) OR NOT EXISTS(SELECT 1 FROM review_source r WHERE r.submission=a.submission AND r.key=a.key))) THEN RAISE(ABORT,'selected evidence absent') END;
    END;
    CREATE TRIGGER r1_seal BEFORE UPDATE OF sealed ON snapshot WHEN OLD.sealed=0 AND NEW.sealed=1 BEGIN
      SELECT CASE WHEN NEW.version!=OLD.version OR NEW.id!=OLD.id THEN RAISE(ABORT,'snapshot identity') END;
      SELECT CASE WHEN (SELECT count(*) FROM attribute WHERE version=OLD.version)!=40 OR (SELECT count(*) FROM review_key WHERE version=OLD.version)!=40*(SELECT count(*) FROM event) THEN RAISE(ABORT,'incomplete master grid') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM snapshot_slot s WHERE s.snapshot=OLD.id AND s.availability='ELIGIBLE' AND s.eligibility_id!=(SELECT max(id) FROM eligibility WHERE submission=s.submission)) THEN RAISE(ABORT,'stale eligibility') END;
      SELECT CASE WHEN EXISTS(SELECT 1 FROM snapshot_slot WHERE snapshot=OLD.id GROUP BY event,model HAVING count(DISTINCT submission)>1 OR (sum(availability='ELIGIBLE')>0 AND sum(availability='ELIGIBLE')!=40)) THEN RAISE(ABORT,'mixed revision or incomplete model') END;
      SELECT CASE WHEN NEW.fingerprint!=snapshot_digest(OLD.id) THEN RAISE(ABORT,'fingerprint mismatch') END;
    END;
    CREATE TRIGGER r1_consensus_insert BEFORE INSERT ON consensus WHEN NOT EXISTS(SELECT 1 FROM snapshot s JOIN review_key k ON k.version=s.version WHERE s.id=NEW.snapshot AND s.sealed=1 AND k.id=NEW.key) BEGIN SELECT RAISE(ABORT,'unsealed or wrong key'); END;
    CREATE TRIGGER r1_expert_insert BEFORE INSERT ON expert_review BEGIN
      SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM snapshot s JOIN review_key k ON k.version=s.version WHERE s.id=NEW.snapshot AND s.sealed=1 AND k.id=NEW.key) THEN RAISE(ABORT,'unsealed or wrong key') END;
      SELECT CASE WHEN NEW.revision!=coalesce((SELECT max(revision)+1 FROM expert_review WHERE snapshot=NEW.snapshot AND key=NEW.key),1) OR (NEW.revision=1 AND NEW.supersedes IS NOT NULL) OR (NEW.revision>1 AND NOT EXISTS(SELECT 1 FROM expert_review WHERE id=NEW.supersedes AND snapshot=NEW.snapshot AND key=NEW.key AND revision=NEW.revision-1)) THEN RAISE(ABORT,'invalid revision chain') END;
    END;
    """)
    return db


def selftest():
    db=connect(); checks=[]
    def ok(name, cond):
        if not cond: raise AssertionError(name)
        checks.append(name)
    def reject(name, sql, params=()):
        try:
            with db: db.execute(sql,params)
        except sqlite3.IntegrityError: checks.append(name)
        else: raise AssertionError(name)
    with db:
        db.execute("INSERT INTO standard VALUES('SYNTHETIC-V1')")
        db.execute("INSERT INTO principle VALUES('SYNTHETIC-V1','P','fixture')")
        db.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)',[('SYNTHETIC-V1',f'X{i:02}','P','fixture','fixture') for i in range(40)])
        db.execute("INSERT INTO event VALUES('SYNTHETIC-001','E001',2000)")
        db.execute("INSERT INTO review_key SELECT queue_id||'-'||code,queue_id,version,code FROM event CROSS JOIN attribute")
        h='a'*64
        db.execute("INSERT INTO source_revision(id,event,expected_sha256,observed_sha256,expected_pages,observed_pages,verification) VALUES(1,'SYNTHETIC-001',?,?,10,10,'VERIFIED')",(h,h))
        for i,model in [(1,'CHATGPT'),(2,'GEMINI'),(3,'CLAUDE'),(4,'CHATGPT')]:
            db.execute('INSERT INTO submission(id,event,version,model,revision,source) VALUES(?,?,?,?,?,1)',(i,'SYNTHETIC-001','SYNTHETIC-V1',model,2 if i==4 else 1))
            db.execute("INSERT INTO ai_review SELECT ?,id,event,version,'N','미선정',NULL,NULL FROM review_key",(i,))
            db.execute('INSERT INTO validation_run VALUES(?,?,?,?,?)',(i,i,'fixture','fixture','2000-01-01'))
            for name in REQUIRED:
                db.execute('INSERT INTO validation_check VALUES(?,?,?,NULL)',(i,name,'FAIL' if i==3 and name=='IDENTITY' else 'PASS'))
        db.execute("INSERT INTO snapshot VALUES(1,'SYNTHETIC-V1','draft',0)")
    reject('direct sealed insert',"INSERT INTO snapshot VALUES(2,'SYNTHETIC-V1','bypass',1)")
    reject('invalid artifact hash',"INSERT INTO artifact VALUES(1,'bad','x',?,?,'ORIGINAL',NULL)",('a'*40,'a'*64))
    reject('failed validation',"INSERT INTO eligibility VALUES(3,3,3,'ELIGIBLE','fixture','fixture','2000-01-01')")
    with db:
        for i in (1,2,4): db.execute('INSERT INTO eligibility VALUES(?,?,?,?,?,?,?)',(i,i,i,'ELIGIBLE','fixture','fixture','2000-01-01'))
        db.execute("INSERT INTO eligibility VALUES(3,3,3,'HOLD','fixture','fixture','2000-01-01')")
    ok('positive eligibility',db.execute("SELECT count(*) FROM eligibility WHERE status='ELIGIBLE'").fetchone()[0]==3)
    reject('late check',"INSERT INTO validation_check VALUES(1,'LATE','PASS',NULL)")
    reject('parent mutation',"UPDATE source_revision SET locator='changed' WHERE id=1")
    reject('late fact',"INSERT INTO fact VALUES(1,'F01','late','fixture',NULL)")
    with db:
        for i,model in [(1,'CHATGPT'),(2,'GEMINI')]:
            db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,?,'ELIGIBLE',?,?,'ELIGIBLE' FROM review_key",(model,i,i))
        db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,'CLAUDE','HOLD',NULL,NULL,NULL FROM review_key")
    reject('wrong model',"UPDATE snapshot_slot SET submission=2,eligibility_id=2 WHERE model='CHATGPT'")
    reject('hold cannot vote',"UPDATE snapshot_slot SET availability='ELIGIBLE',submission=3,eligibility_id=3,eligible_status='ELIGIBLE' WHERE model='CLAUDE'")
    with db: db.execute("UPDATE snapshot_slot SET submission=4,eligibility_id=4 WHERE model='CHATGPT' AND key LIKE '%X00'")
    reject('mixed revision',"UPDATE snapshot SET sealed=1,fingerprint=snapshot_digest(1) WHERE id=1")
    with db: db.execute("UPDATE snapshot_slot SET submission=1,eligibility_id=1 WHERE model='CHATGPT'")
    reject('fingerprint mismatch',"UPDATE snapshot SET sealed=1 WHERE id=1")
    reject('unsealed consensus',"INSERT INTO consensus VALUES(1,'SYNTHETIC-001-X00','1','PENDING_INPUT',NULL,2,'fixture')")
    with db: db.execute("INSERT INTO eligibility VALUES(5,1,1,'HOLD','fixture','fixture','2000-01-02')")
    reject('stale eligibility',"UPDATE snapshot SET sealed=1,fingerprint=snapshot_digest(1) WHERE id=1")
    with db:
        db.execute("UPDATE snapshot_slot SET submission=4,eligibility_id=4 WHERE model='CHATGPT'")
        db.execute("UPDATE snapshot SET sealed=1,fingerprint=snapshot_digest(1) WHERE id=1")
    ok('sealed positive path',db.execute('SELECT sealed FROM snapshot WHERE id=1').fetchone()[0]==1)
    ok('digest exact',db.execute('SELECT fingerprint FROM snapshot WHERE id=1').fetchone()[0]==fingerprint(db,1))
    reject('master append after seal',"INSERT INTO event VALUES('SYNTHETIC-002','E002',2000)")
    with db: db.execute("INSERT INTO expert_review VALUES(1,1,'SYNTHETIC-001-X00',1,'DEFERRED','fixture','fixture','2000-01-01',NULL,'DRAFT')")
    reject('expert wrong chain',"INSERT INTO expert_review VALUES(2,1,'SYNTHETIC-001-X01',2,'DEFERRED','fixture','fixture','2000-01-01',1,'DRAFT')")
    ok('foreign key check',not db.execute('PRAGMA foreign_key_check').fetchall())
    ok('integrity check',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
    print(f'PASS {len(checks)} R1 tests; SQLite {sqlite3.sqlite_version}')
    for check in checks: print('PASS',check)
    db.close()

if __name__=='__main__':
    base.selftest()
    selftest()
