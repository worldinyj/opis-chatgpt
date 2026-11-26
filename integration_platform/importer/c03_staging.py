"""C03 synthetic-only staging importer. No production import or eligibility approval."""
import csv
import hashlib
import io
import json
import re
import sqlite3
import stat
import unittest
import zipfile

FILES = {'review.json', 'excel_import.csv', 'report.md', 'validation.md'}
HEADER = 'review_key,queue_id,event_id,attribute_code,review_result,rationale,source'.split(',')
CODES = tuple(f'{p}{i}' for p, n in [('PA',3),('QA',4),('CO',4),('LA',8),('DM',3),('WE',4),('CL',4),('PI',4),('RC',2),('WP',4)] for i in range(1,n+1))
ROLE = dict(D='선정', I='선정', A='판단보류', H='미선정', P='미선정', N='미선정')
EMPTY = '해당 원문 근거 없음'
LIMIT = 2_000_000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def unpack(data):
    require(len(data) <= LIMIT, 'ZIP size')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        entries = z.infolist()
        require(len(entries) == 4 and {i.filename for i in entries} == FILES, 'ZIP exact paths')
        require(sum(i.file_size for i in entries) <= LIMIT, 'ZIP expanded size')
        for i in entries:
            mode = stat.S_IFMT(i.external_attr >> 16)
            require(mode in (0, stat.S_IFREG) and not i.is_dir() and not i.flag_bits & 1, 'ZIP special or encrypted entry')
            require(i.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), 'ZIP compression')
        return {i.filename: z.read(i) for i in entries}


def location(loc, pages):
    require(type(loc) is dict and set(loc) == {'section','printed_pages','pdf_pages','summary'}, 'location shape')
    require(loc['section'] is None or type(loc['section']) is str, 'section type')
    for field in ('printed_pages','pdf_pages'):
        a = loc[field]
        require(type(a) is list and all(type(p) is int and p > 0 for p in a) and len(set(a)) == len(a), 'page list')
    require(all(p <= pages for p in loc['pdf_pages']), 'physical page range')
    require(bool(loc['printed_pages'] or loc['pdf_pages'] or (loc['section'] or '').strip()), 'empty location')
    require(type(loc['summary']) is str and bool(loc['summary'].strip()), 'location summary')


def unsafe(s):
    return bool(re.match(r'^[=+\-@\t\r\n]', s.lstrip(' ')) or re.match(r'^[=+\-@]', s.lstrip()))


def parse_csv(data):
    s = data.decode('utf-8-sig')
    state = 'start'
    for i, ch in enumerate(s):
        if state == 'quoted':
            if ch == '"': state = 'closed'
        elif state == 'closed' and ch == '"': state = 'quoted'
        elif ch == ',': state = 'start'
        elif ch == '\n' or (ch == '\r' and s[i+1:i+2] == '\n'): state = 'start'
        elif ch == '"' and state == 'start': state = 'quoted'
        elif ch in ('"','\r') or state == 'closed': raise ValueError('CSV quote syntax')
        else: state = 'plain'
    require(state != 'quoted', 'CSV unclosed quote')
    rows = list(csv.reader(io.StringIO(s, newline=''), strict=True))
    require(len(rows) == 41 and rows[0] == HEADER and all(len(r) == 7 for r in rows), 'CSV shape')
    return rows[1:]


def validate(files):
    j = json.loads(files['review.json'].decode('utf-8'), object_pairs_hook=unique,
                   parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
    require(type(j) is dict and set(j) == {'fixture','queue_id','event_id','model','revision','source','facts','attributes','approved','can_ship'}, 'fixture contract')
    require(j['fixture'] == 'SYNTHETIC_ONLY' and re.fullmatch(r'SYNTHETIC-\d{3}',j['queue_id']) and re.fullmatch(r'FIXTURE-E\d{3}',j['event_id']), 'synthetic identity only')
    require(j['model'] in ('CHATGPT','GEMINI','CLAUDE') and type(j['revision']) is int and j['revision'] > 0, 'model/revision')
    require(j['approved'] is False and j['can_ship'] is False, 'approval prohibited')
    src = j['source']
    require(type(src) is dict and set(src) == {'sha256','pages','verification'} and re.fullmatch(r'[a-f0-9]{64}',src['sha256']) and type(src['pages']) is int and src['pages'] > 0 and src['verification'] == 'SYNTHETIC_NOT_PDF_VERIFIED', 'synthetic source')
    facts = j['facts']; attrs = j['attributes']
    require(type(facts) is list and type(attrs) is list and len(attrs) == 40, '40 attributes')
    ledger = {}
    for f in facts:
        require(type(f) is dict and set(f) == {'id','summary','source_refs'} and re.fullmatch(j['model']+r'-F\d{2,}',f['id']) and f['id'] not in ledger and type(f['summary']) is str and f['summary'].strip(), 'fact identity')
        require(type(f['source_refs']) is list and bool(f['source_refs']), 'fact location')
        for loc in f['source_refs']: location(loc,src['pages'])
        ledger[f['id']] = f
    by_key = {}
    for a in attrs:
        require(type(a) is dict and set(a) == {'review_key','code','role','review_result','rationale','fact_ids','source_refs'}, 'attribute shape')
        key = a['review_key']; code = a['code']; role = a['role']
        require(code in CODES and key == j['queue_id']+'-'+code and key not in by_key and role in ROLE and ROLE[role] == a['review_result'], 'attribute identity/role')
        require(type(a['rationale']) is str and a['rationale'].strip() and not unsafe(a['rationale']), 'rationale')
        ids, refs = a['fact_ids'],a['source_refs']
        require(type(ids) is list and all(type(f) is str and f in ledger for f in ids) and len(set(ids)) == len(ids) and type(refs) is list and bool(ids) == bool(refs), 'fact links')
        require(role not in ('D','I') or bool(ids), 'selected without evidence')
        for loc in refs: location(loc,src['pages'])
        for field in ('printed_pages','pdf_pages'):
            linked = {p for f in ids for loc in ledger[f]['source_refs'] for p in loc[field]}
            require(all(p in linked for loc in refs for p in loc[field]), 'ledger page gap')
        by_key[key] = a
    require({a['code'] for a in attrs} == set(CODES), 'standard coverage')
    seen = set()
    for key,q,e,code,result,rationale,source in parse_csv(files['excel_import.csv']):
        a = by_key.get(key)
        require(a is not None and key not in seen and (q,e,code,result,rationale) == (j['queue_id'],j['event_id'],a['code'],a['review_result'],a['rationale']), 'CSV/JSON mismatch')
        require(not any(unsafe(v) for v in (key,q,e,code,result,rationale,source)), 'CSV formula prefix')
        require(set(re.findall(r'(?:CHATGPT|GEMINI|CLAUDE)-F\d{2,}',source)) == set(a['fact_ids']), 'CSV fact mismatch')
        require(bool(a['fact_ids']) or source == EMPTY, 'empty source')
        seen.add(key)
    for name in ('report.md','validation.md'):
        require(files[name].decode('utf-8').startswith('SYNTHETIC_ONLY\n'), 'fixture marker')
    return j


def connect():
    db = sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE package(id INTEGER PRIMARY KEY, queue TEXT NOT NULL, event TEXT NOT NULL, model TEXT NOT NULL, revision INTEGER NOT NULL, content_hash TEXT NOT NULL, state TEXT NOT NULL CHECK(state='STAGED_NOT_ELIGIBLE'), UNIQUE(queue,model,revision));
    CREATE TABLE artifact(package INTEGER REFERENCES package NOT NULL, name TEXT NOT NULL, hash TEXT NOT NULL, content BLOB NOT NULL, PRIMARY KEY(package,name));
    CREATE TABLE judgment(package INTEGER REFERENCES package NOT NULL, review_key TEXT NOT NULL, role TEXT NOT NULL, result TEXT NOT NULL, rationale TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(package,review_key));
    CREATE TABLE audit(id INTEGER PRIMARY KEY, content_hash TEXT NOT NULL, action TEXT NOT NULL, reason TEXT NOT NULL);
    ''')
    for table in ('package','artifact','judgment','audit'):
        for action in ('UPDATE','DELETE'):
            db.execute(f"CREATE TRIGGER {table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'append only'); END")
    return db


def ingest(db, data):
    files = unpack(data)
    j = validate(files)
    fingerprint = sha(json.dumps(sorted((n,sha(v)) for n,v in files.items()),separators=(',',':')).encode())
    identity = (j['queue_id'],j['model'],j['revision'])
    require(not db.in_transaction, 'caller transaction prohibited')
    with db:
        db.execute('BEGIN IMMEDIATE')
        old = db.execute('SELECT content_hash FROM package WHERE queue=? AND model=? AND revision=?',identity).fetchone()
        if old:
            status = 'NOOP' if old[0] == fingerprint else 'CONFLICT_QUARANTINED'
            db.execute('INSERT INTO audit(content_hash,action,reason) VALUES(?,?,?)',(fingerprint,status,'existing revision'))
            return status
        cursor = db.execute("INSERT INTO package(queue,event,model,revision,content_hash,state) VALUES(?,?,?,?,?,'STAGED_NOT_ELIGIBLE')",(j['queue_id'],j['event_id'],j['model'],j['revision'],fingerprint))
        pid = cursor.lastrowid
        db.executemany('INSERT INTO artifact VALUES(?,?,?,?)',[(pid,n,sha(v),v) for n,v in files.items()])
        db.executemany('INSERT INTO judgment VALUES(?,?,?,?,?,?)',[(pid,a['review_key'],a['role'],a['review_result'],a['rationale'],json.dumps(a,ensure_ascii=False)) for a in j['attributes']])
        db.execute('INSERT INTO audit(content_hash,action,reason) VALUES(?,?,?)',(fingerprint,'STAGED','synthetic only'))
    return 'STAGED'


def fixture():
    q,e,model='SYNTHETIC-001','FIXTURE-E001','GEMINI'
    loc={'section':'fixture','printed_pages':[1],'pdf_pages':[1],'summary':'fixture'}
    j={'fixture':'SYNTHETIC_ONLY','queue_id':q,'event_id':e,'model':model,'revision':1,'source':{'sha256':'a'*64,'pages':2,'verification':'SYNTHETIC_NOT_PDF_VERIFIED'},'facts':[{'id':'GEMINI-F01','summary':'fixture','source_refs':[loc]}],'attributes':[],'approved':False,'can_ship':False}
    for i,code in enumerate(CODES):
        j['attributes'].append({'review_key':q+'-'+code,'code':code,'role':'D' if i==0 else 'N','review_result':'선정' if i==0 else '미선정','rationale':'fixture, "quoted"\nline','fact_ids':['GEMINI-F01'] if i==0 else [],'source_refs':[loc.copy()] if i==0 else []})
    return j


def make_files(j):
    s=io.StringIO(newline=''); w=csv.writer(s); w.writerow(HEADER)
    for a in j['attributes']:
        w.writerow([a['review_key'],j['queue_id'],j['event_id'],a['code'],a['review_result'],a['rationale'],';'.join(a['fact_ids']) if a['fact_ids'] else EMPTY])
    return {'review.json':json.dumps(j,ensure_ascii=False).encode(),'excel_import.csv':s.getvalue().encode(),'report.md':b'SYNTHETIC_ONLY\nfixture','validation.md':b'SYNTHETIC_ONLY\nfixture'}


def zip_bytes(files):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
        for n,v in files.items(): z.writestr(n,v)
    return stream.getvalue()


class Tests(unittest.TestCase):
    def setUp(self): self.db=connect(); self.j=fixture()
    def tearDown(self): self.db.close()
    def run_import(self): return ingest(self.db,zip_bytes(make_files(self.j)))
    def reject(self):
        with self.assertRaises((ValueError,TypeError,KeyError,AttributeError,zipfile.BadZipFile)): self.run_import()
        self.assertEqual(self.db.execute('SELECT count(*) FROM package').fetchone()[0],0)
    def test_positive(self):
        self.assertEqual(self.run_import(),'STAGED'); self.assertEqual(self.db.execute('SELECT count(*) FROM judgment').fetchone()[0],40)
        self.assertEqual(self.db.execute('SELECT count(*) FROM artifact').fetchone()[0],4)
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_noop(self): self.run_import(); self.assertEqual(self.run_import(),'NOOP')
    def test_conflict(self):
        self.run_import(); self.j['attributes'][0]['rationale']='changed'; self.assertEqual(self.run_import(),'CONFLICT_QUARANTINED'); self.assertEqual(self.db.execute('SELECT count(*) FROM judgment').fetchone()[0],40)
    def test_revision(self): self.run_import(); self.j['revision']=2; self.assertEqual(self.run_import(),'STAGED')
    def test_real_identity(self): self.j['queue_id']='ROOT-014'; self.reject()
    def test_approval(self): self.j['approved']=True; self.reject()
    def test_partial(self): self.j['attributes'].pop(); self.reject()
    def test_duplicate(self): self.j['attributes'][1]=self.j['attributes'][0]; self.reject()
    def test_role(self): self.j['attributes'][0]['role']='N'; self.reject()
    def test_fact(self): self.j['attributes'][0]['fact_ids']=['GEMINI-F99']; self.reject()
    def test_source_range(self): self.j['attributes'][0]['source_refs'][0]['pdf_pages']=[3]; self.reject()
    def test_ledger_gap(self): self.j['attributes'][0]['source_refs'][0]['printed_pages']=[99]; self.reject()
    def test_formula(self): self.j['attributes'][0]['rationale']=' =SUM(A1)'; self.reject()
    def test_traversal(self):
        files=make_files(self.j); files['../report.md']=files.pop('report.md')
        with self.assertRaises(ValueError): ingest(self.db,zip_bytes(files))
    def test_expansion(self):
        files=make_files(self.j); files['report.md']=b'a'*(LIMIT+1)
        with self.assertRaises(ValueError): ingest(self.db,zip_bytes(files))
    def test_duplicate_json(self):
        files=make_files(self.j); files['review.json']=b'{"fixture":1,"fixture":2}'
        with self.assertRaises(ValueError): ingest(self.db,zip_bytes(files))
    def test_csv_mismatch(self):
        files=make_files(self.j); files['excel_import.csv']=files['excel_import.csv'].replace('선정'.encode(),'미선정'.encode(),1)
        with self.assertRaises(ValueError): ingest(self.db,zip_bytes(files))
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER test_failure BEFORE INSERT ON judgment WHEN NEW.review_key LIKE '%-WP4' BEGIN SELECT RAISE(ABORT,'forced'); END")
        with self.assertRaises(sqlite3.IntegrityError): self.run_import()
        for table in ('package','artifact','judgment','audit'): self.assertEqual(self.db.execute(f'SELECT count(*) FROM {table}').fetchone()[0],0)


if __name__=='__main__': unittest.main(verbosity=2)
