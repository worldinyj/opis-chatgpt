import csv,io,json,sqlite3,unittest,argparse
import c03_r1_adapter as a
import c03_staging as stage
from c09_connection import connect
from c09_import import baseline,seal_pending
from c04_r1_bridge import calculate
from c05_r1_groups import summarize_groups
from c04_consensus import Slot

SCHEMA=STANDARD=None

def archive(model,role='D'):
    loc={'section':'fixture','printed_pages':[1],'pdf_pages':[],'summary':'fixture only'}
    j={'schema_version':'1.0','prompt_version':'1.0','standard_version':'1.0','queue_id':a.Q,'event_id':a.EVENT,'model':{'provider':model,'version':'fixture','run_date':'2000-01-01'},'source':{'filename':'SYNTHETIC_ONLY.pdf','report_number':'FIXTURE-999','report_date':None,'sha256':None,'pdf_page_count':None,'reading_scope':'SYNTHETIC_ONLY','verification':'PDF_READ_HASH_UNAVAILABLE'},'independence':{'other_ai_outputs_seen':False,'notes':'fixture'},'facts':[{'id':model+'-F01','summary':'fixture','kind':'OBSERVED_FACT','source_refs':[loc],'limitation':'fixture'}],'attributes':[],'limitations':['fixture'],'status':'INDEPENDENT_DRAFT','approved':False,'can_ship':False}
    s=io.StringIO(newline='');w=csv.writer(s);w.writerow(stage.HEADER)
    for i,(c,n) in enumerate(a.names(STANDARD).items()):
        r=role if i==0 else 'N';x={'review_key':a.Q+'-'+c,'code':c,'name':n,'role':r,'review_result':stage.ROLE[r],'rationale':'fixture rationale','fact_ids':[model+'-F01'] if i==0 else [],'source_refs':[loc] if i==0 else [],'counterevidence_or_limitation':'fixture'};j['attributes'].append(x);w.writerow([x['review_key'],a.Q,a.EVENT,c,x['review_result'],x['rationale'],a.render_source(x,'FIXTURE-999')])
    return stage.zip_bytes({'review.json':json.dumps(j,ensure_ascii=False).encode(),'excel_import.csv':s.getvalue().encode(),'report.md':b'SYNTHETIC_ONLY\nfixture','validation.md':b'SYNTHETIC_ONLY\nfixture'})

def csv_baseline(role='A'):
    s=io.StringIO(newline='');w=csv.writer(s);w.writerow(['review_key','queue_id','event_id','attribute_code','role','chatgpt_review_result']);w.writerows([[a.Q+'-'+c,a.Q,a.EVENT,c,role,stage.ROLE[role]] for c in stage.CODES]);return s.getvalue().encode()

class Tests(unittest.TestCase):
    def setUp(self):
        self.db=connect();d=self.db
        with d:
            d.execute('INSERT INTO standard VALUES(?)',(a.VERSION,));d.execute('INSERT INTO principle VALUES(?,?,?)',(a.VERSION,'FIXTURE','fixture'));d.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)',[(a.VERSION,c,'FIXTURE',n,'fixture') for c,n in a.names(STANDARD).items()]);d.execute('INSERT INTO event VALUES(?,?,2000)',(a.CORE_Q,a.EVENT));d.execute("INSERT INTO review_key SELECT queue_id||'-'||code,queue_id,version,code FROM event CROSS JOIN attribute")
    def tearDown(self):self.db.close()
    def ingest(self,m='GEMINI',role='D',revision=1):return a.bridge_external(self.db,archive(m,role),SCHEMA,STANDARD,revision)
    def count(self,t):return self.db.execute('SELECT count(*) FROM '+t).fetchone()[0]
    def test_external(self):
        self.assertEqual(self.ingest(),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.ingest('CLAUDE'),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.count('ai_review'),80);self.assertEqual(self.count('eligibility'),0)
    def test_external_conflict(self):
        self.ingest();self.assertEqual(self.ingest(),'NOOP');self.assertEqual(self.ingest(role='I'),'CONFLICT_QUARANTINED');self.assertEqual(self.ingest(revision=2),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.count('submission'),2)
    def test_baseline(self):
        self.assertEqual(baseline(self.db,csv_baseline()),'STAGED_NOT_ELIGIBLE');self.assertEqual(baseline(self.db,csv_baseline()),'NOOP');self.assertEqual(baseline(self.db,csv_baseline('N')),'CONFLICT_QUARANTINED');self.assertEqual(self.db.execute('SELECT count(*) FROM ai_review WHERE rationale IS NULL').fetchone()[0],40)
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER fail_import BEFORE INSERT ON ai_review WHEN NEW.key LIKE '%-WP4' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        for fun in (self.ingest,lambda:baseline(self.db,csv_baseline())):
            self.assertRaises(sqlite3.IntegrityError,fun);self.assertEqual(sum(self.count(t) for t in ('submission','artifact','ai_review','validation_run','audit_event')),0)
    def test_eligibility_denied(self):
        self.ingest();s,r=self.db.execute('SELECT submission,id FROM validation_run').fetchone()
        with self.assertRaises(sqlite3.IntegrityError),self.db:self.db.execute("INSERT INTO eligibility(submission,validation_run,status,reason,actor,at) VALUES(?,?,'ELIGIBLE','fixture','fixture','2000-01-01')",(s,r))
    def test_three_model_pipeline(self):
        self.ingest();self.ingest('CLAUDE');baseline(self.db,csv_baseline());sid=seal_pending(self.db);self.assertEqual(calculate(self.db,sid),('STORED_SYNTHETIC',40));self.assertEqual(self.count('ai_review'),120);self.assertEqual(self.count('snapshot_slot'),120);self.assertEqual(self.db.execute("SELECT count(*) FROM consensus WHERE status='PENDING_INPUT' AND selected_count IS NULL AND responded_count=0").fetchone()[0],40)
        ballots={k:[Slot(**s) for s in json.loads(reason)['result']['votes']] for k,reason in self.db.execute('SELECT key,reason FROM consensus')};out=summarize_groups([a.CORE_Q],ballots,{a.CORE_Q:{'plant':'FIXTURE-999','year':2000}});self.assertEqual(out['overall']['complete_keys'],0);self.assertEqual(out['overall']['pending_keys'],40)
    def test_missing(self):
        self.ingest();sid=seal_pending(self.db);self.assertEqual(dict(self.db.execute('SELECT availability,count(*) FROM snapshot_slot GROUP BY availability')),{'INCOMPLETE':40,'MISSING':80});self.assertEqual(calculate(self.db,sid),('STORED_SYNTHETIC',40))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo');p.add_argument('--local-fixture',action='store_true');args=p.parse_args()
    if args.local_fixture:
        SCHEMA=json.load(open('schema.json'));STANDARD={'principles':[{'attributes':[{'code':c,'name':n} for c,n in group]} for group in json.load(open('names.json'))]}
    else:
        contracts=a.read_contract(args.repo);SCHEMA=contracts['standards/independent_ai_review_v1.schema.json'];STANDARD=contracts['standards/safety_culture_40.json']
    unittest.main(argv=['test'],verbosity=2)
