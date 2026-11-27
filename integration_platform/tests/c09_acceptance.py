"""C09-FINAL: synthetic acceptance tests against C01 rule 1.0.
No actual eligibility, expert approval or release authorization.
"""
import itertools
import unittest
from c04_consensus import MODELS, ROLE, STATES, evaluate, slot

KEY = 'SYNTHETIC-001-PA1'
# Exact semantic cases from INTEGRATION_CONTRACT_V1.json acceptance_cases.
CASES = (
    ('C01-AC01', ('선정','선정','선정'), (True,True,True), 'INTERNAL_CONSENSUS_SELECTED'),
    ('C01-AC02', ('선정','선정','미선정'), (True,True,True), 'EXPERT_REVIEW_REQUIRED'),
    ('C01-AC03', ('선정','미선정','판단보류'), (True,True,True), 'EXPERT_REVIEW_REQUIRED'),
    ('C01-AC04', ('미선정','미선정','미선정'), (True,True,True), 'EXPERT_REVIEW_REQUIRED'),
    ('C01-AC05', ('판단보류','미선정','미선정'), (True,True,True), 'EXPERT_REVIEW_REQUIRED'),
    ('C01-AC06', ('선정','선정',None), (True,True,False), 'PENDING_INPUT'),
    ('C01-AC07', ('선정','선정','선정'), (True,True,False), 'PENDING_INPUT'),
)


class Acceptance(unittest.TestCase):
    def test_c01_specification(self):
        roles = {'선정':'D','미선정':'N','판단보류':'A'}
        for ident, votes, eligible, expected in CASES:
            with self.subTest(ident=ident):
                ballot = [slot(m, roles[v]) if e else slot(m, state='MISSING' if v is None else 'HOLD')
                          for m,v,e in zip(MODELS,votes,eligible)]
                r = evaluate(KEY,ballot)
                self.assertEqual(r['status'],expected)
                self.assertEqual(r['responded_count'],sum(eligible))
                self.assertEqual(r['selected_count'],sum(v=='선정' for v in votes) if all(eligible) else None)
                self.assertFalse(r['approved']); self.assertFalse(r['can_ship'])
                self.assertIsNone(r['expert_decision'])

    def test_exhaustive_valid_ballots(self):
        options = [(r,'ELIGIBLE') for r in ROLE] + [(None,s) for s in STATES if s!='ELIGIBLE']
        total=complete=pending=selected=expert=0
        for combo in itertools.product(options,repeat=3):
            ballot=[slot(m,r,state) for m,(r,state) in zip(MODELS,combo)]
            result=evaluate(KEY,ballot)
            n=sum(state=='ELIGIBLE' for _,state in combo)
            self.assertEqual(result['responded_count'],n)
            self.assertEqual(result['deferred_count'],sum(r=='A' and state=='ELIGIBLE' for r,state in combo))
            self.assertFalse(result['approved']); self.assertFalse(result['can_ship'])
            self.assertIsNone(result['expert_decision'])
            total+=1
            if n==3:
                complete+=1
                count=sum(r in ('D','I') for r,_ in combo)
                self.assertEqual(result['selected_count'],count)
                status='INTERNAL_CONSENSUS_SELECTED' if count==3 else 'EXPERT_REVIEW_REQUIRED'
                self.assertEqual(result['status'],status)
                selected+=count==3; expert+=count!=3
            else:
                pending+=1
                self.assertIsNone(result['selected_count'])
                self.assertEqual(result['status'],'PENDING_INPUT')
        self.assertEqual((total,complete,pending,selected,expert),(729,216,513,8,208))


if __name__=='__main__': unittest.main(verbosity=2)
