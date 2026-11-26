#!/usr/bin/env python3
"""Run existing case QC across the registered root corpus; never promote approvals."""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "video/scripts/final_case_qc.py"

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))

def scope(root):
    queue = read(root / "index/intake_queue.json")
    events = read(root / "index/events.json")
    items = queue["items"]
    ids = [i["event_id"] for i in items]
    if any(not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Unregistered or duplicate intake event ID")
    by_id = {}
    for event in events:
        if event["event_id"] in by_id:
            raise ValueError("Duplicate event index ID")
        by_id[event["event_id"]] = event
    rows = []
    seen = set()
    for item in items:
        eid = item["event_id"]
        rel = Path(by_id[eid]["path"])
        case = (root / rel.parent).resolve()
        if rel.name != "report.md" or not case.is_relative_to(root / "cases") or not (case / "report.md").is_file():
            raise ValueError("Invalid case path: " + str(rel))
        if case in seen:
            raise ValueError("Duplicate case path")
        seen.add(case)
        rows.append((item["queue_id"], eid, case))
    return rows

def classify(result, returncode, contracts_only):
    c = result.get("formal_contracts")
    if result.get("errors") or not c:
        return "ERROR"
    if c.get("total") != 14 or len(c.get("results", [])) != 14 or c.get("passed") != 14 or any(x.get("errors") for x in c["results"]):
        return "FAIL_CONTRACT"
    if returncode != 0:
        return "ERROR"
    if contracts_only:
        return "PASS_CONTRACT_ONLY"
    p = result.get("ppt")
    if not p:
        return "ERROR"
    if p.get("replacement_glyph_pages"):
        return "REVIEW_RENDER_FLAGS"
    return "RENDERED_MANUAL_REVIEW_REQUIRED"

def save(out, head, mode, rows, expected):
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    data = {"source_commit": head, "mode": mode, "selected": expected,
            "processed": len(rows), "counts": counts, "rows": rows,
            "can_ship": False, "approval_mutation": False,
            "a4_render": "NOT_IN_WORKER_SCOPE"}
    tmp = out / "summary.json.tmp"
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out / "summary.json")
    fields = ["queue_id","event_id","case","status","contract_passed","contract_total","error","result_path"]
    with (out / "summary.csv.tmp").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (out / "summary.csv.tmp").replace(out / "summary.csv")
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Fresh output directory outside repository")
    parser.add_argument("--contracts-only", action="store_true")
    parser.add_argument("--case", action="append", default=[], help="Repeat queue ID or event ID to select retry subset")
    parser.add_argument("--timeout", type=int, default=600, help="Per-case subprocess timeout in seconds")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("timeout must be positive")
    head = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git","status","--porcelain","--untracked-files=no"], cwd=ROOT, text=True)
    if dirty:
        parser.error("tracked working tree must be clean")
    cases = scope(ROOT)
    if args.case:
        available = {v for q,e,_ in cases for v in (q,e)}
        if set(args.case) - available:
            parser.error("unknown case selector")
        cases = [r for r in cases if r[0] in args.case or r[1] in args.case]
    out = Path(args.out).resolve()
    if out.is_relative_to(ROOT):
        parser.error("output must be outside repository")
    out.mkdir(parents=True, exist_ok=False)
    mode = "CONTRACTS_ONLY" if args.contracts_only else "CONTRACTS_AND_PPT_RENDER"
    rows = []
    save(out, head, mode, rows, len(cases))
    for q,e,case in cases:
        rel = case.relative_to(ROOT).as_posix()
        dest = out / q
        row = {"queue_id":q,"event_id":e,"case":rel,"status":"ERROR","contract_passed":None,
               "contract_total":None,"error":"","result_path":str(Path(q)/"qc.json")}
        try:
            if subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()!=head:
                raise RuntimeError("HEAD changed during batch")
            cmd = [sys.executable,str(WORKER),rel,"--out",str(dest)]
            if args.contracts_only:
                cmd.append("--contracts-only")
            run = subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=args.timeout)
            dest.mkdir(exist_ok=True)
            (dest/"stdout.log").write_text(run.stdout,encoding="utf-8")
            (dest/"stderr.log").write_text(run.stderr,encoding="utf-8")
            result = read(dest/"qc.json")
            if result.get("source_commit") != head or result.get("case") != rel:
                raise ValueError("Result provenance mismatch")
            c = result.get("formal_contracts") or {}
            row.update(status=classify(result,run.returncode,args.contracts_only),
                       contract_passed=c.get("passed"),contract_total=c.get("total"),
                       error="; ".join(result.get("errors",[])))
        except Exception as exc:
            row["error"] = repr(exc)
            dest.mkdir(exist_ok=True)
        rows.append(row)
        save(out,head,mode,rows,len(cases))
        print(q,e,row["status"],flush=True)
    data=save(out,head,mode,rows,len(cases))
    accepted={"PASS_CONTRACT_ONLY","RENDERED_MANUAL_REVIEW_REQUIRED"}
    return 0 if all(r["status"] in accepted for r in rows) and len(rows)==len(cases) else 1

if __name__ == "__main__":
    raise SystemExit(main())
