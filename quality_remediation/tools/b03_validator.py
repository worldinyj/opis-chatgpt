"""Read-only B03 verifier. No derivative files or approvals are produced."""
import csv, hashlib, io, json, re, subprocess
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator, FormatChecker

HEADER = 'review_key,queue_id,event_id,attribute_code,review_result,rationale,source'.split(',')
FACT = re.compile(r'(?:GEMINI|CLAUDE)-F\d{2,}')
EMPTY = '해당 원문 근거 없음'
ROLE = dict(D='선정', I='선정', A='판단보류', H='미선정', P='미선정', N='미선정')


def unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('duplicate JSON key: '+k)
        out[k] = v
    return out


def parse_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def read_pin(repo, ref, path, blob, sha256=None):
    if not re.fullmatch(r'[0-9a-f]{40}', ref) or not re.fullmatch(r'[0-9a-f]{40}', blob):
        raise ValueError('unpinned reference')
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or str(p) != path or '\\' in path or path.startswith('-'):
        raise ValueError('unsafe path')
    def git(*args):
        return subprocess.check_output(['git','--literal-pathspecs','-C',str(repo),*args])
    entry = git('ls-tree','-z',ref,'--',path)
    expected = ('100644 blob '+blob+'\t'+path+'\0').encode()
    if entry != expected:
        raise ValueError('blob or regular file mismatch: '+path)
    data = git('cat-file','blob',blob)
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() != blob:
        raise ValueError('blob bytes mismatch')
    if sha256 is not None and hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError('SHA256 mismatch: '+path)
    return data


def parse_csv(raw):
    bom = raw.startswith(b'\xef\xbb\xbf')
    s = raw.decode('utf-8-sig')
    # Reject bare quotes, post-quote junk, and CR outside quoted fields except CRLF.
    state = 'start'
    for i, ch in enumerate(s):
        if state == 'quoted':
            if ch == '"': state = 'closed'
        elif state == 'closed' and ch == '"': state = 'quoted'
        elif ch == ',': state = 'start'
        elif ch == '\n' or (ch == '\r' and s[i+1:i+2] == '\n'): state = 'start'
        elif ch == '"' and state == 'start': state = 'quoted'
        elif ch in ('"','\r') or state == 'closed': raise ValueError('malformed CSV quoting')
        else: state = 'plain'
    if state == 'quoted': raise ValueError('unclosed CSV quote')
    rows = list(csv.reader(io.StringIO(s, newline=''), strict=True))
    if not rows or rows[0] != HEADER or len(rows) != 41 or any(len(r)!=7 for r in rows):
        raise ValueError('CSV header/row/column count')
    return [dict(zip(HEADER,r)) for r in rows[1:]], bom


def unsafe(s):
    t = s.lstrip(' ')
    return bool(t and (t[0] in '=+-@\t\r\n' or t.lstrip()[:1] in ('=','+','-','@')))


def verify(review, raw_csv, schema, standard, expected):
    issues, repairs = [], []
    def issue(code, key=''): issues.append([code,key])
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(review))
    if errors:
        return {'issues':[['SCHEMA', '/'.join(map(str,e.absolute_path))] for e in errors], 'repairs':[], 'candidate':False}
    rows,bom = parse_csv(raw_csv)
    names = {a['code']:a['name'] for p in standard['principles'] for a in p['attributes']}
    attrs = review['attributes']; facts = review['facts']; ledger = {f['id']:f for f in facts}
    q,e = expected['queue_id'],expected['event_id']
    if review['queue_id']!=q or review['event_id']!=e or review['model']['provider']!='GEMINI': issue('IDENTITY')
    if len(names)!=40 or len(attrs)!=40 or {a['code'] for a in attrs}!=set(names): issue('ATTRIBUTE_SET')
    if len(ledger)!=len(facts) or any(not re.fullmatch(r'GEMINI-F\d{2,}',f) for f in ledger): issue('FACT_ID')
    bykey={r['review_key']:r for r in rows}
    if len(bykey)!=40 or set(bykey)!={q+'-'+c for c in names}: issue('CSV_KEY_SET')
    source=review['source']; pages=source['pdf_page_count']; exp=expected['expected_pdf']
    if source['sha256']!=exp['sha256'] or pages!=exp['pages'] or source['verification']!='BINARY_HASH_VERIFIED': issue('SOURCE_IDENTITY_UNVERIFIED')
    if q=='ROOT-004': issue('MANUAL_ROOT004')
    for f in facts:
        for ref in f['source_refs']:
            if pages is not None and any(p>pages for p in ref['pdf_pages']): issue('PDF_RANGE',f['id'])
    for a in attrs:
        k=a['review_key']; r=bykey.get(k); ids=a['fact_ids']; refs=a['source_refs']
        if k!=q+'-'+a['code'] or names.get(a['code'])!=a['name'] or ROLE.get(a['role'])!=a['review_result']: issue('ATTRIBUTE_ID_ROLE',k)
        if any(f not in ledger for f in ids): issue('UNKNOWN_FACT',k)
        if bool(ids)!=bool(refs) or (a['role'] in ('D','I') and not ids): issue('EVIDENCE_INCOMPLETE',k)
        for field in ('printed_pages','pdf_pages'):
            linked={p for f in ids if f in ledger for ref in ledger[f]['source_refs'] for p in ref[field]}
            cited={p for ref in refs for p in ref[field]}
            if cited-linked: issue('LEDGER_GAP_'+field,k)
            if field=='pdf_pages' and pages is not None and any(p>pages for p in cited): issue('PDF_RANGE',k)
        if r is None: continue
        if (r['queue_id'],r['event_id'],r['attribute_code'],r['review_result'])!=(q,e,a['code'],a['review_result']): issue('CSV_DECISION_ID',k)
        if set(FACT.findall(r['source']))!=set(ids): issue('CSV_FACT_SET',k)
        if r['rationale']!=a['rationale']:
            if re.fullmatch(r'\['+a['role']+r'\][ \t]+'+re.escape(a['rationale']),r['rationale']): repairs.append(['ROLE_PREFIX',k])
            else: issue('RATIONALE_CHANGED',k)
        if not ids and not refs and r['source']!=EMPTY: repairs.append(['EMPTY_SOURCE',k])
        if refs: repairs.append(['SERIALIZE_SOURCE',k])
        if any(unsafe(v) for v in r.values()) or unsafe(a['rationale']): issue('FORMULA_PREFIX',k)
    return {'issues':issues,'repairs':repairs,'bom':bom,'candidate':not issues,
            'approved':False,'can_ship':False,'semantic_validation':False}


def verify_case(repo, manifest, queue_id):
    ref=manifest['source_ref']; cases=[c for c in manifest['cases'] if c['queue_id']==queue_id]
    if len(cases)!=1: raise ValueError('unknown or duplicate case')
    c=cases[0]; pins=manifest['reference_blobs']; data={}
    for path,blob in pins.items(): data[path]=read_pin(repo,ref,path,blob)
    originals={}
    for f in c['original_files']:
        if f['path']!=c['source_path']+f['name'] or f['name'] in originals: raise ValueError('manifest path mismatch')
        if f['name']!='INTAKE_STATUS.json' and not re.fullmatch(r'[0-9a-f]{64}',f.get('sha256','')): raise ValueError('missing original SHA256')
        originals[f['name']]=read_pin(repo,ref,f['path'],f['blob'],f.get('sha256'))
    if set(originals)!={'report.md','review.json','excel_import.csv','validation.md','INTAKE_STATUS.json'}: raise ValueError('missing original artifact')
    return verify(parse_json(originals['review.json']),originals['excel_import.csv'],parse_json(data['standards/independent_ai_review_v1.schema.json']),parse_json(data['standards/safety_culture_40.json']),c)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('repo')
    parser.add_argument('queue_id',choices=['ROOT-004','ROOT-014','ROOT-015','ROOT-017','ROOT-018','ROOT-019','ROOT-020'])
    args=parser.parse_args()
    try:
        manifest=parse_json(read_pin(args.repo,'62914d6c2b60cd250edd2bc4047addd6f806f053','quality_remediation/HOLD_MANIFEST_V1.json','5c79edd86f4bcbd9d8ac648b389967610d43802d'))
        result=verify_case(args.repo,manifest,args.queue_id)
    except (ValueError, KeyError, subprocess.CalledProcessError, UnicodeError, csv.Error) as exc:
        result={'candidate':False,'error':str(exc),'approved':False,'can_ship':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['candidate'] else 2)
