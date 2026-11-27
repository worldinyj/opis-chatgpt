"""C06 synthetic expert-review service; isolated SQLite, no real approval."""
import re
import sqlite3
import unittest


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def authorize(role, write=False):
    if role not in (('EXPERT',) if write else ('EXPERT','READER','QA')):
        raise PermissionError('review access denied')


def connect():
    db=sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA recursive_triggers=ON')
    db.executescript('''
    CREATE TABLE snapshots(fingerprint TEXT PRIMARY KEY, sealed INTEGER NOT NULL CHECK(sealed=1));
    CREATE TABLE cases(fingerprint TEXT REFERENCES snapshots, key TEXT, status TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(fingerprint,key));
    CREATE TABLE current_snapshot(id INTEGER PRIMARY KEY CHECK(id=1),fingerprint TEXT NOT NULL REFERENCES snapshots);
    CREATE TABLE review(id INTEGER PRIMARY KEY,fingerprint TEXT NOT NULL,key TEXT NOT NULL,revision INTEGER NOT NULL,decision TEXT NOT NULL CHECK(decision IN ('SELECTED','NOT_SELECTED','DEFERRED')),reason TEXT NOT NULL,actor TEXT NOT NULL,supersedes INTEGER REFERENCES review,approval TEXT NOT NULL CHECK(approval='DRAFT'),FOREIGN KEY(fingerprint,key) REFERENCES cases,UNIQUE(fingerprint,key,revision));
    CREATE TABLE audit(id INTEGER PRIMARY KEY, review_id INTEGER NOT NULL REFERENCES review, action TEXT NOT NULL);
    ''')
    for table in ('snapshots','cases','review','audit'):
        for action in ('UPDATE','DELETE'):
            db.execute(f"CREATE TRIGGER immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'append only'); END")
    return db


def detail(db,role,key):
    authorize(role)
    require(re.fullmatch(r'SYNTHETIC-\d{3}-[A-Z]{2}[1-8]',key),'synthetic key only')
    row=db.execute('SELECT c.fingerprint,c.status,c.payload FROM cases c JOIN current_snapshot s ON s.fingerprint=c.fingerprint WHERE c.key=?',(key,)).fetchone()
    require(row is not None,'unknown key')
    fp,status,payload=row
    latest=db.execute('SELECT id,revision,decision,reason,actor FROM review WHERE fingerprint=? AND key=? ORDER BY revision DESC LIMIT 1',(fp,key)).fetchone()
    prior=db.execute('SELECT count(*) FROM review WHERE key=? AND fingerprint<>?',(key,fp)).fetchone()[0]
    return dict(fingerprint=fp,key=key,status=status,payload=payload,revision=latest[1] if latest else 0,latest=latest,stale_review_required=bool(prior and not latest),approved=False,can_ship=False)


def submit(db,role,actor,key,fingerprint,expected_revision,decision,reason):
    authorize(role,True)
    require(type(actor) is str and actor.startswith('fixture:') and len(actor)>8,'synthetic actor only')
    require(type(expected_revision) is int and expected_revision>=0,'revision')
    require(decision in ('SELECTED','NOT_SELECTED','DEFERRED') and type(reason) is str and 0<len(reason.strip())<=4000,'decision/reason')
    require(not db.in_transaction,'caller transaction')
    with db:
        db.execute('BEGIN IMMEDIATE')
        current=detail(db,role,key)
        require(current['fingerprint']==fingerprint,'stale snapshot')
        require(current['revision']==expected_revision,'revision conflict')
        require(current['status'] in ('INTERNAL_CONSENSUS_SELECTED','EXPERT_REVIEW_REQUIRED'),'pending inputs cannot be decided')
        prior=current['latest'][0] if current['latest'] else None
        rid=db.execute("INSERT INTO review(fingerprint,key,revision,decision,reason,actor,supersedes,approval) VALUES(?,?,?,?,?,?,?,'DRAFT')",(fingerprint,key,expected_revision+1,decision,reason.strip(),actor,prior)).lastrowid
        db.execute("INSERT INTO audit(review_id,action) VALUES(?,'DRAFT_RECORDED')",(rid,))
    return rid


class Tests(unittest.TestCase):
    key='SYNTHETIC-001-PA1'
    def setUp(self):
        self.db=connect()
        with self.db:
            self.db.execute('INSERT INTO snapshots VALUES(?,1)',('a'*64,))
            self.db.execute('INSERT INTO cases VALUES(?,?,?,?)',('a'*64,self.key,'EXPERT_REVIEW_REQUIRED','fixture evidence'))
            self.db.execute('INSERT INTO cases VALUES(?,?,?,?)',('a'*64,'SYNTHETIC-001-PA2','PENDING_INPUT','fixture pending'))
            self.db.execute('INSERT INTO current_snapshot VALUES(1,?)',('a'*64,))
    def tearDown(self): self.db.close()
    def save(self,role='EXPERT',revision=0,fp='a'*64,key=None,reason='fixture reason'):
        return submit(self.db,role,'fixture:reviewer',key or self.key,fp,revision,'SELECTED',reason)
    def test_read_roles(self):
        for role in ('QA','READER','EXPERT'): self.assertEqual(detail(self.db,role,self.key)['revision'],0)
    def test_denied(self):
        self.assertRaises(PermissionError,detail,self.db,'ANONYMOUS',self.key)
        self.assertRaises(PermissionError,self.save,'READER')
    def test_revision_chain(self):
        a=self.save();b=self.save(revision=1)
        self.assertEqual(self.db.execute('SELECT supersedes,approval FROM review WHERE id=?',(b,)).fetchone(),(a,'DRAFT'))
    def test_conflict(self): self.save();self.assertRaises(ValueError,self.save)
    def test_pending(self): self.assertRaises(ValueError,self.save,key='SYNTHETIC-001-PA2')
    def test_stale(self):
        self.save()
        with self.db:
            self.db.execute('INSERT INTO snapshots VALUES(?,1)',('b'*64,));self.db.execute('INSERT INTO cases VALUES(?,?,?,?)',('b'*64,self.key,'EXPERT_REVIEW_REQUIRED','new fixture'));self.db.execute('UPDATE current_snapshot SET fingerprint=?',('b'*64,))
        self.assertTrue(detail(self.db,'EXPERT',self.key)['stale_review_required']);self.assertRaises(ValueError,self.save,fp='a'*64)
        self.save(fp='b'*64);self.assertFalse(detail(self.db,'EXPERT',self.key)['stale_review_required'])
    def test_empty_reason(self): self.assertRaises(ValueError,self.save,reason='  ')
    def test_immutable(self):
        self.save()
        with self.assertRaises(sqlite3.IntegrityError): self.db.execute("UPDATE review SET reason='altered'")
    def test_rollback(self):
        self.db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT,'forced'); END")
        self.assertRaises(sqlite3.IntegrityError,self.save);self.assertEqual(self.db.execute('SELECT count(*) FROM review').fetchone()[0],0)
    def test_no_real(self): self.assertRaises(ValueError,detail,self.db,'EXPERT','ROOT-001-PA1')

if __name__=='__main__': unittest.main(verbosity=2)
