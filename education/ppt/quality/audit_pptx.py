"""Local-only PPTX intake and comparison. No external calls or automatic approval."""
import argparse, collections, hashlib, json, re, shutil, statistics, unicodedata
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
LIMIT = 200 * 1024 * 1024

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFC', s))

def preflight(path):
    if Path(path).suffix.lower() != '.pptx' or Path(path).stat().st_size > LIMIT:
        raise ValueError('Only bounded .pptx input accepted')
    with ZipFile(path) as z:
        infos = z.infolist(); names = [i.filename for i in infos]
        if len(infos) > 10000 or len(set(names)) != len(names) or sum(i.file_size for i in infos) > LIMIT:
            raise ValueError('ZIP size/count/duplicate limit')
        for i in infos:
            n = i.filename; p = PurePosixPath(n)
            if p.is_absolute() or '..' in p.parts or '\\' in n or ':' in n or i.flag_bits & 1 or i.file_size > 50*1024*1024 or i.file_size/max(i.compress_size,1) > 1000:
                raise ValueError('Unsafe ZIP entry: '+n)
            if not i.is_dir() and any(x in n.lower() for x in ('vbaproject','/activex/','/embeddings/')):
                raise ValueError('Active/embedded object requires separate review: '+n)
        if not {'[Content_Types].xml','ppt/presentation.xml'} <= set(names) or z.testzip() is not None:
            raise ValueError('Invalid PPTX or CRC')
        external = []
        for n in names:
            if n.endswith(('.xml','.rels')):
                raw = z.read(n)
                if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper(): raise ValueError('DTD/entity forbidden')
                root = etree.fromstring(raw, parser=etree.XMLParser(resolve_entities=False,no_network=True))
                if n.endswith('.rels'):
                    for r in root:
                        if r.get('TargetMode') == 'External':
                            external.append({'part':n,'type':r.get('Type','').rsplit('/',1)[-1]})
                if n == '[Content_Types].xml' and any('macroenabled' in r.get('ContentType','').lower() for r in root):
                    raise ValueError('Macro-enabled content')
        if external: raise ValueError('External relationships require quarantine review; no automatic opening')
        return {'zip_entries':len(names),'media_parts':sum(n.startswith('ppt/media/') for n in names),'external_relationships':external}

def paragraphs(shapes):
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from paragraphs(sh.shapes)
        if sh.has_text_frame:
            yield from (p.text for p in sh.text_frame.paragraphs if p.text.strip())
        if sh.has_table:
            for row in sh.table.rows:
                for cell in row.cells:
                    yield from (p.text for p in cell.text_frame.paragraphs if p.text.strip())

def all_shapes(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP: yield from all_shapes(sh.shapes)

def audit(path, producer='UNKNOWN', role='CANDIDATE', pdf=None, contract=None, archive=None):
    path = Path(path); package = preflight(path); sha = digest(path); deck = Presentation(path)
    expected = json.loads(Path(contract).read_text(encoding='utf-8')) if contract else None
    if expected and (len(expected['slides']) != len(deck.slides) or any(x['page'] != i+1 for i,x in enumerate(expected['slides']))): raise ValueError('Contract slide count/order mismatch')
    doc = None
    if pdf:
        import fitz
        doc = fitz.open(pdf)
        if len(doc) != len(deck.slides): doc.close(); raise ValueError('PDF page count mismatch')
    out = []
    try:
        for i, s in enumerate(deck.slides):
            shapes = list(all_shapes(s.shapes)); types = collections.Counter(sh.shape_type.name for sh in shapes)
            texts = list(paragraphs(s.shapes)); body = norm(' '.join(texts)); notes = ''
            if s.has_notes_slide and s.notes_slide.notes_text_frame is not None: notes = s.notes_slide.notes_text_frame.text.strip()
            colors = sorted({n.get('val').upper() for n in s._element.iter(A+'srgbClr') if n.get('val')})
            fonts = sorted({n.get('typeface') for tag in ('latin','ea','cs') for n in s._element.iter(A+tag) if n.get('typeface')})
            sizes = [int(r.get('sz'))/100 for run in s._element.iter(A+'r') if (t:=run.find(A+'t')) is not None and (t.text or '').strip() and (r:=run.find(A+'rPr')) is not None and r.get('sz','').isdigit()]
            bounds = [sh.name for sh in s.shapes if None not in (sh.left,sh.top,sh.width,sh.height) and (sh.left<0 or sh.top<0 or sh.left+sh.width>deck.slide_width+2 or sh.top+sh.height>deck.slide_height+2)]
            missing = None if doc is None else [t for t in texts if norm(t) not in norm(doc[i].get_text())]
            req = expected['slides'][i] if expected else None
            absent = None if req is None else [t for t in req.get('must_include',[]) if norm(t) not in body]
            note_match = None if req is None or 'notes' not in req else notes == req['notes'].strip()
            out.append({'page':i+1,'shape_count':len(shapes),'top_level_count':len(s.shapes),'shape_types':dict(types),'text_paragraphs':len(texts),'notes_present':bool(notes),'contract_missing':absent,'contract_notes_match':note_match,'direct_colors':colors,'direct_fonts':fonts,'direct_run_median_pt':statistics.median(sizes) if sizes else None,'out_of_bounds_top_level':bounds,'pdf_text_missing':missing})
    finally:
        if doc is not None: doc.close()
    if digest(path) != sha: raise ValueError('Input changed during inspection')
    if archive:
        target = Path(archive)/sha/'source.pptx'; target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists(): shutil.copyfile(path,target)
        if digest(target) != sha: raise ValueError('Archive hash mismatch')
    summary = {'slides':len(out),'notes_present':sum(x['notes_present'] for x in out),'objects':sum(x['shape_count'] for x in out),'top_level_bounds_flags':sum(len(x['out_of_bounds_top_level']) for x in out),'pdf_text_flags':None if pdf is None else sum(len(x['pdf_text_missing']) for x in out),'contract_missing':None if expected is None else sum(len(x['contract_missing']) for x in out),'contract_note_mismatches':None if expected is None else sum(x['contract_notes_match'] is False for x in out)}
    return {'schema_version':'1.0','source_name':path.name,'sha256':sha,'producer_declared':producer,'producer_verified':False,'role':role,'width_emu':deck.slide_width,'height_emu':deck.slide_height,'package':package,'pdf_sha256':digest(pdf) if pdf else None,'pdf_provenance':'CALLER_SUPPLIED_NOT_CRYPTOGRAPHICALLY_BOUND' if pdf else 'NOT_SUPPLIED','contract_sha256':digest(contract) if contract else None,'summary':summary,'slides':out,'status':'REVIEW_REQUIRED','can_ship':False,'quality_score':None,'limitations':['Top-level bounds only; groups/rotation/intentional bleeds require visual review','Explicit formatting only; inherited theme/style and font substitution not resolved','PDF text matching is heuristic, not proof of clipping or fact accuracy','Raster/SmartArt/chart content and external provenance require manual review']}

def compare(reference, candidate, mapping):
    if mapping['sha256'] != reference['sha256']: raise ValueError('Reference hash mismatch')
    rows = mapping['mappings']; expected = ['P'+str(i+1).zfill(2) for i in range(len(candidate['slides']))]
    if [m['slide_id'] for m in rows] != expected: raise ValueError('Mapping count/order mismatch')
    result = []
    for i,m in enumerate(rows):
        pages = m['source_pages']
        if not pages or any(not isinstance(p,int) or p<1 or p>len(reference['slides']) for p in pages): raise ValueError('Mapping page out of range')
        src = [reference['slides'][p-1] for p in pages]; dst = candidate['slides'][i]
        a = set().union(*(set(x['direct_colors']) for x in src)); b = set(dst['direct_colors']); u = a|b
        result.append({'slide_id':m['slide_id'],'reference_pages':pages,'role':m['role'],'explicit_color_jaccard':round(len(a&b)/len(u),3) if u else None,'shared_explicit_colors':sorted(a&b),'reference_fonts':sorted(set().union(*(set(x['direct_fonts']) for x in src))),'candidate_fonts':dst['direct_fonts'],'reference_median_pt':[x['direct_run_median_pt'] for x in src],'candidate_median_pt':dst['direct_run_median_pt'],'candidate_notes':dst['notes_present'],'candidate_bounds_flags':len(dst['out_of_bounds_top_level']),'candidate_pdf_flags':None if dst['pdf_text_missing'] is None else len(dst['pdf_text_missing']),'review':'PENDING','reuse_status':'CANDIDATE_ONLY'})
    return {'schema_version':'1.0','reference_sha256':reference['sha256'],'candidate_sha256':candidate['sha256'],'reference_summary':reference['summary'],'candidate_summary':candidate['summary'],'aspect_equal':reference['width_emu']*candidate['height_emu']==candidate['width_emu']*reference['height_emu'],'mapping':result,'design_score':None,'can_ship':False,'status':'MANUAL_REVIEW_REQUIRED'}

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('audit'); a.add_argument('pptx'); a.add_argument('--producer',default='UNKNOWN'); a.add_argument('--role',choices=['REFERENCE','CANDIDATE','BASELINE'],default='CANDIDATE'); a.add_argument('--pdf'); a.add_argument('--contract'); a.add_argument('--archive'); a.add_argument('--out',required=True)
    c=sub.add_parser('compare'); c.add_argument('reference'); c.add_argument('candidate'); c.add_argument('mapping'); c.add_argument('--out',required=True)
    x=p.parse_args(); read=lambda f:json.loads(Path(f).read_text(encoding='utf-8'))
    result=audit(x.pptx,x.producer,x.role,x.pdf,x.contract,x.archive) if x.command=='audit' else compare(read(x.reference),read(x.candidate),read(x.mapping))
    target=Path(x.out); target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
