"""Optional actual XLSX synthetic round-trip; workbook edits use artifact_tool only."""
import tempfile
import unittest
from pathlib import Path
from artifact_tool import Workbook, SpreadsheetFile, Blob
from c07_portable import create_plan, inspect_xlsx, verify_target_sheet_copy, COLS
from test_c07_portable import fixture


class Roundtrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name);cls.source=cls.root/'source.xlsx'
        cells,cls.records=fixture(38)
        wb=Workbook.create();s=wb.worksheets.add('통합검토');s.get_range('A1').values=[['SYNTHETIC_ONLY']]
        cols=[chr(i) for i in range(65,91)]+['AA','AB','AC']
        s.get_range('A3:AC3').values=[[cells.get(c+'3',('B',None))[1] for c in cols]]
        s.get_range('A4:AC1523').values=[[cells.get(c+str(r),('B',None))[1] if cells.get(c+str(r),('B',None))[0]!='F' else None for c in cols] for r in range(4,1524)]
        s.get_range('V4:V1523').formulas=[[f'=COUNTIF(O{r}:U{r},"선정")'] for r in range(4,1524)]
        s.get_range('AC4:AC1523').formulas=[[f'=V{r}'] for r in range(4,1524)]
        s.get_range('A3:AC3').format={'fill':'#16334A','font':{'bold':True,'color':'#FFFFFF'}}
        SpreadsheetFile.export_xlsx(wb).save(str(cls.source));cls.raw=cls.source.read_bytes()

    def roundtrip(self,model):
        records=[dict(r,model=model) for r in reversed(self.records)]
        plan=create_plan(self.raw,records,model);self.assertEqual((plan['rows'],plan['cells']),(1520,4560))
        values=[x['value'] for x in plan['changes']];cols=COLS[model]
        wb=SpreadsheetFile.import_xlsx(Blob.load(str(self.source)));sheet=wb.worksheets.get_item('통합검토')
        sheet.get_range(f'{cols[0]}4:{cols[-1]}1523').values=[values[i:i+3] for i in range(0,len(values),3)]
        dest=self.root/(model+'.xlsx');SpreadsheetFile.export_xlsx(wb).save(str(dest))
        result=verify_target_sheet_copy(self.raw,dest.read_bytes(),records,model)
        self.assertEqual((result['rows'],result['cells']),(1520,4560));self.assertFalse(result['workbook_features_verified']);self.assertEqual(self.source.read_bytes(),self.raw)
        cells,_=inspect_xlsx(dest.read_bytes());self.assertEqual(sum(v[0]=='F' for v in cells.values()),3040)

    def test_gemini(self):self.roundtrip('GEMINI')
    def test_claude(self):self.roundtrip('CLAUDE')

if __name__=='__main__':unittest.main(verbosity=2)
