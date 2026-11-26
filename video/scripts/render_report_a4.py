#!/usr/bin/env python3
"""Render existing report Markdown to A4 and audit output, without changing source."""
import argparse
import hashlib
import html
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from importlib.metadata import version

FONT = 'Noto Sans CJK KR'
CSS = '''
@page { size: A4; margin: 19mm 18mm 18mm;
  @top-left { content: "OPIS  |  안전문화 교육용 초안"; font-size: 8pt; color: #526174; }
  @bottom-left { content: "전문가 미승인 · 배포 금지"; font-size: 8pt; color: #526174; }
  @bottom-right { content: counter(page) " / " counter(pages); font-size: 8pt; color: #526174; }
}
html { font-family: "Noto Sans CJK KR", sans-serif; font-size: 10.5pt; color: #192533; line-height: 1.48; }
body { margin: 0; overflow-wrap: anywhere; }
h1 { font-size: 17pt; line-height: 1.35; border-bottom: 2px solid #334c62; padding-bottom: 7pt; margin: 0 0 11pt; }
h2 { font-size: 13pt; margin: 15pt 0 5pt; color: #25445c; border-bottom: .5pt solid #c6d1db; padding-bottom: 3pt; }
h3,h4,h5,h6 { font-size: 11pt; margin: 9pt 0 4pt; color: #25445c; }
h1,h2,h3,h4,h5,h6 { break-after: avoid; }
p { margin: 0 0 6pt; orphans: 2; widows: 2; }
ul,ol { padding-left: 17pt; margin: 4pt 0 8pt; }
li { margin-bottom: 3pt; }
blockquote { margin: 6pt 0 10pt; padding: 5pt 8pt; border-left: 2pt solid #607c91; background: #f1f5f8; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; margin: 6pt 0 9pt; font-size: 9.5pt; line-height: 1.4; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th,td { border: .5pt solid #a8b5c1; padding: 4pt 5pt; vertical-align: top; overflow-wrap: anywhere; }
th { background: #e6edf3; text-align: left; font-weight: 700; }
code,pre { font-family: "Noto Sans CJK KR", sans-serif; font-size: 9.5pt; white-space: pre-wrap; overflow-wrap: anywhere; }
a { color: #25445c; text-decoration: none; }
'''


def fingerprints(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob': hashlib.sha1(f'blob {len(data)}'.encode() + b'\0' + data).hexdigest()}


def norm(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', text).replace('\u00ad', ''))


def render(source, out, expected_blob=None):
    import fitz
    import mistune
    from bs4 import BeautifulSoup
    from weasyprint import HTML, CSS as Stylesheet
    source, out = Path(source).resolve(), Path(out).resolve()
    if out == source.parent or out.is_relative_to(source.parent):
        raise ValueError('Output must not be inside source directory')
    raw = source.read_bytes()
    identity = fingerprints(raw)
    if expected_blob and identity['git_blob'] != expected_blob:
        raise ValueError('Markdown blob differs from expected source')
    match = subprocess.check_output(['fc-match', '-f', '%{family}', FONT], text=True)
    if FONT not in match.split(','):
        raise RuntimeError('Required Korean font not installed: ' + FONT)
    out.mkdir(parents=True, exist_ok=False)
    md = mistune.create_markdown(escape=True, plugins=['table', 'strikethrough'])
    soup = BeautifulSoup(md(raw.decode('utf-8')), 'html.parser')
    unsupported = []
    for image in soup.find_all('img'):
        unsupported.append('Image not rendered; alt text retained')
        image.replace_with(image.get('alt', '') or '[이미지]')
    for a in soup.find_all('a'):
        a.unwrap()
    nodes = soup.find_all(['h1','h2','h3','h4','h5','h6','p','li','td','th','pre'])
    expected = [norm(n.get_text()) for n in nodes if not n.find(['h1','h2','h3','h4','h5','h6','p','li','td','th','pre']) and norm(n.get_text())]
    title = soup.h1.get_text() if soup.h1 else source.stem
    body = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>' + html.escape(title) + '</title></head><body>' + str(soup) + '</body></html>'
    def no_fetch(url, *args, **kwargs):
        raise ValueError('External resource fetch prohibited: ' + url)
    pdf = out / 'report_a4.pdf'
    HTML(string=body, url_fetcher=no_fetch).write_pdf(pdf, stylesheets=[Stylesheet(string=CSS, url_fetcher=no_fetch)])
    flags, pages, fonts, all_text = [], [], {}, []
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            text = page.get_text()
            all_text.append(page.get_text(clip=fitz.Rect(0, 53, page.rect.width, page.rect.height-50)))
            issues = []
            if abs(page.rect.width - 595.276) > 1 or abs(page.rect.height - 841.89) > 1:
                issues.append('NOT_A4')
            if '\ufffd' in text or '\x00' in text:
                issues.append('REPLACEMENT_GLYPH')
            spans = [s for b in page.get_text('dict')['blocks'] if b['type']==0 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
            for s in spans:
                x0,y0,x1,y1 = s['bbox']
                if x0 < 48 or x1 > page.rect.width-48 or y0 < 0 or y1 > page.rect.height:
                    issues.append('TEXT_OUTSIDE_MARGIN')
                if y0 > 53 and y1 < page.rect.height-50 and s['size'] < 8.5:
                    issues.append('SMALL_BODY_TEXT')
            for font in page.get_fonts():
                xref = font[0]
                if xref not in fonts:
                    extracted = doc.extract_font(xref)
                    fonts[xref] = {'name':font[3], 'embedded':bool(extracted[3])}
            body_spans = [s for s in spans if 53 < s['bbox'][1] < page.rect.height-50]
            if not body_spans:
                issues.append('EMPTY_BODY')
            elif i == len(doc) and len(doc)>1 and len(''.join(s['text'] for s in body_spans)) < 80:
                issues.append('SPARSE_FINAL_PAGE')
            page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(out/f'page-{i:02d}.png')
            issues = sorted(set(issues))
            pages.append({'page':i,'size_pt':[round(page.rect.width,2),round(page.rect.height,2)],'text_chars':len(text),'flags':issues})
            flags.extend(issues)
    actual = norm(''.join(all_text))
    missing = [i+1 for i,x in enumerate(expected) if x not in actual]
    if missing:
        flags.append('TEXT_COMPLETENESS_HEURISTIC')
    if not fonts or any(not f['embedded'] for f in fonts.values()):
        flags.append('FONT_NOT_EMBEDDED')
    if any('NotoSansCJKKR' not in re.sub(r'[^A-Za-z]','',f['name']) for f in fonts.values()):
        flags.append('FONT_SUBSTITUTION_POSSIBLE')
    if unsupported:
        flags.append('UNSUPPORTED_MARKDOWN_MEDIA')
    if source.read_bytes()!=raw:
        raise RuntimeError('Source changed during rendering')
    result = {'source':source.name,'source_hash':identity,'pdf_hash':fingerprints(pdf.read_bytes()),
              'engine':{'weasyprint':version('weasyprint'),'mistune':version('mistune'),'pymupdf':version('pymupdf')},
              'pages':len(pages),'page_details':pages,'tables':len(soup.find_all('table')),
              'expected_text_blocks':len(expected),'missing_text_block_indices':missing,
              'fonts':list(fonts.values()),'flags':sorted(set(flags)),'unsupported':unsupported,
              'status':'REVIEW_RENDER_FLAGS' if flags else 'RENDERED_MANUAL_REVIEW_REQUIRED',
              'visual_review':'PENDING','can_ship':False,
              'limitations':['Text extraction checks are heuristic; table clipping, layout and readability require visual review.',
                             'No fixed page limit or automatic content reduction; source Markdown unchanged.']}
    (out/'report_a4_qc.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('--out',required=True)
    p.add_argument('--expected-blob')
    a=p.parse_args()
    r=render(a.source,a.out,a.expected_blob)
    print(json.dumps({k:r[k] for k in ['pages','tables','expected_text_blocks','missing_text_block_indices','flags','status']},ensure_ascii=False))
    return int(bool(r['flags']))

if __name__=='__main__':
    raise SystemExit(main())
