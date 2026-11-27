import sqlite3,tempfile,unittest
from pathlib import Path
from c09_connection import connect,reopen,submit
from c09_core_e2e import fixture
from c09_guard import install
from c04_r1_bridge import calculate

class Tests(unittest.TestCase):
    def setUp(self):
        self.db=fixture(3);install(self.db);calculate(self.db,1)
        self.fp=self.db.execute('SELECT fingerprint FROM snapshot WHERE id=1').fetchone()[0]
    def tearDown(self):self.db.close()
    def save(self,role='EXPERT',key='SYNTHETIC-001-PA1',rev=0,fp=None):
        return submit(self.db,role,'fixture:reviewer',1,key,fp or self.fp,rev,'DEFERRED','fixture reason')
    def test_default(self):
        d=connect()
        try:self.assertEqual(d.execute("SELECT count(*) FROM sqlite_master WHERE name IN ('c09_consensus_insert','c09_expert_insert')").fetchone()[0],2)
        finally:d.close()
    def test_draft_revision(self):
        a=self.save();b=self.save(rev=1);self.assertEqual(self.db.execute('SELECT supersedes,approval_state FROM expert_review WHERE id=?',(b,)).fetchone(),(a,'DRAFT'))
    def test_role(self):self.assertRaises(PermissionError,self.save,'QA')
    def test_pending(self):self.assertRaises(ValueError,self.save,key='SYNTHETIC-002-PA1')
    def test_stale(self):self.assertRaises(ValueError,self.save,fp='a'*64)
    def test_conflict(self):self.save();self.assertRaises(ValueError,self.save)
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER fail_expert_audit BEFORE INSERT ON audit_event WHEN NEW.action='EXPERT_DRAFT' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        self.assertRaises(sqlite3.IntegrityError,self.save);self.assertEqual(self.db.execute('SELECT count(*) FROM expert_review').fetchone()[0],0)
    def test_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'backup.sqlite';a=sqlite3.connect(p);self.db.backup(a);a.close();b=reopen(p)
            try:self.assertEqual(calculate(b,1),('NOOP',120));b.execute('DROP TRIGGER c09_expert_insert');b.commit()
            finally:b.close()
            self.assertRaises(ValueError,reopen,p)
if __name__=='__main__':unittest.main(verbosity=2)
