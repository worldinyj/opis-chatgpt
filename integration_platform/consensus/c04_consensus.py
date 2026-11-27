"""C04 rule 1.0, pure synthetic consensus. No DB, I/O or approval."""
from dataclasses import dataclass, asdict
from itertools import product
import hashlib
import json
import re
import unittest

MODELS = ('CHATGPT', 'GEMINI', 'CLAUDE')
ROLE = dict(D='선정', I='선정', A='판단보류', H='미선정', P='미선정', N='미선정')
STATES = ('ELIGIBLE', 'HOLD', 'MISSING', 'INCOMPLETE')
CODES = tuple(f'{p}{i}' for p,n in [('PA',3),('QA',4),('CO',4),('LA',8),('DM',3),('WE',4),('CL',4),('PI',4),('RC',2),('WP',4)] for i in range(1,n+1))
RULE = '1.0'


@dataclass(frozen=True)
class Slot:
    model: str
    availability: str
    role: str | None = None
    result: str | None = None
    submission_ref: str | None = None
    eligibility_ref: str | None = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evaluate(key, slots):
    """Only explicitly eligible, complete votes count. Missing never equals N."""
    require(isinstance(key, str) and re.fullmatch(r'SYNTHETIC-\d{3}-[A-Z]{2}[1-8]', key) and key.rsplit('-',1)[1] in CODES, 'synthetic key only')
    slots = tuple(slots)
    require(len(slots)==3 and all(type(s) is Slot for s in slots), 'exactly three explicit slots')
    require({s.model for s in slots}==set(MODELS), 'model coverage or duplicate')
    ordered = sorted(slots, key=lambda s: MODELS.index(s.model))
    valid = []
    pending = []
    for s in ordered:
        require(s.availability in STATES, 'unknown availability')
        for ref in (s.submission_ref,s.eligibility_ref):
            require(ref is None or (type(ref) is str and ref.startswith('fixture:') and len(ref)>8), 'synthetic references only')
        if s.availability=='ELIGIBLE':
            require(s.role in ROLE and ROLE[s.role]==s.result, 'eligible vote inconsistent')
            require(bool(s.submission_ref) and bool(s.eligibility_ref), 'eligible provenance required')
            valid.append(s)
        else:
            require(s.role is None and s.result is None, 'noneligible ballot forbidden')
            if s.availability=='MISSING':
                require(s.submission_ref is None and s.eligibility_ref is None, 'missing has provenance')
            elif s.availability=='HOLD':
                require(bool(s.submission_ref) and bool(s.eligibility_ref), 'HOLD provenance required')
            else:
                require(bool(s.submission_ref) and s.eligibility_ref is None, 'incomplete provenance')
            pending.append({'model':s.model,'availability':s.availability})
    responded = len(valid)
    if pending:
        status, count = 'PENDING_INPUT', None
        reason = 'NOT_ALL_THREE_ELIGIBLE'
    else:
        count = sum(s.result=='선정' for s in valid)
        status = 'INTERNAL_CONSENSUS_SELECTED' if count==3 else 'EXPERT_REVIEW_REQUIRED'
        reason = 'ALL_THREE_SELECTED' if count==3 else 'ZERO_TO_TWO_SELECTED'
    payload = {'key':key,'rule_version':RULE,'status':status,'selected_count':count,
               'responded_count':responded,'deferred_count':sum(s.role=='A' for s in valid),
               'pending':pending,'reason':reason,'votes':[asdict(s) for s in ordered],
               'approved':False,'can_ship':False,'expert_decision':None}
    payload['result_sha256'] = hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return payload


def evaluate_grid(events, ballots):
    """Reject missing/extra keys; callers represent missing models as explicit slots."""
    events = tuple(events)
    require(len(events)==len(set(events)) and bool(events) and all(re.fullmatch(r'SYNTHETIC-\d{3}',e) for e in events), 'synthetic event set')
    keys = {e+'-'+c for e in events for c in CODES}
    require(set(ballots)==keys, 'incomplete or extra grid keys')
    return [evaluate(k,ballots[k]) for k in sorted(keys)]


def slot(model, role='D', state='ELIGIBLE'):
    sub='fixture:'+model+':revision1'
    dec='fixture:'+model+':decision1'
    if state=='ELIGIBLE': return Slot(model,state,role,ROLE[role],sub,dec)
    if state=='HOLD': return Slot(model,state,None,None,sub,dec)
    if state=='INCOMPLETE': return Slot(model,state,None,None,sub,None)
    return Slot(model,state)


class Tests(unittest.TestCase):
    key='SYNTHETIC-001-PA1'
    def votes(self, roles='DDD', states=('ELIGIBLE',)*3):
        return [slot(m,r,s) for m,r,s in zip(MODELS,roles,states)]
    def test_all_216_role_combinations(self):
        for roles in product(ROLE,repeat=3):
            r=evaluate(self.key,self.votes(roles))
            n=sum(x in ('D','I') for x in roles)
            self.assertEqual(r['selected_count'],n)
            self.assertEqual(r['responded_count'],3)
            self.assertEqual(r['deferred_count'],roles.count('A'))
            self.assertEqual(r['status'],'INTERNAL_CONSENSUS_SELECTED' if n==3 else 'EXPERT_REVIEW_REQUIRED')
            self.assertFalse(r['approved']);self.assertFalse(r['can_ship'])
    def test_all_64_availability_combinations(self):
        for states in product(STATES,repeat=3):
            r=evaluate(self.key,self.votes('DDA',states))
            n=states.count('ELIGIBLE')
            self.assertEqual(r['responded_count'],n)
            self.assertEqual(r['selected_count'],2 if n==3 else None)
            self.assertEqual(r['status'],'EXPERT_REVIEW_REQUIRED' if n==3 else 'PENDING_INPUT')
    def test_zero_not_auto_reject(self):
        self.assertEqual(evaluate(self.key,self.votes('NNN'))['status'],'EXPERT_REVIEW_REQUIRED')
    def test_all_missing(self):
        r=evaluate(self.key,self.votes(states=('MISSING',)*3));self.assertIsNone(r['selected_count']);self.assertEqual(r['responded_count'],0)
    def test_duplicate_model(self):
        v=self.votes();v[2]=v[0];self.assertRaises(ValueError,evaluate,self.key,v)
    def test_absent_slot(self): self.assertRaises(ValueError,evaluate,self.key,self.votes()[:2])
    def test_bad_role(self):
        v=self.votes();v[0]=Slot('CHATGPT','ELIGIBLE','D','미선정','fixture:s','fixture:e');self.assertRaises(ValueError,evaluate,self.key,v)
    def test_held_vote(self):
        v=self.votes();v[0]=Slot('CHATGPT','HOLD','D','선정','fixture:s','fixture:e');self.assertRaises(ValueError,evaluate,self.key,v)
    def test_provenance(self):
        v=self.votes();v[0]=Slot('CHATGPT','ELIGIBLE','D','선정');self.assertRaises(ValueError,evaluate,self.key,v)
    def test_nonfixture(self): self.assertRaises(ValueError,evaluate,'ROOT-001-PA1',self.votes())
    def test_bad_state(self):
        v=self.votes();v[0]=Slot('CHATGPT','STORED');self.assertRaises(ValueError,evaluate,self.key,v)
    def test_order_and_digest(self):
        v=self.votes();self.assertEqual(evaluate(self.key,v),evaluate(self.key,list(reversed(v))))
        self.assertNotEqual(evaluate(self.key,v)['result_sha256'],evaluate(self.key,self.votes('DID'))['result_sha256'])
    def test_full_grid(self):
        events=[f'SYNTHETIC-{i:03}' for i in range(38)]
        ballots={e+'-'+c:self.votes('DDD' if i%3==0 else 'DNA',('ELIGIBLE','ELIGIBLE','HOLD') if i%3==2 else ('ELIGIBLE',)*3) for i,e in enumerate(events) for c in CODES}
        rows=evaluate_grid(events,ballots);self.assertEqual(len(rows),1520)
        self.assertEqual(sum(r['status']=='INTERNAL_CONSENSUS_SELECTED' for r in rows),520)
        self.assertEqual(sum(r['status']=='EXPERT_REVIEW_REQUIRED' for r in rows),520)
        self.assertEqual(sum(r['status']=='PENDING_INPUT' for r in rows),480)
        self.assertEqual(sum(len(r['votes']) for r in rows),4560)
    def test_incomplete_grid(self): self.assertRaises(ValueError,evaluate_grid,['SYNTHETIC-001'],{self.key:self.votes()})


if __name__=='__main__': unittest.main(verbosity=2)
