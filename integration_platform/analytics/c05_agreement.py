"""C05 synthetic agreement metrics. No real input or expert accuracy claims."""
from collections import Counter
from itertools import combinations
import unittest
from c04_consensus import MODELS, STATES, evaluate_grid, slot, CODES

THREE = ('선정','판단보류','미선정')
BINARY = ('선정','비선정 응답')


def ratio(n,d):
    return n/d if d else None


def classify(result, categories):
    return result if categories==THREE or result=='선정' else BINARY[1]


def pair_metrics(pairs, categories):
    n=len(pairs); matrix=[[0 for _ in categories] for _ in categories]
    for a,b in pairs: matrix[categories.index(a)][categories.index(b)]+=1
    observed=ratio(sum(matrix[i][i] for i in range(len(categories))),n)
    expected=ratio(sum(sum(matrix[i])*sum(row[i] for row in matrix) for i in range(len(categories))),n*n)
    kappa=None if expected is None or expected==1 else (observed-expected)/(1-expected)
    intersection=sum(a==b=='선정' for a,b in pairs)
    union=sum(a=='선정' or b=='선정' for a,b in pairs)
    return dict(n=n,confusion=matrix,agreement=observed,cohen_kappa=kappa,
                kappa_undefined_reason='NO_PAIRED_ELIGIBLE' if not n else 'EXPECTED_AGREEMENT_ONE' if expected==1 else None,
                selected_jaccard=ratio(intersection,union),jaccard_union=union)


def multi_metrics(rows,categories):
    n=len(rows);counts=Counter(x for r in rows for x in r)
    if not n:return dict(n=0,unanimous_agreement=None,mean_pair_agreement=None,fleiss_kappa=None,kappa_undefined_reason='NO_COMPLETE_CASES',category_counts={c:0 for c in categories})
    observed=sum(sum(v*(v-1) for v in Counter(r).values())/6 for r in rows)/n
    expected=sum((counts[c]/(3*n))**2 for c in categories)
    return dict(n=n,unanimous_agreement=sum(len(set(r))==1 for r in rows)/n,
                mean_pair_agreement=observed,fleiss_kappa=None if expected==1 else (observed-expected)/(1-expected),
                kappa_undefined_reason='EXPECTED_AGREEMENT_ONE' if expected==1 else None,
                category_counts={c:counts[c] for c in categories})


def summarize(events,ballots):
    rows=evaluate_grid(events,ballots)
    coverage={m:{s:0 for s in STATES} for m in MODELS};results={m:Counter() for m in MODELS}
    parsed=[]
    for row in rows:
        values={}
        for v in row['votes']:
            m=v['model'];coverage[m][v['availability']]+=1
            if v['availability']=='ELIGIBLE':values[m]=v['result'];results[m][v['result']]+=1
        parsed.append(values)
    n=len(rows);complete=sum(len(v)==3 for v in parsed)
    output={'keys':n,'slots':3*n,'complete_keys':complete,'pending_keys':n-complete,
            'availability':coverage,'eligible_outcomes':{m:{c:results[m][c] for c in THREE} for m in MODELS},
            'complete_coverage':ratio(complete,n),'metrics':{},'approved':False,'can_ship':False}
    for mode,categories in [('three_category',THREE),('binary_selected',BINARY)]:
        pairs={}
        for a,b in combinations(MODELS,2):
            paired=[(classify(v[a],categories),classify(v[b],categories)) for v in parsed if a in v and b in v]
            pairs[a+'__'+b]=dict(pair_metrics(paired,categories),excluded_keys=n-len(paired))
        full=[tuple(classify(v[m],categories) for m in MODELS) for v in parsed if len(v)==3]
        output['metrics'][mode]={'categories':categories,'pairs':pairs,'complete_case':dict(multi_metrics(full,categories),excluded_keys=n-len(full))}
    return output


class Tests(unittest.TestCase):
    def grid(self,roles=('D','D','N'),states=('ELIGIBLE',)*3):
        e='SYNTHETIC-001';return [e],{e+'-'+c:[slot(m,r,s) for m,r,s in zip(MODELS,roles,states)] for c in CODES}
    def test_perfect_balanced(self):
        p=pair_metrics([('선정','선정'),('미선정','미선정')],THREE);self.assertEqual(p['cohen_kappa'],1);self.assertEqual(p['selected_jaccard'],1)
        self.assertEqual(multi_metrics([('선정',)*3,('미선정',)*3],THREE)['fleiss_kappa'],1)
    def test_negative_kappa(self):
        self.assertEqual(pair_metrics([('선정','미선정'),('미선정','선정')],THREE)['cohen_kappa'],-1)
        self.assertAlmostEqual(multi_metrics([('선정','선정','미선정'),('미선정','미선정','선정')],THREE)['fleiss_kappa'],-1/3)
    def test_all_negative(self):
        p=pair_metrics([('미선정','미선정')],THREE);self.assertIsNone(p['cohen_kappa']);self.assertIsNone(p['selected_jaccard']);self.assertEqual(p['agreement'],1)
    def test_all_missing(self):
        r=summarize(*self.grid(states=('MISSING',)*3));self.assertEqual(r['complete_keys'],0);self.assertIsNone(r['metrics']['three_category']['complete_case']['fleiss_kappa']);self.assertEqual(r['availability']['CHATGPT']['MISSING'],40)
    def test_partial(self):
        r=summarize(*self.grid(states=('ELIGIBLE','ELIGIBLE','HOLD')));m=r['metrics']['three_category'];self.assertEqual(m['pairs']['CHATGPT__GEMINI']['n'],40);self.assertEqual(m['pairs']['CHATGPT__CLAUDE']['n'],0);self.assertEqual(m['complete_case']['n'],0)
    def test_deferred_separate(self):
        r=summarize(*self.grid(roles=('A','N','D')));a=r['metrics']['three_category']['pairs']['CHATGPT__GEMINI'];b=r['metrics']['binary_selected']['pairs']['CHATGPT__GEMINI'];self.assertEqual(a['agreement'],0);self.assertEqual(b['agreement'],1);self.assertEqual(r['eligible_outcomes']['CHATGPT']['판단보류'],40)
    def test_full_grid(self):
        es=[f'SYNTHETIC-{i:03}' for i in range(38)];b={e+'-'+c:[slot(m,'D' if j==0 else 'A', 'HOLD' if i%2 and j==2 else 'ELIGIBLE') for j,m in enumerate(MODELS)] for i,e in enumerate(es) for c in CODES};r=summarize(es,b);self.assertEqual(r['keys'],1520);self.assertEqual(r['complete_keys'],760);self.assertEqual(r['slots'],4560);self.assertEqual(r['metrics']['three_category']['pairs']['CHATGPT__GEMINI']['n'],1520)
    def test_real_key(self):self.assertRaises(ValueError,summarize,['ROOT-001'],{})
    def test_grid_missing(self):self.assertRaises(ValueError,summarize,['SYNTHETIC-001'],{})

if __name__=='__main__':unittest.main(verbosity=2)
