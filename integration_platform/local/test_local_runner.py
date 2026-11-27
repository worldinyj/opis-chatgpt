"""Tests of orchestration only, using small disposable local fixtures."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run_local_suite as runner

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.repo=self.root/'repo';self.out=self.root/'report';self.out.mkdir();(self.repo/'integration_platform').mkdir(parents=True)
    def execute(self,source,expected=1):
        (self.repo/'integration_platform'/'fixture.py').write_text(source,encoding='utf-8')
        return runner.run_suite(self.repo,self.out,('TEST','fixture.py',(),(),expected),runner.environment(self.repo))
    def test_missing_dependency(self):
        r=runner.run_suite(self.repo,self.out,('TEST','fixture.py',(),('opis_impossible_dependency',),1),runner.environment(self.repo));self.assertEqual(r['status'],'BLOCKED_DEPENDENCY')
    def test_success(self):self.assertEqual(self.execute("print('Ran 1 test in 0.001s')")['status'],'PASS')
    def test_wrong_count(self):self.assertEqual(self.execute("print('Ran 0 tests in 0.001s')")['status'],'FAIL')
    def test_failure(self):self.assertEqual(self.execute("raise SystemExit(2)")['status'],'FAIL')
    def test_skip(self):self.assertEqual(self.execute("print('Ran 1 test in 0.001s\\nOK (skipped=1)')")['status'],'FAIL')
    def test_sanitize(self):
        with patch.dict(os.environ,{'OPIS_CONTRACT_FIXTURE':'bad','DJANGO_SETTINGS_MODULE':'bad','PYTHONPATH':'bad'}):
            env=runner.environment(self.repo);self.assertNotIn('OPIS_CONTRACT_FIXTURE',env);self.assertNotIn('DJANGO_SETTINGS_MODULE',env);self.assertNotEqual(env['PYTHONPATH'],'bad')
    def test_preflight_reject(self):
        with self.assertRaises(Exception):runner.preflight(self.repo)
if __name__=='__main__':unittest.main(verbosity=2)
