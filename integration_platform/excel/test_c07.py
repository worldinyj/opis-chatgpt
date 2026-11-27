import tempfile, unittest
from pathlib import Path
from artifact_tool import Workbook, SpreadsheetFile
from c07_excel import CODES, export_copy, plan, digest

def fixture(n=1):
    rows=[];records=[]
    for i in range(n):
        q=f'SYNTHETIC-{i:03}';e=f'FIXTURE-E{i:03}'
        for c in CODES:
            k=q+'-'+c;v=[None]*29;v[:3]=[k,q,e];v[7]=c;v[14]='선정';v[24]='기존 전문가 초안';rows.append(v)
            records.append(dict(key=k,queue_id=q,event_id=e,code=c,model='GEMINI',availability='ELIGIBLE',eligibility_ref='fixture:'+q,role='D',result='선정',rationale='합성 근거',source='합성 출처'))
    return rows,records

class Tests(unittest.TestCase):
    def test_grid(self):
        r,x=fixture(38);self.assertEqual(len(plan(r,list(reversed(x)),'GEMINI')),1520)
    def test_partial(self):
        r,x=fixture();self.assertRaises(ValueError,plan,r,x[:-1],'GEMINI')
    def test_hold(self):
        r,x=fixture();x[0]['availability']='HOLD';self.assertRaises(ValueError,plan,r,x,'GEMINI')
    def test_formula(self):
        r,x=fixture();x[0]['rationale']='  =1+1';self.assertRaises(ValueError,plan,r,x,'GEMINI')
    def test_duplicate(self):
        r,x=fixture();self.assertRaises(ValueError,plan,r,x+[x[0]],'GEMINI')
    def test_real_key(self):
        r,x=fixture();r[0][1]='ROOT-001';self.assertRaises(ValueError,plan,r,x,'GEMINI')
    def test_copy(self):
        r,x=fixture();r.reverse()
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a.xlsx',Path(d)/'b.xlsx';w=Workbook.create();s=w.worksheets.add('통합검토');s.get_range('A1').values=[['SYNTHETIC_ONLY']];s.get_range('A4:AC43').values=r;s.get_range('V4').formulas=[['=COUNTIF(O4:U4,"선정")']];s.get_range('AC4').formulas=[['=V4']];SpreadsheetFile.export_xlsx(w).save(str(a));h=digest(a);out=export_copy(a,b,x,'GEMINI',40);self.assertEqual(out['cells'],120);self.assertEqual(digest(a),h);self.assertRaises(ValueError,export_copy,a,b,x,'GEMINI',40)
if __name__=='__main__':unittest.main(verbosity=2)
