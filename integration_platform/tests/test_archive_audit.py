"""Compatibility-schema tests, not a full C02/F1 execution."""
import sqlite3, tempfile, unittest
from pathlib import Path
from c09_archive_audit import *

DDL='''
CREATE TABLE submission(id INTEGER PRIMARY KEY,event TEXT,model TEXT,revision INTEGER);
CREATE TABLE artifact(id INTEGER PRIMARY KEY,git_ref TEXT,path TEXT,blob TEXT,sha256 TEXT,kind TEXT,parent INTEGER);
CREATE TABLE submission_artifact(submission INTEGER REFERENCES submission,artifact INTEGER REFERENCES artifact,PRIMARY KEY(submission,artifact));
CREATE TABLE intake_archive(id INTEGER PRIMARY KEY,scope TEXT,model TEXT,revision INTEGER,digest TEXT,payload BLOB,sidecar BLOB,outcome TEXT,UNIQUE(scope,model,revision,digest));
CREATE TABLE artifact_bytes(artifact INTEGER PRIMARY KEY REFERENCES artifact,raw BLOB NOT NULL);
CREATE TABLE intake_binding(submission INTEGER PRIMARY KEY REFERENCES submission,archive INTEGER REFERENCES intake_archive);
'''

def fixture():
    db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON');db.executescript(DDL)
    def add(scope,model,files,payload,sidecar,events,outcome='STAGED'):
        digest=sha(canonical([sha(payload),sha(sidecar) if sidecar is not None else None]))
        aid=db.execute('INSERT INTO intake_archive(scope,model,revision,digest,payload,sidecar,outcome) VALUES(?,?,1,?,?,?,?)',(scope,model,digest,payload,sidecar,outcome)).lastrowid
        for event in events:
            sid=db.execute('INSERT INTO submission(event,model,revision) VALUES(?,?,1)',(event,model)).lastrowid;db.execute('INSERT INTO intake_binding VALUES(?,?)',(sid,aid))
            prefix='fixture/baseline/v1/' if model=='CHATGPT' else f'fixture/{model}/{event}/v1/'
            for name,raw in files.items():
                old=db.execute('SELECT id FROM artifact WHERE path=?',(prefix+name,)).fetchone()
                if old: ident=old[0]
                else:
                    ident=db.execute("INSERT INTO artifact(git_ref,path,blob,sha256,kind,parent) VALUES(?,?,?,?,'ORIGINAL',NULL)",('0'*40,prefix+name,blob(raw),sha(raw))).lastrowid;db.execute('INSERT INTO artifact_bytes VALUES(?,?)',(ident,raw))
                db.execute('INSERT INTO submission_artifact VALUES(?,?)',(sid,ident))
    add('ALL38','CHATGPT',{'baseline.csv':b'fixture baseline'},b'fixture baseline',None,sorted(EVENTS))
    for e in sorted(EVENTS):
        for m in ('GEMINI','CLAUDE'):
            files={n:f'fixture {e} {m} {n}'.encode() for n in FILES};buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w') as z:
                for n,raw in files.items():z.writestr(n,raw)
            raw=buf.getvalue();sc=canonical(dict(fixture='SYNTHETIC_ONLY',queue_id='ROOT-'+e[-3:],event_id='FIXTURE-E'+e[-3:],model=m,revision=1,status='STORED',artifact_sha256={k:sha(v) for k,v in files.items()}))
            add(e,m,dict(files,**{'INTAKE_STATUS.json':sc}),raw,sc,[e])
            if e=='SYNTHETIC-900' and m=='GEMINI':
                files['report.md']=b'fixture conflicting report';buf=io.BytesIO()
                with zipfile.ZipFile(buf,'w') as z:
                    for n,content in files.items():z.writestr(n,content)
                changed=json.loads(sc);changed['artifact_sha256']={k:sha(v) for k,v in files.items()}
                add(e,m,{},buf.getvalue(),canonical(changed),[],'CONFLICT')
    db.commit();return db

class Tests(unittest.TestCase):
    def setUp(self):self.db=fixture()
    def tearDown(self):self.db.close()
    def run_audit(self,db=None):
        db=db or self.db;db.execute('BEGIN')
        try:return verify(db)
        finally:db.rollback()
    def test_full(self):self.assertEqual(self.run_audit(),dict(archives=78,staged=77,conflicts=1,bindings=114,artifacts=381,approved=False,can_ship=False))
    def test_backup(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'backup.sqlite';dest=sqlite3.connect(p);self.db.backup(dest);dest.close();restored=sqlite3.connect(p);restored.execute('PRAGMA foreign_keys=ON')
            try:self.assertEqual(self.run_audit(),self.run_audit(restored))
            finally:restored.close()
    def reject(self,sql):
        with self.db:self.db.execute(sql)
        self.assertRaises(ValueError,self.run_audit)
    def test_raw(self):self.reject("UPDATE artifact_bytes SET raw=X'00' WHERE artifact=1")
    def test_archive_hash(self):self.reject("UPDATE intake_archive SET digest='bad' WHERE id=1")
    def test_binding(self):self.reject('DELETE FROM intake_binding WHERE submission=1')
    def test_conflict_binding(self):self.reject("UPDATE intake_binding SET archive=(SELECT id FROM intake_archive WHERE outcome='CONFLICT') WHERE submission=39")
    def test_artifact_path(self):self.reject("UPDATE artifact SET path='bad' WHERE id=1")
    def test_source_identity(self):self.reject("UPDATE submission SET event='ROOT-001' WHERE id=1")
    def test_transaction(self):self.assertRaises(ValueError,verify,self.db)

if __name__=='__main__':unittest.main(verbosity=2)
