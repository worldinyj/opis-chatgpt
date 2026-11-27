import sqlite3
import tempfile
import unittest
from pathlib import Path
from c09_core_e2e import fixture,reopen
from c09_guard import install,register,expected
from c04_r1_bridge import calculate

class Tests(unittest.TestCase):
    def setUp(self):self.db=fixture(3);install(self.db)
    def tearDown(self):self.db.close()
    def test_invalid_consensus(self):
        with self.assertRaises(sqlite3.IntegrityError),self.db:self.db.execute("INSERT INTO consensus VALUES(1,'SYNTHETIC-002-PA1','1.0','INTERNAL_CONSENSUS_SELECTED',3,3,'forged')")
    def test_forged_reason(self):
        k='SYNTHETIC-000-PA1';s,n,r,_=expected(self.db,1,k)
        with self.assertRaises(sqlite3.IntegrityError),self.db:self.db.execute('INSERT INTO consensus VALUES(1,?,?,?,?,?,?)',(k,'1.0',s,n,r,'forged'))
    def test_positive_and_noop(self):
        self.assertEqual(calculate(self.db,1),('STORED_SYNTHETIC',120));self.assertEqual(calculate(self.db,1),('NOOP',120))
    def test_expert_pending(self):
        calculate(self.db,1)
        with self.assertRaises(sqlite3.IntegrityError),self.db:self.db.execute("INSERT INTO expert_review VALUES(1,1,'SYNTHETIC-002-PA1',1,'SELECTED','fixture','fixture:reviewer','2000-01-01',NULL,'DRAFT')")
    def test_expert_draft(self):
        calculate(self.db,1)
        with self.db:self.db.execute("INSERT INTO expert_review VALUES(1,1,'SYNTHETIC-001-PA1',1,'DEFERRED','fixture','fixture:reviewer','2000-01-01',NULL,'DRAFT')")
        self.assertEqual(self.db.execute('SELECT approval_state FROM expert_review').fetchone()[0],'DRAFT')
    def test_restore_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fixture.sqlite';b=sqlite3.connect(p);self.db.backup(b);b.close();r=reopen(p)
            try:
                with self.assertRaises(sqlite3.OperationalError):calculate(r,1)
                self.assertEqual(r.execute('SELECT count(*) FROM consensus').fetchone()[0],0)
                register(r);self.assertEqual(calculate(r,1),('STORED_SYNTHETIC',120))
            finally:r.close()
    def test_existing_store_rejected(self):
        d=fixture(3)
        try:calculate(d,1);self.assertRaises(ValueError,install,d)
        finally:d.close()

if __name__=='__main__':unittest.main(verbosity=2)
