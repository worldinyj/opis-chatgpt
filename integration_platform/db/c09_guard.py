"""C09-R1 opt-in synthetic insert guards; privileged SQL remains out of scope."""
import json
from c04_consensus import Slot, evaluate, RULE


def expected(db,sid,key):
    head=db.execute('SELECT fingerprint,sealed FROM snapshot WHERE id=?',(sid,)).fetchone()
    if not head or head[1]!=1: raise ValueError('unsealed snapshot')
    votes=[]
    rows=db.execute('''SELECT s.event,s.model,s.availability,s.submission,s.eligibility_id,a.role,a.result,u.revision,
        p.submission,p.decision,pu.revision
        FROM snapshot_slot s LEFT JOIN ai_review a ON a.submission=s.submission AND a.key=s.key
        LEFT JOIN submission u ON u.id=s.submission
        LEFT JOIN pending_trace p ON p.snapshot=s.snapshot AND p.event=s.event AND p.model=s.model
        LEFT JOIN submission pu ON pu.id=p.submission WHERE s.snapshot=? AND s.key=?''',(sid,key)).fetchall()
    for e,m,state,sub,dec,role,result,rev,ps,pd,pr in rows:
        if state=='ELIGIBLE':votes.append(Slot(m,state,role,result,f'fixture:{e}:{m}:{rev}:{sub}',f'fixture:decision:{dec}'))
        elif state in ('HOLD','INCOMPLETE'):votes.append(Slot(m,state,None,None,f'fixture:{e}:{m}:{pr}:{ps}',f'fixture:decision:{pd}' if pd is not None else None))
        else:votes.append(Slot(m,state))
    r=evaluate(key,votes)
    reason=json.dumps({'snapshot_fingerprint':head[0],'result':r},ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return r['status'],r['selected_count'],r['responded_count'],reason


def register(db):
    def ok(sid,key,rule,status,selected,responded,reason):
        try:return int(rule==RULE and expected(db,sid,key)==(status,selected,responded,reason))
        except (ValueError,TypeError,KeyError):return 0
    db.create_function('c09_consensus_ok',7,ok)


def install(db):
    if db.in_transaction or db.execute('PRAGMA recursive_triggers').fetchone()[0]!=1 or db.execute('PRAGMA foreign_keys').fetchone()[0]!=1:
        raise ValueError('guard installation requires idle guarded connection')
    if db.execute('SELECT count(*) FROM consensus').fetchone()[0] or db.execute('SELECT count(*) FROM expert_review').fetchone()[0]:
        raise ValueError('install on new result store only; no historical certification')
    register(db)
    db.executescript('''
    BEGIN;
    CREATE TRIGGER c09_consensus_insert BEFORE INSERT ON consensus
    WHEN c09_consensus_ok(NEW.snapshot,NEW.key,NEW.rule_version,NEW.status,NEW.selected_count,NEW.responded_count,NEW.reason)!=1
    BEGIN SELECT RAISE(ABORT,'invalid computed consensus'); END;
    CREATE TRIGGER c09_expert_insert BEFORE INSERT ON expert_review
    WHEN NOT EXISTS(SELECT 1 FROM consensus c WHERE c.snapshot=NEW.snapshot AND c.key=NEW.key AND c.rule_version='1.0'
        AND c.status IN ('INTERNAL_CONSENSUS_SELECTED','EXPERT_REVIEW_REQUIRED'))
      OR length(trim(NEW.rationale))=0 OR length(NEW.rationale)>4000 OR NEW.actor NOT LIKE 'fixture:%'
    BEGIN SELECT RAISE(ABORT,'expert draft requires complete consensus and fixture provenance'); END;
    COMMIT;
    ''')
