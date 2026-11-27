"""C08 standalone HTML dashboard, synthetic data only, no DB or approval."""
from collections import Counter
from html import escape
from pathlib import Path
from c04_consensus import MODELS, CODES, STATES, evaluate_grid, slot
from c05_r1_groups import summarize_groups


def fmt(v): return '미정의' if v is None else f'{v:.3f}'


def table(headers,rows):
    def cell(v): return escape(str(v))
    return '<div class="scroll"><table><thead><tr>'+''.join(f'<th scope="col">{cell(h)}</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{cell(v)}</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'


def render(events,ballots,metadata):
    events=tuple(events);stats=summarize_groups(events,ballots,metadata)
    records=evaluate_grid(events,ballots);overall=stats['overall'];n=overall['keys']
    counts=Counter(r['status'] for r in records)
    order=[('INTERNAL_CONSENSUS_SELECTED','내부 합의 후보'),('EXPERT_REVIEW_REQUIRED','전문가 검토 필요'),('PENDING_INPUT','입력 대기')]
    cards=''.join(f'<article><small>{label}</small><strong>{counts[k]:,}</strong><progress value="{counts[k]}" max="{n}"></progress></article>' for k,label in order)
    coverage=table(['모델','적격','HOLD','미확보','불완전','선정','판단보류','미선정'],[[m]+[overall['coverage'][m][s] for s in STATES]+[overall['outcomes'][m][c] for c in ('선정','판단보류','미선정')] for m in MODELS])
    comparisons=[]
    for mode,label in [('three_category','3범주'),('binary_selected','2범주')]:
        for pair,values in overall['metrics'][mode]['pairs'].items():
            for basis,basis_label in [('pairwise','쌍별 적격'),('common','공통 완전사례')]:
                v=values[basis];comparisons.append([label,pair.replace('__',' / '),basis_label,v['n'],fmt(v['agreement']),fmt(v['cohen_kappa']),fmt(v['selected_jaccard'])])
    agreement=table(['범주','모델 조합','분모 기준','N','일치율','Cohen κ','Jaccard'],comparisons)
    multi=table(['범주','완전사례 N','만장일치율','Fleiss κ'],[[label,overall['metrics'][mode]['complete_case']['n'],fmt(overall['metrics'][mode]['complete_case']['unanimous_agreement']),fmt(overall['metrics'][mode]['complete_case']['fleiss_kappa'])] for mode,label in [('three_category','3범주'),('binary_selected','2범주')]])
    sections=[];nav=[]
    for dim,label in [('principle','원칙별'),('attribute','속성별'),('plant','발전소별'),('year','연도별'),('event','사건별')]:
        nav.append(f'<a href="#{dim}">{label}</a>')
        rows=[]
        for k,g in stats['groups'][dim].items():
            m=g['metrics']['three_category']['complete_case'];rows.append([k,g['keys'],g['complete_keys'],g['pending_keys'],*[g['outcomes'][model]['선정'] for model in MODELS],fmt(m['fleiss_kappa'])])
        sections.append(f'<section id="{dim}"><h2>{label}</h2>'+table(['구분','키','완전','입력 대기','ChatGPT 선정','Gemini 선정','Claude 선정','Fleiss κ'],rows)+'</section>')
    return '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>OPIS 합성 분석 대시보드</title><style>
:root{color-scheme:light;font-family:system-ui,sans-serif;color:#17283d;background:#f2f5f8}body{max-width:1120px;margin:0 auto;padding:24px}header{border-bottom:3px solid #315a74;padding:12px 0}h1{margin:0;font-size:28px}h2{font-size:20px;margin:0 0 14px}p{line-height:1.6}small{color:#41576a}strong{display:block;font-size:30px;margin:8px 0}nav{display:flex;flex-wrap:wrap;gap:16px;margin:20px 0}a{color:#225678}section{background:white;border:1px solid #dce3ea;border-radius:10px;margin:18px 0;padding:20px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}article{border:1px solid #dce3ea;border-radius:8px;padding:16px}progress{width:100%;accent-color:#397e89}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:9px 12px;text-align:left;border-bottom:1px solid #e5eaf0;white-space:nowrap}th{background:#eaf0f4}footer{font-size:13px;color:#41576a;padding:12px 0}</style></head><body><header><small>OPIS / C08 · SYNTHETIC ONLY</small><h1>안전문화 교차판정 대시보드</h1><p>합성 데이터 시범 화면 — 실제 사건 판정 및 전문가 승인 아님</p></header>'''+f'<nav>{"".join(nav)}</nav><section><h2>교차판정 현황</h2><p>{n:,}개 검토키 · {3*n:,}개 슬롯 · 완전사례 {overall["complete_keys"]:,}개</p><div class="cards">{cards}</div></section><section><h2>모델별 데이터 충족률 및 응답</h2>{coverage}</section><section><h2>모델 간 일치도</h2><p>쌍별 적격과 공통 완전사례의 분모를 구분. HOLD·미확보·불완전은 미선정이 아님.</p>{agreement}{multi}</section>'+''.join(sections)+'<section><h2>전문가 검토 진행</h2><p>연결되지 않음 — 실제 검토 건수 및 승인 현황 미산정.</p></section><footer>합성 시험 전용 · approved=false · can_ship=false · 실제 DB 연동 및 배포 금지</footer></body></html>'


def fixture():
    es=[f'SYNTHETIC-{i:03}' for i in range(38)]
    b={e+'-'+c:[slot(m,'D' if i%3==0 else 'A' if j==1 else 'N','HOLD' if i%3==2 and j==2 else 'ELIGIBLE') for j,m in enumerate(MODELS)] for i,e in enumerate(es) for c in CODES}
    return es,b,{e:{'plant':f'FIXTURE-{i%3}','year':2000+i%4} for i,e in enumerate(es)}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args()
    with Path(a.output).open('x',encoding='utf-8') as f: f.write(render(*fixture()))
