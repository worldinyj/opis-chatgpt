"""Run pinned, synthetic-only OPIS tests in isolated subprocesses (Python 3.12+)."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

BASE = '6aecf146a077774290e05d07b2a69155bc651dc7'
DIRS = ('db','consensus','analytics','importer','expert_review','excel','dashboard','tests','local')
# C02-R2 main runs all three database selftests; do not count base/R1 twice.
SUITES = (
    ('C02','db/c02_r2.py',(),(),61),
    ('C03','importer/c03_staging.py',(),(),18),
    ('C03-R1','importer/test_c03_r1_adapter.py',('--repo','{repo}'),('jsonschema',),16),
    ('C04','consensus/c04_consensus.py',(),(),14),
    ('C04-R1','consensus/test_c04_r1_bridge.py',(),(),9),
    ('C05','analytics/c05_agreement.py',(),(),9),
    ('C05-R1','analytics/c05_r1_groups.py',(),('sklearn','statsmodels'),6),
    ('C06','expert_review/c06_review.py',(),(),10),
    ('C07','excel/test_c07.py',(),('artifact_tool',),7),
    ('C07-PORTABLE','excel/test_c07_portable.py',(),(),17),
    ('C07-ROUNDTRIP','excel/test_c07_portable_roundtrip.py',(),('artifact_tool',),2),
    ('C08','dashboard/test_c08.py',(),(),7),
    ('C09-AB','tests/c09_core_e2e.py',(),(),9),
    ('C09-R1','tests/test_c09_guard.py',(),(),7),
    ('C09-C','tests/test_c09_import.py',('--repo','{repo}'),('jsonschema',),7),
    ('C09-R2','tests/test_c09_connection.py',(),(),8),
    ('C09-FINAL','tests/c09_acceptance.py',(),(),2),
    ('C09-F1F2','tests/test_f1f2.py',(),('jsonschema',),10),
    ('C09-F3','tests/test_archive_audit.py',(),(),9),
    ('C06-R1','tests/test_core_review.py',(),(),5),
    ('C09-F4','local/test_full_restore.py',(),('jsonschema',),1),
    ('C06-WEB','local/test_django_core.py',(),('django',),6),
)


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.STDOUT)


def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def preflight(repo):
    root=repo/'integration_platform'
    git(repo,'merge-base','--is-ancestor',BASE,'HEAD')
    raw=git(repo,'ls-tree','-rz',BASE,'--','integration_platform')
    checked=0
    for item in raw.split(b'\0'):
        if not item:continue
        meta,name=item.split(b'\t',1);mode,kind,sha=meta.decode().split();name=name.decode()
        # Pin every pre-existing Python and template file, plus the C01 contract.
        if not (name.endswith(('.py','.html')) or name.endswith('/INTEGRATION_CONTRACT_V1.json')):continue
        path=repo/name
        if mode!='100644' or kind!='blob' or path.is_symlink() or not path.is_file() or blob(path.read_bytes())!=sha:
            raise ValueError('source pin mismatch: '+name)
        checked+=1
    if checked<20:raise ValueError('incomplete source tree')
    for rel in [row[1] for row in SUITES]+['excel/c07_portable.py']:
        path=root/rel
        if path.is_symlink() or not path.is_file() or blob(path.read_bytes())!=git(repo,'rev-parse','HEAD:integration_platform/'+rel).decode().strip():
            raise ValueError('suite file not committed or modified: '+rel)
    contract=json.loads((root/'contracts/INTEGRATION_CONTRACT_V1.json').read_text(encoding='utf-8'))
    for name,sha in contract['reference_blobs'].items():
        if git(repo,'rev-parse',contract['base_ref']+':'+name).decode().strip()!=sha or blob(git(repo,'cat-file','blob',sha))!=sha:
            raise ValueError('contract pin mismatch: '+name)
    return {'source_files':checked,'contract_blobs':len(contract['reference_blobs']),'head':git(repo,'rev-parse','HEAD').decode().strip()}


def environment(repo):
    root=repo/'integration_platform';env=os.environ.copy()
    for k in ('OPIS_CONTRACT_FIXTURE','OPIS_LOCAL_WORKSPACE','DJANGO_SETTINGS_MODULE','OPIS_SYNTHETIC_CORE_REVIEW_ENABLED'):
        env.pop(k,None)
    env['OPIS_REPO']=str(repo)
    env['PYTHONPATH']=os.pathsep.join([str(root), *(str(root/d) for d in DIRS)])
    env['PYTHONUTF8']='1';env['PYTHONDONTWRITEBYTECODE']='1'
    return env


def run_suite(repo,out,suite,env):
    name,rel,args,deps,expected=suite
    missing=[d for d in deps if importlib.util.find_spec(d) is None]
    if missing:return dict(id=name,status='BLOCKED_DEPENDENCY',missing=missing,expected_tests=expected)
    path=repo/'integration_platform'/rel
    if not path.is_file():return dict(id=name,status='BLOCKED_FILE',path=rel,expected_tests=expected)
    cmd=[sys.executable,str(path),*[a.format(repo=repo) for a in args]]
    start=time.monotonic()
    try:
        p=subprocess.run(cmd,cwd=repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        (out/(name+'.log')).write_bytes(p.stdout)
        log=p.stdout.decode('utf-8',errors='replace')
        counts=re.findall(r'^Ran (\d+) tests? in ',log,re.M)
        if name=='C02':counts=re.findall(r'^PASS (\d+) ',log,re.M)
        observed=sum(map(int,counts)) if counts else None
        clean=p.returncode==0 and observed==expected and not re.search(r'skipped=|expected failures=|unexpected successes=',log)
        return dict(id=name,status='PASS' if clean else 'FAIL',returncode=p.returncode,seconds=round(time.monotonic()-start,3),expected_tests=expected,observed_tests=observed)
    except subprocess.TimeoutExpired as e:
        (out/(name+'.log')).write_bytes(e.stdout or b'')
        return dict(id=name,status='TIMEOUT',expected_tests=expected)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--report-dir',required=True,type=Path);args=p.parse_args()
    repo=args.repo.resolve();out=args.report_dir.resolve()
    if out==repo or repo in out.parents: p.error('report directory must be outside repository')
    out.mkdir(parents=True,exist_ok=False)
    report=dict(synthetic_only=True,approved=False,can_ship=False,actual_data_import=False,acceptance_go=False,base=BASE,python=sys.version,results=[])
    try:report['preflight']=preflight(repo)
    except (OSError,ValueError,subprocess.CalledProcessError) as e:
        report['preflight_error']=str(e);report['status']='BLOCKED_PREFLIGHT'
    else:
        env=environment(repo)
        for suite in SUITES:
            row=run_suite(repo,out,suite,env);report['results'].append(row);print(row['id'],row['status'],flush=True)
        report['status']='SYNTHETIC_SUITES_PASS' if all(r['status']=='PASS' for r in report['results']) else 'INCOMPLETE_OR_FAILED'
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(report['status'],out/'report.json')
    return 0 if report['status']=='SYNTHETIC_SUITES_PASS' else 1

if __name__=='__main__':raise SystemExit(main())
