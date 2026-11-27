"""C09-A/B: full C02-R2 runtime + C04/C05/C08 synthetic integration tests."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
from collections import Counter
from pathlib import Path
import c02_r2 as core
from c04_r1_bridge import calculate
from c04_consensus import CODES, MODELS, ROLE, Slot
from c05_r1_groups import summarize_groups
from c08_dashboard import render

V='SYNTHETIC-V1'


def fixture(n=38, offset=0):
    db=core.connect()
    with db:
        db.execute('INSERT INTO standard VALUES(?)',(V,))
        db.executemany('INSERT INTO principle VALUES(?,?,?)',[(V,p,p) for p in sorted({c[:2] for c in CODES})])
        db.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)',[(V,c,c[:2],c,'fixture') for c in CODES])
        db.executemany('INSERT INTO event VALUES(?,?,?)',[(f'SYNTHETIC-{i:03}',f'FIXTURE-E{i:03}',2000+i%4) for i in range(n)])
        db.execute("INSERT INTO review_key SELECT queue_id||'-'||code,queue_id,version,code FROM event CROSS JOIN attribute")
        db.execute('INSERT INTO snapshot VALUES(1,?,?,0)',(V,'draft'))
        for i in range(n):
            e=f'SYNTHETIC-{i:03}';src=offset+i+1;h=hashlib.sha256(e.encode()).hexdigest()
            db.execute("INSERT INTO source_revision(id,event,expected_sha256,observed_sha256,expected_pages,observed_pages,verification) VALUES(?,?,?,?,10,10,'VERIFIED')",(src,e,h,h))
            for j,m in enumerate(MODELS):
                sub=offset+i*3+j+1
                state=('HOLD','MISSING','INCOMPLETE')[(i//3)%3] if i%3==2 and j==2 else 'ELIGIBLE'
                if state!='MISSING':
                    db.execute('INSERT INTO submission(id,event,version,model,revision,source) VALUES(?,?,?,?,1,?)',(sub,e,V,m,src))
                    db.execute("INSERT INTO artifact VALUES(?,?,?,?,?,'ORIGINAL',NULL)",(sub,'b'*40,f'fixture/{e}/{m}', 'c'*40,hashlib.sha256(f'{e}/{m}'.encode()).hexdigest()))
                    db.execute('INSERT INTO submission_artifact VALUES(?,?)',(sub,sub))
                    role='D' if i%3==0 else ('A' if j==1 else 'N')
                    keys=[(e+'-'+c,c) for c in CODES][:1 if state=='INCOMPLETE' else 40]
                    db.executemany('INSERT INTO ai_review VALUES(?,?,?,?,?,?,?,NULL)',[(sub,k,e,V,role,ROLE[role],'fixture rationale') for k,c in keys])
                    if role=='D':
                        db.execute("INSERT INTO fact VALUES(?,'F01','fixture','fixture',NULL)",(sub,))
                        db.execute("INSERT INTO fact_source VALUES(?,'F01',1,'fixture','[1]','[2]','fixture')",(sub,))
                        db.executemany("INSERT INTO review_fact VALUES(?,?,'F01')",[(sub,k) for k,c in keys])
                        db.executemany("INSERT INTO review_source VALUES(?,?,1,'fixture','[1]','[2]','fixture')",[(sub,k) for k,c in keys])
                    if state!='INCOMPLETE':
                        db.execute('INSERT INTO validation_run VALUES(?,?,?,?,?)',(sub,sub,'fixture','fixture','2000-01-01'))
                        db.executemany('INSERT INTO validation_check VALUES(?,?,?,NULL)',[(sub,name,'PASS' if state=='ELIGIBLE' else 'HOLD') for name in core.r1.REQUIRED])
                        db.execute('INSERT INTO eligibility VALUES(?,?,?,?,?,?,?)',(sub,sub,sub,state,'fixture','fixture','2000-01-01'))
                if state=='ELIGIBLE':
                    db.execute("INSERT INTO snapshot_slot SELECT 1,event,version,id,?,'ELIGIBLE',?,?,'ELIGIBLE' FROM review_key WHERE event=?",(m,sub,sub,e))
                else:
                    db.execute('INSERT INTO snapshot_slot SELECT 1,event,version,id,?,?,NULL,NULL,NULL FROM review_key WHERE event=?',(m,state,e))
                    if state in ('HOLD','INCOMPLETE'):
                        db.execute('INSERT INTO pending_trace VALUES(1,?,?,?,?,?,?,?)',(e,V,m,state,sub,sub if state=='HOLD' else None,'HOLD' if state=='HOLD' else None))
        db.execute('UPDATE snapshot SET fingerprint=snapshot_digest(1),sealed=1 WHERE id=1')
    return db


def analytics_input(db):
    meta={e:{'plant':f'FIXTURE-{int(e[-3:])%3}','year':year} for e,year in db.execute('SELECT queue_id,event_year FROM event')}
    fp=db.execute('SELECT fingerprint FROM snapshot WHERE id=1').fetchone()[0]
    ballots={}
    for k,reason in db.execute("SELECT key,reason FROM consensus WHERE snapshot=1 AND rule_version='1.0'"):
        record=json.loads(reason)
        if record['snapshot_fingerprint']!=fp or record['result']['key']!=k: raise ValueError('consensus identity')
        ballots[k]=[Slot(**s) for s in record['result']['votes']]
    return sorted(meta),ballots,meta


def reopen(path):
    db=sqlite3.connect(path,timeout=0.05)
    db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA recursive_triggers=ON')
    db.create_function('location_ok',5,core.location_ok)
    db.create_function('snapshot_digest',1,lambda sid:core.digest(db,sid))
    return db


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=fixture();cls.fp=core.digest(cls.db,1);cls.result=calculate(cls.db,1)
    @classmethod
    def tearDownClass(cls): cls.db.close()
    def test_full_core(self):
        self.assertEqual(self.result,('STORED_SYNTHETIC',1520))
        self.assertEqual(self.db.execute('SELECT count(*) FROM snapshot_slot').fetchone()[0],4560)
        self.assertEqual(dict(self.db.execute('SELECT status,count(*) FROM consensus GROUP BY status')),
            {'INTERNAL_CONSENSUS_SELECTED':520,'EXPERT_REVIEW_REQUIRED':520,'PENDING_INPUT':480})
        self.assertEqual(self.db.execute("SELECT count(*) FROM consensus WHERE status='PENDING_INPUT' AND selected_count IS NULL").fetchone()[0],480)
        self.assertEqual(self.db.execute('SELECT count(DISTINCT availability) FROM snapshot_slot').fetchone()[0],4)
    def test_noop(self):
        self.assertEqual(calculate(self.db,1),('NOOP',1520));self.assertEqual(self.db.execute('SELECT count(*) FROM audit_event').fetchone()[0],1)
    def test_analytics_dashboard(self):
        inputs=analytics_input(self.db);r=summarize_groups(*inputs)
        self.assertEqual(r['overall']['complete_keys'],1040);self.assertEqual(r['overall']['pending_keys'],480)
        self.assertIn('1,040개',render(*inputs));self.assertEqual(len(r['groups']['attribute']),40)
    def test_integrity(self):
        self.assertFalse(self.db.execute('PRAGMA foreign_key_check').fetchall());self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_immutable(self):
        for sql in ("DELETE FROM consensus", "DELETE FROM pending_trace", "UPDATE snapshot SET sealed=0", "UPDATE ai_review SET rationale='changed'"):
            with self.assertRaises(sqlite3.IntegrityError),self.db:self.db.execute(sql)
        self.assertEqual(core.digest(self.db,1),self.fp)
    def test_backup_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'backup.sqlite';b=sqlite3.connect(path);self.db.backup(b);b.close()
            r=reopen(path)
            try:
                self.assertEqual(core.digest(r,1),self.fp);self.assertEqual(calculate(r,1),('NOOP',1520))
                self.assertEqual(r.execute('PRAGMA integrity_check').fetchone()[0],'ok');self.assertFalse(r.execute('PRAGMA foreign_key_check').fetchall())
                self.assertEqual(r.execute('SELECT * FROM consensus ORDER BY key').fetchall(),self.db.execute('SELECT * FROM consensus ORDER BY key').fetchall())
            finally:r.close()
    def test_writer_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'lock.sqlite';a=sqlite3.connect(path);self.db.backup(a);a.close();a=reopen(path);b=reopen(path)
            try:
                a.execute('BEGIN IMMEDIATE')
                with self.assertRaises(sqlite3.OperationalError): calculate(b,1)
                a.rollback();self.assertEqual(calculate(b,1),('NOOP',1520))
            finally:a.close();b.close()
    def test_portable_snapshot_digest(self):
        a=fixture(3);b=fixture(3,100)
        try:self.assertEqual(core.digest(a,1),core.digest(b,1))
        finally:a.close();b.close()
    def test_atomic_rollback(self):
        db=fixture(3)
        try:
            db.execute("CREATE TRIGGER fail_c09 BEFORE INSERT ON consensus WHEN NEW.key='SYNTHETIC-002-WP4' BEGIN SELECT RAISE(ABORT,'fixture'); END")
            with self.assertRaises(sqlite3.IntegrityError):calculate(db,1)
            self.assertEqual(db.execute('SELECT count(*) FROM consensus').fetchone()[0],0);self.assertEqual(db.execute('SELECT count(*) FROM audit_event').fetchone()[0],0)
        finally:db.close()

if __name__=='__main__':unittest.main(verbosity=2)
