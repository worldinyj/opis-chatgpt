"""Standard library tests of portable plan and XML parsing (no workbook writes)."""
import copy
import unittest
from c07_portable import CODES, NS, ROLE, COLS, plan, sheet_cells, xml, coord, verify_cells


def fixture(n=1,model='GEMINI'):
    cells={'A1':('T','SYNTHETIC_ONLY')}
    for c,label in {'A':'review_key','B':'queue_id','C':'event_id','H':'attribute_code','P':'Gemini result','Q':'Gemini rationale','R':'Gemini source','S':'Claude result','T':'Claude rationale','U':'Claude source'}.items():cells[c+'3']=('T',label)
    records=[];row=4
    for i in range(n):
        q=f'SYNTHETIC-{i:03}';e=f'FIXTURE-E{i:03}'
        for code in CODES:
            k=q+'-'+code
            for c,v in zip(('A','B','C','H'),(k,q,e,code)):cells[c+str(row)]=('T',v)
            cells['O'+str(row)]=('T','선정');cells['Y'+str(row)]=('T','fixture expert draft');cells['AC'+str(row)]=('F',f'V{row}')
            records.append(dict(key=k,queue_id=q,event_id=e,code=code,model=model,availability='ELIGIBLE',eligibility_ref='fixture:'+q,role='D',result=ROLE['D'],rationale='합성 근거',source='합성 출처'))
            row+=1
    return cells,records


class Tests(unittest.TestCase):
    def test_full_grid_both_models(self):
        for model,cols in COLS.items():
            cells,records=fixture(38,model);before=copy.deepcopy(cells);result=plan(cells,[],list(reversed(records)),model)
            self.assertEqual(len(result),4560);self.assertEqual({x['cell'] for x in result},{c+str(r) for c in cols for r in range(4,1524)});self.assertEqual(cells,before)
    def test_partial_event(self):
        cells,r=fixture();self.assertRaises(ValueError,plan,cells,[],r[:-1],'GEMINI',40)
    def test_complete_subset(self):
        cells,r=fixture(38);self.assertEqual(len(plan(cells,[],r[-40:],'GEMINI')),120)
    def test_duplicate(self):
        cells,r=fixture();self.assertRaises(ValueError,plan,cells,[],r+[r[0]],'GEMINI',40)
    def test_hold(self):
        cells,r=fixture();r[0]['availability']='HOLD';self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_mixed_reference(self):
        cells,r=fixture();r[0]['eligibility_ref']='fixture:different';self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_wrong_header(self):
        cells,r=fixture();cells['P3']=('T','wrong');self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_wrong_identity(self):
        cells,r=fixture();r[0]['event_id']='FIXTURE-E999';self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_real_id(self):
        cells,r=fixture();cells['B4']=('T','ROOT-001');self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_formula_injection(self):
        cells,r=fixture()
        for s in (' =1+1','\t@x','  +123','-1','\u00a0=1','', 'x\x00y'):
            r[0]['rationale']=s;self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_target_not_empty(self):
        cells,r=fixture()
        for v in [('F','IF(1,0,0)'),('T','existing'),('n','0')]:
            cells['P4']=v;self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_merged_target(self):
        cells,r=fixture();self.assertRaises(ValueError,plan,cells,[(coord('O4'),coord('P4'))],r,'GEMINI',40)
    def test_extra_master_row(self):
        cells,r=fixture();cells['A44']=('T','extra');self.assertRaises(ValueError,plan,cells,[],r,'GEMINI',40)
    def test_verify_copy(self):
        cells,r=fixture();changes=plan(cells,[],r,'GEMINI',40);after=dict(cells)
        for x in changes:after[x['cell']]=('T',x['value'])
        verify_cells(cells,after,changes)
        for addr,v in [('O4',('T','altered')),('Y4',('T','altered')),('AC4',('F','1+1')),('S4',('T','unexpected')),('P4',('F','1+1'))]:
            altered=dict(after);altered[addr]=v;self.assertRaises(ValueError,verify_cells,cells,altered,changes)
    def test_xml_values(self):
        raw=f'<worksheet xmlns="{NS}"><sheetData><row r="4"><c r="A4" t="s"><v>0</v></c><c r="P4" t="inlineStr"><is><r><t>합성</t></r><r><t> 근거</t></r></is></c><c r="AC4"><f>V4</f><v>0</v></c></row></sheetData></worksheet>'.encode();cells,merges=sheet_cells(xml(raw),['key']);self.assertEqual(cells,{'A4':('T','key'),'P4':('T','합성 근거'),'AC4':('F','V4')});self.assertEqual(merges,[])
    def test_xml_unsafe(self):
        self.assertRaises(ValueError,xml,b'<!DOCTYPE x [<!ENTITY x "y">]><x>&x;</x>')
    def test_xml_duplicate_and_shared_formula(self):
        for content in ('<c r="A4"/><c r="A4"/>','<c r="A4"><f t="shared" si="0">V4</f></c>','<c r="A4" t="s"><v>2</v></c>'):
            raw=f'<worksheet xmlns="{NS}"><sheetData><row r="4">{content}</row></sheetData></worksheet>'.encode();self.assertRaises(ValueError,sheet_cells,xml(raw),[])
if __name__=='__main__':unittest.main(verbosity=2)
