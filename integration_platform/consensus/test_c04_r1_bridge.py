"""Core-schema compatibility harness; not the full C02-R2 trigger suite."""
import hashlib
import sqlite3
import unittest
from c04_r1_bridge import calculate
from c04_consensus import CODES, MODELS


def fixture():
    db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE event(queue_id TEXT PRIMARY KEY);
    CREATE TABLE review_key(id TEXT PRIMARY KEY,event TEXT,version TEXT,code TEXT);
    CREATE TABLE snapshot(id INTEGER PRIMARY KEY,version TEXT,fingerprint TEXT,sealed INTEGER);
    CREATE TABLE submission(id INTEGER PRIMARY KEY,event TEXT,model TEXT,version TEXT,revision INTEGER);
    CREATE TABLE eligibility(id INTEGER PRIMARY KEY,submission INTEGER,status TEXT);
    CREATE TABLE ai_review(submission INTEGER,key TEXT,event TEXT,version TEXT,role TEXT,result TEXT,PRIMARY KEY(submission,key));
    CREATE TABLE snapshot_slot(snapshot INTEGER,event TEXT,version TEXT,key TEXT,model TEXT,availability TEXT,submission INTEGER,eligibility_id INTEGER,eligible_status TEXT,PRIMARY KEY(snapshot,key,model));
    CREATE TABLE pending_trace(snapshot INTEGER,event TEXT,version TEXT,model TEXT,availability TEXT,submission INTEGER,decision INTEGER,decision_status TEXT,PRIMARY KEY(snapshot,event,model));
    CREATE TABLE consensus(snapshot INTEGER,key TEXT,rule_version TEXT,status TEXT,selected_count INTEGER,responded_count INTEGER,reason TEXT,PRIMARY KEY(snapshot,key,rule_version));
    CREATE TABLE audit_event(id INTEGER PRIMARY KEY,actor TEXT,action TEXT,target TEXT,at TEXT,reason TEXT);
    ''')
    # Harness digest deliberately not a substitute for C02-R2 portable digest.
    def digest(sid):
        return hashlib.sha256(repr([db.execute('SELECT * FROM '+t+' ORDER BY 1,2').fetchall() for t in ('submission','eligibility','ai_review','snapshot_slot','pending_trace')]).encode()).hexdigest()
    db.create_function('snapshot_digest',1,digest)
    v='SYNTHETIC-V1'
    with db:
        db.execute('INSERT INTO snapshot VALUES(1,?,\'draft\',0)',(v,))
        for i in range(3):
            e=f'SYNTHETIC-{i:03}';db.execute('INSERT INTO event VALUES(?)',(e,))
            for c in CODES:db.execute('INSERT INTO review_key VALUES(?,?,?,?)',(e+'-'+c,e,v,c))
            for j,m in enumerate(MODELS):
                sub=i*3+j+1;state='HOLD' if i==2 and j==2 else 'ELIGIBLE';role='N' if i==1 else 'D';result='미선정' if role=='N' else '선정'
                db.execute('INSERT INTO submission VALUES(?,?,?,?,1)',(sub,e,m,v));db.execute('INSERT INTO eligibility VALUES(?,?,?)',(sub,sub,state))
                if state=='HOLD':db.execute('INSERT INTO pending_trace VALUES(1,?,?,?,?,?,?,?)',(e,v,m,state,sub,sub,state))
                for c in CODES:
                    k=e+'-'+c;db.execute('INSERT INTO ai_review VALUES(?,?,?,?,?,?)',(sub,k,e,v,role,result));db.execute('INSERT INTO snapshot_slot VALUES(1,?,?,?,?,?,?,?,?)',(e,v,k,m,state,sub if state=='ELIGIBLE' else None,sub if state=='ELIGIBLE' else None,state if state=='ELIGIBLE' else None))
        db.execute('UPDATE snapshot SET fingerprint=snapshot_digest(1),sealed=1')
    return db


class Tests(unittest.TestCase):
    def setUp(self):self.db=fixture()
    def tearDown(self):self.db.close()
    def run_bridge(self):return calculate(self.db,1)
    def reseal(self):
        self.db.execute('UPDATE snapshot SET fingerprint=snapshot_digest(1)');self.db.commit()
    def test_positive(self):
        self.assertEqual(self.run_bridge(),('STORED_SYNTHETIC',120));self.assertEqual(dict(self.db.execute('SELECT status,count(*) FROM consensus GROUP BY status')),{s:40 for s in ('PENDING_INPUT','INTERNAL_CONSENSUS_SELECTED','EXPERT_REVIEW_REQUIRED')});self.assertEqual(self.db.execute("SELECT count(*) FROM consensus WHERE status='PENDING_INPUT' AND selected_count IS NULL").fetchone()[0],40)
    def test_noop(self):self.run_bridge();self.assertEqual(self.run_bridge(),('NOOP',120));self.assertEqual(self.db.execute('SELECT count(*) FROM audit_event').fetchone()[0],1)
    def test_unsealed(self):
        with self.db:self.db.execute('UPDATE snapshot SET sealed=0')
        self.assertRaises(ValueError,self.run_bridge)
    def test_digest(self):
        with self.db:self.db.execute("UPDATE snapshot SET fingerprint=?",('a'*64,))
        self.assertRaises(ValueError,self.run_bridge)
    def test_bad_link(self):
        with self.db:self.db.execute('UPDATE snapshot_slot SET eligibility_id=9 WHERE submission=1')
        self.reseal();self.assertRaises(ValueError,self.run_bridge)
    def test_pending_trace(self):
        with self.db:self.db.execute('DELETE FROM pending_trace')
        self.reseal();self.assertRaises(ValueError,self.run_bridge)
    def test_mixed(self):
        with self.db:self.db.execute("UPDATE snapshot_slot SET availability='MISSING',submission=NULL,eligibility_id=NULL,eligible_status=NULL WHERE key='SYNTHETIC-000-PA1' AND model='CHATGPT'")
        self.reseal();self.assertRaises(ValueError,self.run_bridge)
    def test_partial(self):
        self.run_bridge()
        with self.db:self.db.execute('DELETE FROM consensus WHERE key=?',('SYNTHETIC-000-PA1',))
        self.assertRaises(ValueError,self.run_bridge)
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER fail BEFORE INSERT ON consensus WHEN NEW.key='SYNTHETIC-002-WP4' BEGIN SELECT RAISE(ABORT,'forced'); END")
        self.assertRaises(sqlite3.IntegrityError,self.run_bridge);self.assertEqual(self.db.execute('SELECT count(*) FROM consensus').fetchone()[0],0);self.assertEqual(self.db.execute('SELECT count(*) FROM audit_event').fetchone()[0],0)

if __name__=='__main__':unittest.main(verbosity=2)
