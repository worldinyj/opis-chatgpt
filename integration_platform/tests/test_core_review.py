"""Projection contract tests on a minimal compatibility schema."""
import json,sqlite3,unittest
from core_review import detail

KEY='SYNTHETIC-900-PA1';FP='a'*64
class Tests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.create_function('snapshot_digest',1,lambda sid:FP if sid==1 else 'b'*64)
        self.db.executescript('CREATE TABLE snapshot(id, fingerprint, sealed);CREATE TABLE consensus(snapshot,key,rule_version,status,reason);CREATE TABLE expert_review(snapshot,key,revision,decision,rationale,actor,at);')
        self.add(1,FP,'EXPERT_REVIEW_REQUIRED')
    def add(self,sid,fp,status):
        with self.db:
            self.db.execute('INSERT INTO snapshot VALUES(?,?,1)',(sid,fp));self.db.execute('INSERT INTO consensus VALUES(?,?,?,?,?)',(sid,KEY,'1.0',status,json.dumps(dict(snapshot_fingerprint=fp,result=dict(key=KEY,status=status,votes=[dict(model=m,availability='ELIGIBLE') for m in ('CHATGPT','GEMINI','CLAUDE')])))))
    def tearDown(self):self.db.close()
    def test_permissions(self):
        self.assertTrue(detail(self.db,'EXPERT',KEY)['can_edit']);self.assertFalse(detail(self.db,'QA',KEY)['can_edit']);self.assertRaises(PermissionError,detail,self.db,'ANONYMOUS',KEY)
    def test_pending(self):self.add(2,'b'*64,'PENDING_INPUT');self.assertFalse(detail(self.db,'EXPERT',KEY)['can_edit'])
    def test_stale(self):
        with self.db:self.db.execute("INSERT INTO expert_review VALUES(1,?,1,'DEFERRED','fixture','fixture:expert','2000-01-01')",(KEY,))
        self.assertEqual(detail(self.db,'EXPERT',KEY)['revision'],1);self.add(2,'b'*64,'EXPERT_REVIEW_REQUIRED');self.assertTrue(detail(self.db,'EXPERT',KEY)['stale_review_required']);self.assertEqual(detail(self.db,'EXPERT',KEY)['revision'],0)
    def test_digest(self):
        with self.db:self.db.execute("UPDATE snapshot SET fingerprint=?",('c'*64,))
        self.assertRaises(ValueError,detail,self.db,'EXPERT',KEY)
    def test_real(self):self.assertRaises(ValueError,detail,self.db,'EXPERT','ROOT-001-PA1')
if __name__=='__main__':unittest.main(verbosity=2)
