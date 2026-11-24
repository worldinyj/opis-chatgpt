"""Offline PPTX native object, notes, and optional PDF text check.
Usage: python verify_pptx.py manifest.json output.pptx [--pdf output.pdf]
Dependencies: python-pptx; PyMuPDF for optional PDF.
"""
import argparse, json, re
from pathlib import Path
from zipfile import ZipFile
from pptx import Presentation

def verify(manifest, pptx, pdf=None):
    m=json.loads(Path(manifest).read_text(encoding="utf-8"))
    deck=Presentation(pptx)
    assert len(deck.slides)==len(m["slides"]), "slide count"
    assert deck.slide_width*9==deck.slide_height*16, "aspect"
    with ZipFile(pptx) as z:
        assert z.testzip() is None, "ZIP integrity"
        assert not any(x.startswith("ppt/media/") for x in z.namelist()), "unexpected raster/media asset"
    doc=None
    if pdf:
        import fitz
        doc=fitz.open(pdf)
        assert len(doc)==len(deck.slides), "PDF slide count"
    normalize=lambda x: re.sub(r"\s+","",x)
    minutes=0
    shapes=0
    for i,s in enumerate(deck.slides):
        expected=m["slides"][i]["speaker_notes"]
        assert s.notes_slide.notes_text_frame.text==expected, f"notes {i+1}"
        match=re.match(r"^(\d+)분",expected)
        minutes+=int(match.group(1)) if match else 0
        shapes+=len(s.shapes)
        rendered=normalize(doc[i].get_text()) if doc else None
        for sh in s.shapes:
            assert sh.left>=0 and sh.top>=0 and sh.left+sh.width<=deck.slide_width+2 and sh.top+sh.height<=deck.slide_height+2, f"bounds slide {i+1}"
            if rendered is not None and sh.has_text_frame:
                for para in sh.text_frame.paragraphs:
                    t=normalize(para.text)
                    assert not t or t in rendered, f"rendered text missing slide {i+1}: {t}"
    if doc: doc.close()
    print(f"PASS: {len(deck.slides)} slides, {shapes} native shapes, notes exact; proposed minutes {minutes}; PDF checked={bool(pdf)}")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("manifest"); p.add_argument("pptx"); p.add_argument("--pdf")
    a=p.parse_args(); verify(a.manifest,a.pptx,a.pdf)
