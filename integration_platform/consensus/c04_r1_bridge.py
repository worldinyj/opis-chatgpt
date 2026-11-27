"""C04-R1: sealed synthetic snapshot to atomic consensus records."""
import json
import re
from c04_consensus import Slot, evaluate_grid, RULE, MODELS, CODES, require


def calculate(db, snapshot):
    require(type(snapshot) is int and snapshot > 0 and not db.in_transaction, 'snapshot/transaction')
    require(db.execute('PRAGMA foreign_keys').fetchone()[0] == 1, 'foreign keys disabled')
    with db:
        db.execute('BEGIN IMMEDIATE')
        head = db.execute('SELECT version,fingerprint,sealed FROM snapshot WHERE id=?',(snapshot,)).fetchone()
        require(head is not None and head[2] == 1 and head[0] == 'SYNTHETIC-V1', 'sealed synthetic snapshot required')
        version, fingerprint, _ = head
        require(re.fullmatch(r'[a-f0-9]{64}', fingerprint) and db.execute('SELECT snapshot_digest(?)',(snapshot,)).fetchone()[0] == fingerprint, 'snapshot digest mismatch')
        events = [r[0] for r in db.execute('SELECT queue_id FROM event ORDER BY queue_id')]
        expected = {(e+'-'+c,e,c) for e in events for c in CODES}
        actual = set(db.execute('SELECT id,event,code FROM review_key WHERE version=?',(version,)))
        require(actual == expected, 'master key mismatch')
        slots = db.execute('''SELECT s.key,s.event,s.version,s.model,s.availability,s.submission,s.eligibility_id,s.eligible_status,
            a.role,a.result,u.revision,u.event,u.model,u.version,d.submission,d.status,
            p.availability,p.submission,p.decision,p.decision_status,pu.revision,pu.event,pu.model,pu.version,pd.submission,pd.status,p.version
            FROM snapshot_slot s LEFT JOIN ai_review a ON a.submission=s.submission AND a.key=s.key AND a.event=s.event AND a.version=s.version
            LEFT JOIN submission u ON u.id=s.submission LEFT JOIN eligibility d ON d.id=s.eligibility_id
            LEFT JOIN pending_trace p ON p.snapshot=s.snapshot AND p.event=s.event AND p.model=s.model
            LEFT JOIN submission pu ON pu.id=p.submission LEFT JOIN eligibility pd ON pd.id=p.decision WHERE s.snapshot=?''',(snapshot,)).fetchall()
        require(len(slots)==len(expected)*3, 'slot count')
        ballots={}; seen=set(); traces=set(); groups={}
        for k,e,v,m,state,sub,dec,es,role,result,rev,ue,um,uv,ds,ds_status,ps,p_sub,p_dec,p_status,p_rev,pe,pm,pv,pds,pds_status,trace_version in slots:
            require(v==version and (k,e,k.rsplit('-',1)[1]) in expected and m in MODELS and (k,m) not in seen, 'slot key/model')
            seen.add((k,m))
            if state=='ELIGIBLE':
                require(sub is not None and dec is not None and es=='ELIGIBLE' and (ue,um,uv)==(e,m,v) and (ds,ds_status)==(sub,'ELIGIBLE') and ps is None, 'eligible linkage')
                s=Slot(m,state,role,result,f'fixture:{e}:{m}:{rev}:{sub}',f'fixture:decision:{dec}')
            elif state in ('HOLD','INCOMPLETE'):
                require(sub is None and dec is None and es is None and role is None and result is None and ps==state and trace_version==v and (pe,pm,pv)==(e,m,v), 'pending linkage')
                if state=='HOLD': require(p_dec is not None and p_status in ('HOLD','REJECTED') and (pds,pds_status)==(p_sub,p_status), 'hold decision linkage')
                else: require(p_dec is None and p_status is None, 'incomplete has decision')
                traces.add((e,m));s=Slot(m,state,None,None,f'fixture:{e}:{m}:{p_rev}:{p_sub}',f'fixture:decision:{p_dec}' if p_dec is not None else None)
            else:
                require(state=='MISSING' and all(x is None for x in (sub,dec,es,role,result,ps)), 'missing linkage')
                s=Slot(m,state)
            group=(e,m);identity=(state,s.submission_ref,s.eligibility_ref)
            require(group not in groups or groups[group]==identity,'mixed revision or availability')
            groups[group]=identity
            ballots.setdefault(k,[]).append(s)
        require(traces==set(db.execute('SELECT event,model FROM pending_trace WHERE snapshot=?',(snapshot,))), 'orphan pending trace')
        results=evaluate_grid(events,ballots)
        records=[]
        for r in results:
            reason=json.dumps({'snapshot_fingerprint':fingerprint,'result':r},ensure_ascii=False,sort_keys=True,separators=(',',':'))
            records.append((snapshot,r['key'],RULE,r['status'],r['selected_count'],r['responded_count'],reason))
        old=db.execute('SELECT snapshot,key,rule_version,status,selected_count,responded_count,reason FROM consensus WHERE snapshot=? AND rule_version=? ORDER BY key',(snapshot,RULE)).fetchall()
        if old:
            require(old==records,'existing consensus conflict or partial results')
            return 'NOOP',len(records)
        db.executemany('INSERT INTO consensus VALUES(?,?,?,?,?,?,?)',records)
        db.execute('INSERT INTO audit_event(actor,action,target,at,reason) VALUES(?,?,?,?,?)',('fixture','C04_CALCULATED',str(snapshot),'2000-01-01',fingerprint))
    return 'STORED_SYNTHETIC',len(records)
