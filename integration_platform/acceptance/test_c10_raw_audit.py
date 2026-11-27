"""Actual disposable Git objects; no real OPIS inputs in tests."""
import json
from pathlib import Path
import tempfile
import unittest
import c10_raw_audit as a

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.repo=Path(self.tmp.name)
        a.git(self.repo,'init','-q');a.git(self.repo,'config','user.name','fixture');a.git(self.repo,'config','user.email','fixture@example.invalid');a.git(self.repo,'config','core.autocrlf','false')
        self.base=self.repo/'gemini/cases/2000/FIXTURE-E001/v1';self.base.mkdir(parents=True)
        self.data={n:('합성 '+n+'\r\n').encode() for n in a.NAMES};self.data['report.md']+=b'\0\xff'
        for name,raw in self.data.items():(self.base/name).write_bytes(raw)
        self.status=dict(model='GEMINI',queue_id='ROOT-001',event_id='FIXTURE-E001',artifact_status='STORED',integration_status='HOLD',approved=False,can_ship=False,eligible_for_three_ai_consensus=False,files=[dict(name=n,blob=a.blob(b),sha256=a.sha256(b)) for n,b in self.data.items()])
        self.commit()
    def commit(self):
        raw=json.dumps(self.status).encode();(self.base/'INTAKE_STATUS.json').write_bytes(raw);a.git(self.repo,'add','.');a.git(self.repo,'commit','-qm','fixture','--allow-empty');self.ref=a.git(self.repo,'rev-parse','HEAD').decode().strip()
        self.row=dict(model='GEMINI',queue_id='ROOT-001',event_id='FIXTURE-E001',revision_path='v1',path='gemini/cases/2000/FIXTURE-E001/v1/INTAKE_STATUS.json',status_blob=a.blob(raw),declared_integration='HOLD',eligible=False,issues=[],artifacts=[dict(name=n,tree_blob=a.blob(b),declared_blob=a.blob(b),blob_match=True) for n,b in self.data.items()])
    def audit(self):return a.audit_record(self.repo,self.row,self.ref)
    def test_exact(self):
        result=self.audit();self.assertEqual([x['sha256_status'] for x in result['artifacts']],['MATCH']*4);self.assertEqual(result['artifacts'][0]['bytes'],len(self.data['report.md']))
    def test_worktree_not_used(self):
        (self.base/'report.md').write_bytes(b'changed');self.assertEqual(self.audit()['artifacts'][0]['observed_sha256'],a.sha256(self.data['report.md']))
    def test_missing_declaration(self):
        del self.status['files'][0]['sha256'];self.commit();self.assertEqual(self.audit()['artifacts'][0]['sha256_status'],'NEW_MEASUREMENT_NO_DECLARATION')
    def test_mismatch(self):
        self.status['files'][0]['sha256']='0'*64;self.commit();self.assertEqual(self.audit()['artifacts'][0]['sha256_status'],'MISMATCH');self.assertEqual(a.summarize([self.audit()],[])['status'],'INCOMPLETE_OR_MISMATCH')
    def test_pin(self):
        self.row['status_blob']='0'*40;self.assertRaises(ValueError,self.audit)
    def test_flag(self):
        self.status['approved']=True;self.commit();self.assertRaises(ValueError,self.audit)
    def test_path(self):
        self.row['path']='../../INTAKE_STATUS.json';self.assertRaises(ValueError,self.audit)
    def test_duplicate_json(self):self.assertRaises(ValueError,a.read_json,b'{"key":1,"key":2}')
    def test_unsafe_blob_path(self):self.assertRaises(ValueError,a.read_blob,self.repo,self.ref,'../outside')
    def test_partial_summary(self):self.assertEqual(a.summarize([self.audit()],[])['status'],'INCOMPLETE_OR_MISMATCH')
    def test_full_summary(self):
        r=self.audit();rows=[dict(r,model=m,queue_id=f'ROOT-{i:03}') for m in ('GEMINI','CLAUDE') for i in range(1,39)]
        self.assertEqual(a.summarize(rows,[])['status'],'RAW_BYTES_MATCH')
        self.assertEqual(a.summarize([r]*76,[])['status'],'INCOMPLETE_OR_MISMATCH')
        r['artifacts'][0]['sha256_status']='NEW_MEASUREMENT_NO_DECLARATION';self.assertEqual(a.summarize(rows,[])['status'],'RAW_BYTES_MATCH_WITH_DECLARATION_GAPS')

if __name__=='__main__':unittest.main(verbosity=2)
