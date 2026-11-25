#!/usr/bin/env python3
"""Offline case QC: formal contracts + existing PPTX audit + actual render.
Never changes release state, expert approvals, or the intake queue.
Requires Python jsonschema, python-pptx, lxml, pymupdf; Node.js; LibreOffice.
Run from a checked-out repository, with output outside the source case.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[2]
PATHS = [
    ("fact_ledger", "fact_ledger.json"),
    ("learning_ledger", "learning_ledger.json"),
    ("discussion_action", "discussion_action/manifest.json"),
    ("production", "incident_understanding/production.json"),
    ("production", "safety_culture_learning/production.json"),
    ("production", "shorts/SHORT-01/production.json"),
    ("batch_job", "safety_culture_learning/batch_job.example.json"),
    ("batch_job", "shorts/SHORT-01/batch_job.example.json"),
]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def hashes(path):
    b = path.read_bytes()
    return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "git_blob": hashlib.sha1(("blob %d" % len(b)).encode() + bytes([0]) + b).hexdigest()}

def tracked(path):
    rel = path.relative_to(ROOT).as_posix()
    expected = subprocess.check_output(["git", "rev-parse", "HEAD:" + rel], cwd=ROOT, text=True).strip()
    h = hashes(path)
    if h["git_blob"] != expected:
        raise ValueError("Working copy differs from HEAD: " + rel)
    return h

def contracts(media):
    from jsonschema import Draft202012Validator
    results, schema_hashes, input_hashes, schemas = [], {}, {}, {}
    for name, rel in PATHS:
        sp = ROOT / "video/schemas" / (name + ".schema.json")
        ip = media / rel
        if name not in schemas:
            schema_hashes[name] = tracked(sp)
            schemas[name] = read(sp)
            Draft202012Validator.check_schema(schemas[name])
        input_hashes[rel] = tracked(ip)
        errors = sorted(str(e.json_path) + ": " + e.message
                        for e in Draft202012Validator(schemas[name]).iter_errors(read(ip)))
        results.append({"test": "schema " + rel, "errors": errors})
    validator = ROOT / "video/scripts/validate_contract.mjs"
    validator_hash = tracked(validator)
    js = """
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const [validator,base]=process.argv.slice(1);
const {validateRelations,validateBatch}=await import(pathToFileURL(validator).href);
const read=p=>JSON.parse(fs.readFileSync(path.join(base,p),'utf8'));
const f=read('fact_ledger.json'),l=read('learning_ledger.json');
const paths=['discussion_action/manifest.json','incident_understanding/production.json','safety_culture_learning/production.json','shorts/SHORT-01/production.json'];
const r=paths.map(p=>({test:'relations '+p,errors:validateRelations(read(p),f,l)}));
for(const dir of ['safety_culture_learning','shorts/SHORT-01']){
 const p=dir+'/batch_job.example.json';
 r.push({test:'batch '+p,errors:validateBatch(read(p),read(dir+'/production.json'))});
}
console.log(JSON.stringify(r));
"""
    run = subprocess.run(["node", "--input-type=module", "-e", js, str(validator), str(media)],
                         check=True, capture_output=True, text=True, timeout=120)
    results.extend(json.loads(run.stdout))
    return {"engine": "jsonschema " + version("jsonschema") + " Draft202012Validator + repository Node validator",
            "schema_meta_checks": len(schemas), "input_hashes": input_hashes,
            "schema_hashes": schema_hashes, "validator_hash": validator_hash,
            "passed": sum(not x["errors"] for x in results), "total": len(results), "results": results}

def ppt_render(deck, out):
    import fitz
    import importlib.util
    info = tracked(deck)
    audit_path = ROOT / "education/ppt/quality/audit_pptx.py"
    audit_hash = tracked(audit_path)
    spec = importlib.util.spec_from_file_location("audit_pptx", audit_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.preflight(deck)
    with tempfile.TemporaryDirectory(prefix="opis-lo-") as tmp:
        tmp = Path(tmp)
        subprocess.run(["libreoffice", "-env:UserInstallation=" + (tmp / "profile").as_uri(),
                        "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(deck)],
                       check=True, capture_output=True, timeout=180)
        pdf = tmp / (deck.stem + ".pdf")
        if not pdf.is_file():
            raise RuntimeError("LibreOffice did not produce PDF")
        dst = out / "classroom_render.pdf"
        dst.write_bytes(pdf.read_bytes())
    if hashes(deck) != info:
        raise RuntimeError("PPTX changed during rendering")
    result = mod.audit(deck, producer="REPOSITORY_GENERATOR", pdf=dst)
    with fitz.open(dst) as doc:
        flags = []
        pages = out / "pages"
        pages.mkdir(exist_ok=True)
        for i, page in enumerate(doc, 1):
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(pages / f"page-{i:02d}.png")
            if "\ufffd" in page.get_text():
                flags.append(i)
    result.update({"input_hash": info, "audit_script_hash": audit_hash,
                   "replacement_glyph_pages": flags,
                   "visual_review": "PENDING", "status": "MANUAL_VISUAL_REVIEW_REQUIRED"})
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("case", help="Case path, e.g. cases/2011/110419K34")
    p.add_argument("--out", required=True)
    p.add_argument("--contracts-only", action="store_true")
    args = p.parse_args()
    case = (ROOT / args.case).resolve()
    if not case.is_relative_to(ROOT / "cases"):
        p.error("case must be under repository cases/")
    out = Path(args.out).resolve()
    if out.is_relative_to(ROOT / "cases"):
        p.error("output must be outside cases/")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "qc.json").exists() or (out / "classroom_render.pdf").exists() or (out / "pages").exists():
        p.error("choose a fresh output directory")
    result = {"case": case.relative_to(ROOT).as_posix(),
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "can_ship": False, "formal_contracts": None, "ppt": None, "errors": [],
              "author_technical_qc": "PENDING", "queue_advanced": False}
    try:
        result["formal_contracts"] = contracts(case / "media")
    except Exception as exc:
        result["errors"].append("contracts: " + repr(exc))
    if not args.contracts_only:
        try:
            decks = list((case / "media/classroom_ppt").glob("*.pptx"))
            if len(decks) != 1:
                raise ValueError("Expected exactly one classroom PPTX")
            result["ppt"] = ppt_render(decks[0], out)
        except Exception as exc:
            result["errors"].append("ppt: " + repr(exc))
    (out / "qc.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    c = result["formal_contracts"]
    return 1 if result["errors"] or not c or c["passed"] != 14 or c["total"] != 14 else 0

if __name__ == "__main__":
    raise SystemExit(main())
