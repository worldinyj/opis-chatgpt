"""C05-R1 synthetic grouped metrics and common-case denominators."""
from collections import defaultdict, Counter
from itertools import combinations
import unittest
from c04_consensus import MODELS, STATES, CODES, evaluate_grid, slot, require
from c05_agreement import THREE, BINARY, classify, pair_metrics, multi_metrics


def group_metrics(rows):
    parsed=[]
    coverage={m:Counter() for m in MODELS}
    outcomes={m:Counter() for m in MODELS}
    for row in rows:
        valid={}
        for v in row['votes']:
            m=v['model'];coverage[m][v['availability']]+=1
            if v['availability']=='ELIGIBLE':
                valid[m]=v['result'];outcomes[m][v['result']]+=1
        parsed.append(valid)
    full=[r for r in parsed if len(r)==3]
    out=dict(keys=len(rows),complete_keys=len(full),pending_keys=len(rows)-len(full),
             coverage={m:{s:coverage[m][s] for s in STATES} for m in MODELS},
             outcomes={m:{c:outcomes[m][c] for c in THREE} for m in MODELS},metrics={})
    for mode,cats in [('three_category',THREE),('binary_selected',BINARY)]:
        pairs={}
        for a,b in combinations(MODELS,2):
            eligible=[(classify(r[a],cats),classify(r[b],cats)) for r in parsed if a in r and b in r]
            common=[(classify(r[a],cats),classify(r[b],cats)) for r in full]
            pairs[a+'__'+b]={'pairwise':pair_metrics(eligible,cats),'common':pair_metrics(common,cats)}
        out['metrics'][mode]={'pairs':pairs,'complete_case':multi_metrics([tuple(classify(r[m],cats) for m in MODELS) for r in full],cats)}
    return out


def summarize_groups(events,ballots,metadata):
    events=tuple(events);require(set(metadata)==set(events),'metadata coverage')
    for e in events:
        m=metadata[e]
        require(set(m)=={'plant','year'} and type(m['plant']) is str and m['plant'].startswith('FIXTURE-') and type(m['year']) is int and 1900<=m['year']<=2100,'synthetic metadata')
    rows=evaluate_grid(events,ballots)
    buckets={dim:defaultdict(list) for dim in ('principle','attribute','plant','year','event')}
    for row in rows:
        e,code=row['key'].rsplit('-',1);m=metadata[e]
        for dim,value in [('principle',code[:2]),('attribute',code),('plant',m['plant']),('year',str(m['year'])),('event',e)]:
            buckets[dim][value].append(row)
    return {'overall':group_metrics(rows),'groups':{dim:{k:group_metrics(v) for k,v in sorted(groups.items())} for dim,groups in buckets.items()},'approved':False,'can_ship':False}


class Tests(unittest.TestCase):
    def fixture(self,n=2):
        es=[f'SYNTHETIC-{i:03}' for i in range(n)]
        b={e+'-'+c:[slot(m,'D' if j==0 else ('A' if i%2 else 'N'),'HOLD' if i%2 and j==2 else 'ELIGIBLE') for j,m in enumerate(MODELS)] for i,e in enumerate(es) for c in CODES}
        return es,b,{e:{'plant':f'FIXTURE-{i%3}','year':2000+i%2} for i,e in enumerate(es)}
    def test_partitions(self):
        r=summarize_groups(*self.fixture(38));self.assertEqual(r['overall']['keys'],1520)
        for groups in r['groups'].values():
            self.assertEqual(sum(x['keys'] for x in groups.values()),1520);self.assertEqual(sum(x['complete_keys'] for x in groups.values()),760)
        self.assertEqual(len(r['groups']['principle']),10);self.assertEqual(len(r['groups']['attribute']),40)
    def test_common_denominator(self):
        r=summarize_groups(*self.fixture())['overall']['metrics']['three_category']['pairs']
        self.assertEqual(r['CHATGPT__GEMINI']['pairwise']['n'],80);self.assertTrue(all(x['common']['n']==40 for x in r.values()))
    def test_metadata(self):
        e,b,m=self.fixture();m.pop(e[0]);self.assertRaises(ValueError,summarize_groups,e,b,m)
    def test_real_plant(self):
        e,b,m=self.fixture();m[e[0]]['plant']='REAL';self.assertRaises(ValueError,summarize_groups,e,b,m)
    def test_reference_cohen(self):
        from sklearn.metrics import cohen_kappa_score, jaccard_score
        a=['선정','미선정','판단보류','선정','선정'];b=['선정','선정','판단보류','미선정','선정']
        r=pair_metrics(list(zip(a,b)),THREE);self.assertAlmostEqual(r['cohen_kappa'],cohen_kappa_score(a,b,labels=list(THREE)));self.assertAlmostEqual(r['selected_jaccard'],jaccard_score([x=='선정' for x in a],[x=='선정' for x in b]))
    def test_reference_fleiss(self):
        from statsmodels.stats.inter_rater import fleiss_kappa
        rows=[('선정','미선정','판단보류'),('선정','선정','미선정'),('미선정',)*3]
        counts=[[r.count(c) for c in THREE] for r in rows];self.assertAlmostEqual(multi_metrics(rows,THREE)['fleiss_kappa'],fleiss_kappa(counts))

if __name__=='__main__': unittest.main(verbosity=2)
