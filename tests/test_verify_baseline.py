import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from verify_baseline import verify


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.g('init', '-q')
        self.g('config', 'user.email', 'fixture@example.invalid')
        self.g('config', 'user.name', 'Fixture')
        self.matrix = 'index/phase3c_attribute_roles_20261126_v2.csv'
        self.packet = 'cases/2000/example/review_package/EXPERT_REVIEW_PACKET_V1.json'
        self.write(self.matrix, 'queue_id,event_id,PA1,PA2\nROOT-001,EXAMPLE,D,A\n')
        self.write(self.packet, '{}\n')
        self.write('cases/2000/example/report.md', 'original\n')
        self.commit('anchor')
        anchor = self.g('rev-parse', 'HEAD')
        self.manifest = {'baseline_commit':anchor,'protected_prefixes':['cases/'],
                         'protected_paths':[self.matrix], 'reference_blobs':[{'path':self.matrix,'blob':self.g('rev-parse','HEAD:'+self.matrix)}],
                         'case_packets':[{'path':self.packet,'blob':self.g('rev-parse','HEAD:'+self.packet)}],
                         'baseline_csv':'baseline/CHATGPT_BASELINE_V1.csv',
                         'scope':{'case_count':1,'attribute_count':2,'review_rows':2,'role_counts':{'D':1,'A':1}}}
        self.write(self.manifest['baseline_csv'], 'review_key,queue_id,event_id,attribute_code,role,chatgpt_review_result\nROOT-001-PA1,ROOT-001,EXAMPLE,PA1,D,선정\nROOT-001-PA2,ROOT-001,EXAMPLE,PA2,A,판단보류\n')
        self.commit('baseline')
    def tearDown(self): self.temp.cleanup()
    def g(self,*args): return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.DEVNULL).decode().strip()
    def write(self,p,text):
        f=self.repo/p; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(text,encoding='utf-8')
    def commit(self,msg): self.g('add','-A'); self.g('commit','-qm',msg)
    def test_clean(self): self.assertEqual(verify(self.repo,self.manifest)['status'],'PASS')
    def test_external_model_addition(self):
        self.write('gemini/cases/example/report.md','fixture'); self.write('claude/cases/example/review.json','{}'); self.commit('external')
        self.assertEqual(verify(self.repo,self.manifest)['status'],'PASS')
    def test_committed_modification(self):
        self.write('cases/2000/example/report.md','changed'); self.commit('change')
        self.assertEqual(verify(self.repo,self.manifest)['status'],'FAIL')
    def test_untracked_protected(self):
        self.write('cases/new.md','changed'); self.assertEqual(verify(self.repo,self.manifest)['status'],'FAIL')
    def test_deletion(self):
        (self.repo/self.packet).unlink(); self.commit('delete'); self.assertEqual(verify(self.repo,self.manifest)['status'],'FAIL')
    def test_csv_tamper(self):
        self.write(self.manifest['baseline_csv'],'wrong\n'); self.commit('tamper'); self.assertEqual(verify(self.repo,self.manifest)['status'],'FAIL')
    def test_dirty_protected(self):
        self.write('cases/2000/example/report.md','uncommitted'); self.assertEqual(verify(self.repo,self.manifest)['status'],'FAIL')
    def test_committed_only(self):
        self.write('cases/2000/example/report.md','uncommitted'); self.assertEqual(verify(self.repo,self.manifest,check_worktree=False)['status'],'PASS')


if __name__=='__main__': unittest.main()
