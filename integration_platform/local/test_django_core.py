"""Actual Django HTTP/CSRF/session tests; synthetic core only."""
import os
import sqlite3
import tempfile
from pathlib import Path
os.environ.pop('OPIS_LOCAL_WORKSPACE',None)
os.environ['DJANGO_SETTINGS_MODULE']='local_settings'
import django
django.setup()
from django.contrib.auth.models import Group,User
from django.test import Client,TestCase,override_settings
from django.test.runner import DiscoverRunner
from c09_core_e2e import fixture
from c09_guard import install
from c04_r1_bridge import calculate
from c09_connection import reopen

URL='/fixture/core-review/SYNTHETIC-001-PA1/'
PENDING='/fixture/core-review/SYNTHETIC-002-PA1/'

class WebTests(TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'core.sqlite'
        db=fixture(3)
        try:
            install(db);calculate(db,1);self.fp=db.execute('SELECT fingerprint FROM snapshot WHERE id=1').fetchone()[0]
            dst=sqlite3.connect(self.path)
            try:db.backup(dst)
            finally:dst.close()
        finally:db.close()
        cfg=override_settings(OPIS_SYNTHETIC_CORE_REVIEW_ENABLED=True,OPIS_SYNTHETIC_CORE_CONNECTION_FACTORY=lambda:reopen(self.path));cfg.enable();self.addCleanup(cfg.disable)
        for role in ('EXPERT','QA'):
            group=Group.objects.create(name=role);user=User.objects.create_user(username='fixture:'+role.lower(),password='synthetic-test-password');user.groups.add(group)
        self.c=Client(enforce_csrf_checks=True)
    def login(self,role='expert'):
        self.assertTrue(self.c.login(username='fixture:'+role,password='synthetic-test-password'))
    def payload(self):return dict(snapshot=1,fingerprint=self.fp,revision=0,decision='DEFERRED',reason='fixture reason')
    def post(self,url=URL):
        self.assertEqual(self.c.get(URL).status_code,200)
        return self.c.post(url,self.payload(),HTTP_X_CSRFTOKEN=self.c.cookies['csrftoken'].value)
    def test_login_required(self):self.assertEqual(self.c.get(URL).status_code,302)
    def test_disabled(self):
        self.login()
        with override_settings(OPIS_SYNTHETIC_CORE_REVIEW_ENABLED=False):self.assertEqual(self.c.get(URL).status_code,403)
    def test_csrf(self):self.login();self.assertEqual(self.c.post(URL,self.payload()).status_code,403)
    def test_expert_revision(self):
        self.login();response=self.post();self.assertEqual(response.status_code,302);self.assertEqual(self.post().status_code,409)
        db=reopen(self.path)
        try:self.assertEqual(db.execute('SELECT decision,approval_state FROM expert_review').fetchall(),[('DEFERRED','DRAFT')])
        finally:db.close()
    def test_qa_read_only(self):
        self.login('qa');self.assertContains(self.c.get(URL),'읽기 전용');self.assertNotContains(self.c.get(URL),'초안 기록')
        # Obtain CSRF token via login form even when read-only template has no form.
        self.c.get('/accounts/login/');self.assertEqual(self.c.post(URL,self.payload(),HTTP_X_CSRFTOKEN=self.c.cookies['csrftoken'].value).status_code,403)
    def test_pending(self):self.login();self.assertNotContains(self.c.get(PENDING),'초안 기록');self.assertEqual(self.post(PENDING).status_code,409)

if __name__=='__main__':raise SystemExit(bool(DiscoverRunner(verbosity=2).run_tests(['test_django_core'])))
