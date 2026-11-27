import csv,io,json,sqlite3,unittest,os
from pathlib import Path
import c09_f1_intake as f
import c09_f2_snapshot as g
import c03_r1_adapter as a
import c03_staging as s
import c02_r2 as core
from c04_r1_bridge import calculate
from c09_core_e2e import fixture
from c09_guard import install

if os.environ.get('OPIS_CONTRACT_FIXTURE'):
    root=Path(os.environ['OPIS_CONTRACT_FIXTURE']);SCHEMA=json.loads((root/'schema.json').read_text());names=json.loads((root/'names.json').read_text())
    assert s.sha(f.canonical(SCHEMA))=='326114a38cf2dcfe07d6d2204dec47f16d5bbde6a46a81445f7d26a259798f0c'
    assert s.sha(f.canonical(names))=='b003748ae407fd953ee12727dd9862ae735238cc307c976dd286b44bc6fc42b1'
    STANDARD={'principles':[{'attributes':[{'code':c,'name':n} for c,n in group]} for group in names]}
else:
    contracts=a.read_contract(os.environ.get('OPIS_REPO','.'));SCHEMA=contracts['standards/independent_ai_review_v1.schema.json'];STANDARD=contracts['standards/safety_culture_40.json']


def packet(i=900,model='GEMINI',rev=1,role='D'):
    q=f'ROOT-{i}';e=f'FIXTURE-E{i}';loc={'section':'fixture','printed_pages':[1],'pdf_pages':[],'summary':'fixture'}
    j={'schema_version':'1.0','prompt_version':'1.0','standard_version':'1.0','queue_id':q,'event_id':e,'model':{'provider':model,'version':'fixture','run_date':'2000-01-01'},'source':{'filename':'SYNTHETIC_ONLY.pdf','report_number':f'FIXTURE-{i}','report_date':None,'sha256':None,'pdf_page_count':None,'reading_scope':'SYNTHETIC_ONLY','verification':'PDF_READ_HASH_UNAVAILABLE'},'independence':{'other_ai_outputs_seen':False,'notes':'fixture'},'facts':[{'id':model+'-F01','summary':'fixture','kind':'OBSERVED_FACT','source_refs':[loc],'limitation':'fixture'}],'attributes':[],'limitations':['fixture'],'status':'INDEPENDENT_DRAFT','approved':False,'can_ship':False}
    out=io.StringIO(newline='');w=csv.writer(out);w.writerow(s.HEADER)
    for n,(c,name) in enumerate(a.names(STANDARD).items()):
        r=role if n==0 else 'N';x={'review_key':q+'-'+c,'code':c,'name':name,'role':r,'review_result':s.ROLE[r],'rationale':'fixture rationale','fact_ids':[model+'-F01'] if n==0 else [],'source_refs':[loc] if n==0 else [],'counterevidence_or_limitation':'fixture'};j['attributes'].append(x);w.writerow([x['review_key'],q,e,c,x['review_result'],x['rationale'],a.render_source(x,f'FIXTURE-{i}')])
    files={'review.json':f.canonical(j),'excel_import.csv':out.getvalue().encode(),'report.md':b'SYNTHETIC_ONLY\nfixture','validation.md':b'SYNTHETIC_ONLY\nfixture'}
    status=f.canonical(dict(fixture='SYNTHETIC_ONLY',queue_id=q,event_id=e,model=model,revision=rev,status='STORED',artifact_sha256={k:s.sha(v) for k,v in files.items()}))
    return s.zip_bytes(files),status


def baseline(role='A'):
    out=io.StringIO(newline='');w=csv.writer(out);w.writerow(['review_key','queue_id','event_id','attribute_code','role','chatgpt_review_result'])
    for i in range(900,938):
        for c in s.CODES:w.writerow([f'ROOT-{i}-{c}',f'ROOT-{i}',f'FIXTURE-E{i}',c,role,s.ROLE[role]])
    return out.getvalue().encode()


class Tests(unittest.TestCase):
    def setUp(self):self.db=f.connect(STANDARD)
    def tearDown(self):self.db.close()
    def ingest(self,p):return f.ingest(self.db,*p,SCHEMA,STANDARD)
    def count(self,t):return self.db.execute('SELECT count(*) FROM '+t).fetchone()[0]
    def test_full(self):
        b=baseline();self.assertEqual(f.baseline(self.db,b),'STAGED_NOT_ELIGIBLE');self.assertEqual(f.baseline(self.db,b),'NOOP')
        for i in range(900,938):
            for m in ('GEMINI','CLAUDE'):
                p=packet(i,m);self.assertEqual(self.ingest(p),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.db.execute('SELECT payload,sidecar FROM intake_archive WHERE scope=? AND model=?',(f'SYNTHETIC-{i}',m)).fetchone(),p)
        self.assertEqual(self.count('submission'),114);self.assertEqual(self.count('ai_review'),4560);self.assertEqual(self.count('intake_archive'),77);self.assertEqual(self.count('intake_binding'),114);self.assertEqual(self.count('eligibility'),0);self.assertEqual(self.count('artifact_bytes'),381)
        for h,blob,raw in self.db.execute('SELECT sha256,blob,raw FROM artifact JOIN artifact_bytes ON artifact.id=artifact_bytes.artifact'):self.assertEqual((h,blob),(s.sha(raw),a.git_blob(raw)))
        sid,state=g.seal(self.db);self.assertEqual(state,'SEALED');self.assertEqual(g.seal(self.db),(sid,'NOOP'));self.assertEqual(self.count('snapshot'),1);self.assertEqual(calculate(self.db,sid),('STORED_SYNTHETIC',1520));self.assertEqual(self.db.execute("SELECT count(*) FROM consensus WHERE status='PENDING_INPUT' AND selected_count IS NULL AND responded_count=0").fetchone()[0],1520)
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok');self.assertFalse(self.db.execute('PRAGMA foreign_key_check').fetchall())
    def test_conflict(self):
        p=packet();q=packet(role='I');self.assertEqual(self.ingest(p),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.ingest(p),'NOOP');self.assertEqual(self.ingest(q),'CONFLICT_QUARANTINED');self.assertEqual(self.ingest(q),'CONFLICT_QUARANTINED');self.assertEqual(self.count('submission'),1);self.assertEqual(self.db.execute("SELECT payload,sidecar FROM intake_archive WHERE outcome='CONFLICT'").fetchone(),q)
    def test_bad_sidecar(self):
        z,status=packet();j=json.loads(status);j['artifact_sha256']['review.json']='0'*64
        self.assertRaises(ValueError,self.ingest,(z,f.canonical(j)));self.assertEqual(self.count('intake_archive'),0)
    def test_real_id(self):self.assertRaises(ValueError,self.ingest,packet(899))
    def test_baseline_conflict(self):
        self.assertEqual(f.baseline(self.db,baseline()),'STAGED_NOT_ELIGIBLE');b=baseline('N');self.assertEqual(f.baseline(self.db,b),'CONFLICT_QUARANTINED');self.assertEqual(self.count('submission'),38);self.assertEqual(self.db.execute("SELECT payload FROM intake_archive WHERE outcome='CONFLICT'").fetchone(),(b,))
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER fail_fixture BEFORE INSERT ON ai_review WHEN NEW.key LIKE '%-WP4' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        for fun in (lambda:self.ingest(packet()),lambda:f.baseline(self.db,baseline())):
            self.assertRaises(sqlite3.IntegrityError,fun);self.assertEqual(sum(self.count(t) for t in ('submission','artifact','intake_archive','artifact_bytes','audit_event')),0)
    def test_archive_immutable(self):
        self.ingest(packet());
        for sql in ("UPDATE intake_archive SET payload=X'00'",'DELETE FROM artifact_bytes','DELETE FROM intake_binding'):
            with self.assertRaises(sqlite3.IntegrityError),self.db:self.db.execute(sql)
    def test_decision_snapshot(self):
        self.ingest(packet());sub=self.db.execute('SELECT id FROM submission').fetchone()[0];old,_=g.seal(self.db);fp=core.digest(self.db,old)
        self.assertRaises(PermissionError,g.decide,self.db,sub,'READER','fixture:qa','HOLD','reason');self.assertRaises(ValueError,g.decide,self.db,sub,'QA','fixture:qa','ELIGIBLE','reason')
        d=g.decide(self.db,sub,'QA','fixture:qa','HOLD','reason');self.assertEqual(g.decide(self.db,sub,'QA','fixture:qa','HOLD','reason'),d);new,_=g.seal(self.db);self.assertNotEqual(old,new);self.assertEqual(core.digest(self.db,old),fp);self.assertEqual(g.seal(self.db),(new,'NOOP'));self.assertEqual(dict(self.db.execute('SELECT availability,count(*) FROM snapshot_slot WHERE snapshot=? GROUP BY availability',(new,))),{'HOLD':40,'MISSING':4520})
    def test_latest_revision(self):
        self.ingest(packet());old=self.db.execute('SELECT id FROM submission').fetchone()[0];g.decide(self.db,old,'QA','fixture:qa','REJECTED','reason');self.ingest(packet(rev=2));self.assertRaises(ValueError,g.decide,self.db,old,'QA','fixture:qa','HOLD','reason');sid,_=g.seal(self.db);self.assertEqual(self.db.execute('SELECT availability,s.revision FROM pending_trace p JOIN submission s ON s.id=p.submission WHERE snapshot=?',(sid,)).fetchone(),('INCOMPLETE',2))
    def test_mixed_core(self):
        db=fixture(9)
        try:
            install(db);sid,state=g.seal(db);self.assertEqual((sid,state),(1,'NOOP'));self.assertEqual(db.execute('SELECT count(DISTINCT availability) FROM snapshot_slot WHERE snapshot=?',(sid,)).fetchone()[0],4);self.assertEqual(calculate(db,sid),('STORED_SYNTHETIC',360))
        finally:db.close()

if __name__=='__main__':unittest.main(verbosity=2)
