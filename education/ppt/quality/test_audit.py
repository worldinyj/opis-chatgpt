"""Offline unit tests; run with python -m unittest test_audit.py."""
import copy, json, tempfile, unittest
from pathlib import Path
from zipfile import ZipFile
from pptx import Presentation
from pptx.util import Inches
from audit_pptx import audit, compare, preflight, digest

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.p=self.root/'source.pptx'; d=Presentation(); s=d.slides.add_slide(d.slide_layouts[6]); s.shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(1)).text='WP1 작업 관리'; s.notes_slide.notes_text_frame.text='근거 F01'; d.save(self.p)
    def tearDown(self): self.tmp.cleanup()
    def altered(self,name,data):
        out=self.root/'bad.pptx'
        with ZipFile(self.p) as src, ZipFile(out,'w') as dst:
            for i in src.infolist(): dst.writestr(i,src.read(i.filename))
            dst.writestr(name,data)
        return out
    def test_archive_and_notes(self):
        d=audit(self.p,archive=self.root/'archive'); self.assertEqual(d['summary']['notes_present'],1); self.assertFalse(d['can_ship']); self.assertEqual(digest(self.root/'archive'/d['sha256']/'source.pptx'),d['sha256']); self.assertEqual(audit(self.p,archive=self.root/'archive')['sha256'],d['sha256'])
    def test_missing_content(self):
        c=self.root/'contract.json'; c.write_text(json.dumps({'slides':[{'page':1,'must_include':['WP2'], 'notes':'wrong'}]})); d=audit(self.p,contract=c); self.assertEqual(d['summary']['contract_missing'],1); self.assertEqual(d['summary']['contract_note_mismatches'],1)
    def test_contract_count(self):
        c=self.root/'contract.json'; c.write_text('{"slides":[]}'); self.assertRaises(ValueError,audit,self.p,contract=c)
    def test_zip_traversal(self): self.assertRaises(ValueError,preflight,self.altered('../escape.xml','<a/>'))
    def test_embedded(self): self.assertRaises(ValueError,preflight,self.altered('ppt/embeddings/obj.bin',b'bad'))
    def test_external(self): self.assertRaises(ValueError,preflight,self.altered('ppt/_rels/test.xml.rels','<Relationships><Relationship TargetMode="External" Type="x/hyperlink" Target="https://example.invalid"/></Relationships>'))
    def test_dtd(self): self.assertRaises(ValueError,preflight,self.altered('ppt/test.xml','<!DOCTYPE a><a/>'))
    def test_empty_embedding_directory(self): preflight(self.altered('ppt/embeddings/',b''))
    def test_mapping(self):
        d=audit(self.p); m={'sha256':d['sha256'],'mappings':[{'slide_id':'P01','source_pages':[1],'role':'TEST'}]}; self.assertEqual(len(compare(d,d,m)['mapping']),1); self.assertIsNone(compare(d,d,m)['design_score']); self.assertFalse(compare(d,d,m)['can_ship']); bad=copy.deepcopy(m); bad['sha256']='bad'; self.assertRaises(ValueError,compare,d,d,bad); bad=copy.deepcopy(m); bad['mappings'][0]['source_pages']=[2]; self.assertRaises(ValueError,compare,d,d,bad)
    def test_wrong_pdf_page_count(self):
        import fitz
        pdf=self.root/'bad.pdf'; d=fitz.open(); d.new_page(); d.new_page(); d.save(pdf); d.close(); self.assertRaises(ValueError,audit,self.p,pdf=pdf)

if __name__=='__main__': unittest.main()
