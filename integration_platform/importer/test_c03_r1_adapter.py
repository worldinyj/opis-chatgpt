"""Run in the integration branch checkout: python integration_platform/importer/test_c03_r1_adapter.py --repo ."""
import argparse
import copy
import csv
import io
import json
import sqlite3
import sys
import unittest
from pathlib import Path
from jsonschema import ValidationError
import c03_r1_adapter as a
import c03_staging as stage

SCHEMA = STANDARD = CONNECT = None


def fixture(model='GEMINI'):
    loc={'section':'fixture','printed_pages':[1],'pdf_pages':[],'summary':'fixture only'}
    j={'schema_version':'1.0','prompt_version':'1.0','standard_version':'1.0','queue_id':a.Q,'event_id':a.EVENT,
       'model':{'provider':model,'version':'fixture','run_date':'2000-01-01'},
       'source':{'filename':'SYNTHETIC_ONLY.pdf','report_number':'FIXTURE-999','report_date':None,'sha256':None,'pdf_page_count':None,'reading_scope':'SYNTHETIC_ONLY','verification':'PDF_READ_HASH_UNAVAILABLE'},
       'independence':{'other_ai_outputs_seen':False,'notes':'fixture'},
       'facts':[{'id':model+'-F01','summary':'fixture','kind':'OBSERVED_FACT','source_refs':[loc],'limitation':'fixture'}],
       'attributes':[],'limitations':['fixture'],'status':'INDEPENDENT_DRAFT','approved':False,'can_ship':False}
    for i,(code,name) in enumerate(a.names(STANDARD).items()):
        j['attributes'].append({'review_key':a.Q+'-'+code,'code':code,'name':name,'role':'D' if i==0 else 'N','review_result':'선정' if i==0 else '미선정','rationale':'fixture, "quoted"\nline','fact_ids':[model+'-F01'] if i==0 else [],'source_refs':[copy.deepcopy(loc)] if i==0 else [],'counterevidence_or_limitation':'fixture only'})
    return j


def archive(j, csv_mutator=None):
    s=io.StringIO(newline='');w=csv.writer(s);w.writerow(stage.HEADER)
    for x in j['attributes']:
        w.writerow([x['review_key'],j['queue_id'],j['event_id'],x['code'],x['review_result'],x['rationale'],a.render_source(x,j['source']['report_number'])])
    raw=s.getvalue()
    if csv_mutator: raw=csv_mutator(raw)
    return stage.zip_bytes({'review.json':json.dumps(j,ensure_ascii=False).encode(),'excel_import.csv':raw.encode(),'report.md':b'SYNTHETIC_ONLY\nfixture','validation.md':b'SYNTHETIC_ONLY\nfixture'})


def seed(db):
    with db:
        db.execute('INSERT INTO standard VALUES(?)',(a.VERSION,))
        db.execute('INSERT INTO principle VALUES(?,?,?)',(a.VERSION,'FIXTURE','fixture'))
        db.executemany('INSERT INTO attribute VALUES(?,?,?,?,?)',[(a.VERSION,c,'FIXTURE',n,'fixture') for c,n in a.names(STANDARD).items()])
        db.execute('INSERT INTO event VALUES(?,?,2000)',(a.CORE_Q,a.EVENT))
        db.execute("INSERT INTO review_key SELECT queue_id||'-'||code,queue_id,version,code FROM event CROSS JOIN attribute")


class AdapterTests(unittest.TestCase):
    def setUp(self): self.j=fixture()
    def validate(self): return a.adapt_external(archive(self.j),SCHEMA,STANDARD)
    def test_gemini(self): self.assertEqual(len(self.validate()[0]['attributes']),40)
    def test_claude(self): self.j=fixture('CLAUDE'); self.assertEqual(self.validate()[0]['model']['provider'],'CLAUDE')
    def test_real_id(self): self.j['queue_id']='ROOT-004'; self.assertRaises(ValueError,self.validate)
    def test_schema_approval(self): self.j['approved']=True; self.assertRaises(ValidationError,self.validate)
    def test_date(self): self.j['model']['run_date']='invalid'; self.assertRaises(ValidationError,self.validate)
    def test_name(self): self.j['attributes'][0]['name']='wrong'; self.assertRaises(ValueError,self.validate)
    def test_section(self): self.j['attributes'][0]['source_refs'][0]['section']='wrong'; self.assertRaises(ValueError,self.validate)
    def test_page_gap(self): self.j['attributes'][0]['source_refs'][0]['printed_pages']=[2]; self.assertRaises(ValueError,self.validate)
    def test_csv_source(self):
        self.assertRaises(ValueError,a.adapt_external,archive(self.j,lambda s:s.replace('절 fixture','절 altered')),SCHEMA,STANDARD)
    def test_baseline_null(self):
        s=io.StringIO(newline=''); w=csv.writer(s); w.writerow(['review_key','queue_id','event_id','attribute_code','role','chatgpt_review_result']);w.writerows([[a.Q+'-'+c,a.Q,a.EVENT,c,'A','판단보류'] for c in stage.CODES]);out=a.adapt_baseline(s.getvalue().encode());self.assertEqual(len(out),40);self.assertTrue(all(x['rationale'] is None for x in out))


class BridgeTests(unittest.TestCase):
    def setUp(self): self.db=CONNECT();seed(self.db);self.j=fixture()
    def tearDown(self): self.db.close()
    def ingest(self,revision=1): return a.bridge_external(self.db,archive(self.j),SCHEMA,STANDARD,revision)
    def count(self,table): return self.db.execute('SELECT count(*) FROM '+table).fetchone()[0]
    def test_positive(self):
        self.assertEqual(self.ingest(),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.count('ai_review'),40);self.assertEqual(self.count('artifact'),4);self.assertEqual(self.count('fact'),1);self.assertEqual(self.count('review_fact'),1);self.assertEqual(self.count('eligibility'),0);self.assertEqual(self.count('validation_check'),4)
    def test_noop(self): self.ingest();self.assertEqual(self.ingest(),'NOOP');self.assertEqual(self.count('ai_review'),40)
    def test_conflict(self): self.ingest();self.j['attributes'][0]['rationale']='changed';self.assertEqual(self.ingest(),'CONFLICT_QUARANTINED');self.assertEqual(self.count('submission'),1)
    def test_revision(self): self.ingest();self.assertEqual(self.ingest(2),'STAGED_NOT_ELIGIBLE');self.assertEqual(self.count('ai_review'),80)
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER force_rollback BEFORE INSERT ON ai_review WHEN NEW.key LIKE '%-WP4' BEGIN SELECT RAISE(ABORT,'forced'); END")
        self.assertRaises(sqlite3.IntegrityError,self.ingest)
        for table in ('source_revision','submission','artifact','ai_review','fact','validation_run','audit_event'):self.assertEqual(self.count(table),0)
    def test_two_models(self): self.ingest();self.j=fixture('CLAUDE');self.ingest();self.assertEqual(self.count('submission'),2);self.assertEqual(self.count('ai_review'),80)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo',required=True);args=parser.parse_args()
    contracts=a.read_contract(args.repo);SCHEMA=contracts['standards/independent_ai_review_v1.schema.json'];STANDARD=contracts['standards/safety_culture_40.json']
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'db'))
    import c02_r2
    CONNECT=c02_r2.connect
    unittest.main(argv=[sys.argv[0]],verbosity=2)
