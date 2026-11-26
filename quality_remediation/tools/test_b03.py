import copy,csv,io,hashlib,subprocess,tempfile,unittest
from pathlib import Path
from b03_validator import *

class TestB03(unittest.TestCase):
    def setUp(self):
        self.q='ROOT-014'; self.e='00123'; self.h='a'*64
        self.names=[{'code':f'X{i:02}','name':f'fixture {i}'} for i in range(40)]
        self.std={'principles':[{'attributes':self.names}]}
        self.schema={'type':'object','properties':{'attributes':{'type':'array','minItems':40,'maxItems':40},'model':{'properties':{'run_date':{'format':'date'}}}},'required':['attributes','model']}
        self.expected={'queue_id':self.q,'event_id':self.e,'expected_pdf':{'sha256':self.h,'pages':10}}
        ref={'section':'fixture','printed_pages':[2],'pdf_pages':[3],'summary':'fixture'}
        self.review={'queue_id':self.q,'event_id':self.e,'model':{'provider':'GEMINI','run_date':'2000-01-01'},'source':{'sha256':self.h,'pdf_page_count':10,'verification':'BINARY_HASH_VERIFIED'},'facts':[{'id':'GEMINI-F01','source_refs':[ref]}],'attributes':[]}
        self.rows=[]
        for i,n in enumerate(self.names):
            a={'review_key':self.q+'-'+n['code'],**n,'role':'D' if i==0 else 'N','review_result':'선정' if i==0 else '미선정','rationale':'fixture, "quoted"\nline','fact_ids':['GEMINI-F01'] if i==0 else [],'source_refs':[copy.deepcopy(ref)] if i==0 else []}
            self.review['attributes'].append(a)
            self.rows.append([a['review_key'],self.q,self.e,a['code'],a['review_result'],a['rationale'],'GEMINI-F01' if i==0 else EMPTY])
    def raw(self):
        s=io.StringIO(newline=''); w=csv.writer(s);w.writerow(HEADER);w.writerows(self.rows);return s.getvalue().encode()
    def check(self): return verify(self.review,self.raw(),self.schema,self.std,self.expected)
    def has(self,c): self.assertIn(c,[i[0] for i in self.check()['issues']])
    def test_valid(self): self.assertTrue(self.check()['candidate'])
    def test_json_duplicate(self): self.assertRaises(ValueError,parse_json,b'{"x":1,"x":2}')
    def test_bad_csv(self): self.assertRaises(ValueError,parse_csv,self.raw().replace(b'ROOT-014-X00',b'ROOT-"014-X00',1))
    def test_partial(self): self.rows.pop();self.assertRaises(ValueError,self.check)
    def test_duplicate(self): self.rows[1]=self.rows[0];self.has('CSV_KEY_SET')
    def test_role(self): self.review['attributes'][0]['role']='N';self.has('ATTRIBUTE_ID_ROLE')
    def test_missing_evidence(self): self.review['attributes'][0]['fact_ids']=[];self.has('EVIDENCE_INCOMPLETE')
    def test_unknown_fact(self): self.review['attributes'][0]['fact_ids']=['GEMINI-F99'];self.has('UNKNOWN_FACT')
    def test_gap(self): self.review['attributes'][0]['source_refs'][0]['printed_pages']=[68,69];self.has('LEDGER_GAP_printed_pages')
    def test_pdf_range(self): self.review['attributes'][0]['source_refs'][0]['pdf_pages']=[11];self.has('PDF_RANGE')
    def test_identity(self): self.review['source']['sha256']=None;self.has('SOURCE_IDENTITY_UNVERIFIED')
    def test_formula(self): self.rows[0][5]=' =SUM(A1)';self.has('FORMULA_PREFIX')
    def test_prefix(self): self.rows[0][5]='[D] '+self.rows[0][5];self.assertTrue(self.check()['candidate']);self.assertIn(['ROLE_PREFIX',self.rows[0][0]],self.check()['repairs'])
    def test_changed_rationale(self): self.rows[0][5]='different';self.has('RATIONALE_CHANGED')
    def test_format_checker(self): self.review['model']['run_date']='invalid';self.has('SCHEMA')
    def test_empty(self): self.rows[1][6]='none';self.assertIn(['EMPTY_SOURCE',self.rows[1][0]],self.check()['repairs'])
    def test_pin(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*a): return subprocess.check_output(['git','-C',d,*a],stderr=subprocess.DEVNULL).decode().strip()
            git('init');p=Path(d)/'x';p.write_bytes(b'fixture');git('add','x');git('-c','user.name=fixture','-c','user.email=fixture@example.invalid','commit','-m','fixture');ref=git('rev-parse','HEAD');blob=git('rev-parse','HEAD:x')
            self.assertEqual(read_pin(d,ref,'x',blob,hashlib.sha256(b'fixture').hexdigest()),b'fixture')
            self.assertRaises(ValueError,read_pin,d,ref,'x','0'*40)
            self.assertRaises(ValueError,read_pin,d,ref,'x',blob,'0'*64)
            self.assertRaises(ValueError,read_pin,d,ref,'../x',blob)

if __name__=='__main__': unittest.main()
