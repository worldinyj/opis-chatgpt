"""Synthetic application connection and expert draft service on C02-R2."""
import sqlite3
import re
import c02_r2 as core
import c09_guard as guard
from c04_consensus import RULE


def connect():
    db=core.connect()
    guard.install(db)
    return db


def reopen(path):
    db=sqlite3.connect(path,timeout=0.1)
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA recursive_triggers=ON')
        db.create_function('location_ok',5,core.location_ok)
        db.create_function('snapshot_digest',1,lambda sid:core.digest(db,sid))
        guard.register(db)
        required={'c09_consensus_insert','c09_expert_insert','r2_seal','r1_seal'}
        names={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
        if not required<=names or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('guard or integrity missing')
        return db
    except BaseException:
        db.close();raise


def submit(db,role,actor,snapshot,key,fingerprint,revision,decision,reason):
    if role!='EXPERT':raise PermissionError('expert only')
    if not isinstance(actor,str) or not re.fullmatch(r'fixture:[A-Za-z0-9_-]+',actor):raise ValueError('fixture actor')
    if type(revision) is not int or revision<0 or decision not in ('SELECTED','NOT_SELECTED','DEFERRED') or not isinstance(reason,str) or not 0<len(reason.strip())<=4000 or db.in_transaction:raise ValueError('invalid draft')
    with db:
        db.execute('BEGIN IMMEDIATE')
        head=db.execute('SELECT id,fingerprint FROM snapshot WHERE sealed=1 ORDER BY id DESC LIMIT 1').fetchone()
        if head!=(snapshot,fingerprint):raise ValueError('stale snapshot')
        if core.digest(db,snapshot)!=fingerprint:raise ValueError('digest mismatch')
        row=db.execute('SELECT status FROM consensus WHERE snapshot=? AND key=? AND rule_version=?',(snapshot,key,RULE)).fetchone()
        if not row or row[0] not in ('INTERNAL_CONSENSUS_SELECTED','EXPERT_REVIEW_REQUIRED'):raise ValueError('pending')
        last=db.execute('SELECT id,revision FROM expert_review WHERE snapshot=? AND key=? ORDER BY revision DESC LIMIT 1',(snapshot,key)).fetchone()
        if revision!=(last[1] if last else 0):raise ValueError('revision conflict')
        rid=db.execute("INSERT INTO expert_review(snapshot,key,revision,decision,rationale,actor,at,supersedes,approval_state) VALUES(?,?,?,?,?,?,'2000-01-01',?,'DRAFT')",(snapshot,key,revision+1,decision,reason.strip(),actor,last[0] if last else None)).lastrowid
        db.execute("INSERT INTO audit_event(actor,action,target,at,reason) VALUES(?,'EXPERT_DRAFT',?,'2000-01-01',?)",(actor,str(rid),fingerprint))
    return rid
