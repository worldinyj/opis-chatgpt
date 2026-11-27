"""Read-only synthetic core projection for the future Django expert screen."""
import json, re

MODELS=('CHATGPT','GEMINI','CLAUDE')
RULE='1.0'


def detail(db,role,key):
    if role not in ('EXPERT','QA','READER'):raise PermissionError('review access denied')
    if not re.fullmatch(r'SYNTHETIC-\d{3}-[A-Z]{2}[1-8]',key):raise ValueError('synthetic key only')
    if db.in_transaction:raise ValueError('caller transaction')
    with db:
        db.execute('BEGIN')
        head=db.execute('SELECT id,fingerprint FROM snapshot WHERE sealed=1 ORDER BY id DESC LIMIT 1').fetchone()
        if not head:raise ValueError('no sealed snapshot')
        sid,fp=head
        if not re.fullmatch(r'[a-f0-9]{64}',fp) or db.execute('SELECT snapshot_digest(?)',(sid,)).fetchone()!=(fp,):raise ValueError('snapshot digest')
        row=db.execute('SELECT status,reason FROM consensus WHERE snapshot=? AND key=? AND rule_version=?',(sid,key,RULE)).fetchone()
        if not row:raise ValueError('consensus missing')
        status,reason=row;record=json.loads(reason);result=record['result']
        if record['snapshot_fingerprint']!=fp or result['key']!=key or result['status']!=status:raise ValueError('consensus identity')
        votes={v['model']:v for v in result['votes']}
        if len(result['votes'])!=3 or set(votes)!=set(MODELS):raise ValueError('model grid')
        latest=db.execute('SELECT revision,decision,rationale,actor,at FROM expert_review WHERE snapshot=? AND key=? ORDER BY revision DESC LIMIT 1',(sid,key)).fetchone()
        prior=db.execute('SELECT count(*) FROM expert_review WHERE snapshot<>? AND key=?',(sid,key)).fetchone()[0]
        return dict(key=key,snapshot=sid,fingerprint=fp,status=status,votes=[votes[m] for m in MODELS],revision=latest[0] if latest else 0,latest=latest,stale_review_required=bool(prior and latest is None),can_edit=role=='EXPERT' and status in ('INTERNAL_CONSENSUS_SELECTED','EXPERT_REVIEW_REQUIRED'),approved=False,can_ship=False)
