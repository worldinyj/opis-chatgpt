# C07-R1 — Portable XLSX planning and independent copy verification
2026-11-27. Base C 26ae8ddb1e803a12b0f226357558f2b6887866b2; main 8775c5ae6249cf0f8bcd70d513e3296cbb46343e. Synthetic only. No actual workbook or actual analysis import.

## 1. Existing contract and scope
Reopened main docs/THREE_AI_INDEPENDENT_REVIEW_V1.md (blob 9781e8f84b5916d31faf9f52ecde803b4eb2a1c8) and C07 prototype/test. Target 통합검토, header row 3, data 4–1523, key A, queue B, event C, attribute H; Gemini P/Q/R and Claude S/T/U; ChatGPT O, formulas V/W/X/AC, expert Y:AB protected. The actual OPIS_38건_3AI_교차검토_전문가판정_V1.xlsx is absent from the untruncated pinned main tree (no xlsx) and current conversation file inventory (no xlsx/xls). No new actual Drive search in this turn. Exact real header names, sheet structure, formats unknown; synthetic headers deliberately distinct, A1 marker SYNTHETIC_ONLY and synthetic keys required.
Decision: dependency reduction by separating read-only planning and verification from actual workbook writing. Python stdlib zipfile/XML/JSON/hashlib only for portable module; existing C07 exporter retained; artifact_tool alone used for synthetic workbook creation/editing. No alternate workbook editing library, no automatic workbook modification in portable module, no claim that full Excel export is dependency-free.

## 2. Implementation
excel/c07_portable.py: bounded read-only OOXML ZIP inspection (32 MB compressed and expanded aggregate, 1000 entries), exact visible sheet relation, shared/inline text, address bounds, normal formulas vs literal text, external relationships/active content/unsafe XML rejected, duplicate rows/cells rejected; unsupported protected sheet/shared or array formulas rejected. Exact synthetic headers and 40-code per event grid, 40/1520 rows only, event ID uniqueness, key-based model mapping, one eligibility reference per included complete event, role→result, synthetic eligible refs only, text length/empty/formula-injection checks, blank and unmerged target cells. No actual DB eligibility lookup; fixture ref is not real authorization. Records JSON list has key, queue_id, event_id, code, model, availability, eligibility_ref, role, result, rationale, source. Output JSON plan with source SHA256, canonical records and plan hash, exact target cell addresses/text; exclusive new output file, source unchanged check.
verify_target_sheet_copy: recompute plan from source and records, compare all nonblank target-sheet literal values/formula strings and merge ranges against expected copy, ignore equivalent blank representation and cached formula results. Detect modifications outside target columns and formula injection; explicitly does not verify styles, conditional formatting, data validation, charts, workbook relationships, other sheets or formula recalculation. Read-only, not general OOXML security certification; strict format limitations can reject legitimate Excel files. Actual approved template adaptation and DB binding remain open.

## 3. Actual test results
- python -S test_c07_portable.py: 17/17 PASS (0.136s last run), no external packages/site imports. Both models full 1520-key plan, reverse record order, complete subset, partial/duplicate/hold/mixed ref, wrong header/identity/real ID, unsafe text, target nonempty/merged, extra master row, protected cell mutation, XML text/duplicate/unsafe/shared formula.
- test_c07_portable_roundtrip.py: 2/2 PASS (9.452s) executed in artifact_tool environment, full single-sheet synthetic 1520 rows, reverse record order, plan-derived bulk writes to separate copy for each model, actual XLSX export and read-only verification. Each 4560 target cells, 3040 existing formulas (V and AC) preserved; O and Y values preserved; all other cells in this synthetic target sheet unchanged except permitted targets; original raw bytes unchanged. Total 9120 planned/applied cells across two independent copies; not both models in one cumulative copy. No actual V/W/X/AC full template structure or features verification; fixture has V and AC formulas only.
- CLI actual synthetic XLSX: python -S c07_portable.py ... --model GEMINI plan and --verify-copy both return success 1520/4560 and original SHA unchanged. Manual extra two-model file verification hashes: source 24ee66f771e84b5e40f7fc67e912f31b538dc6c0e8559546d917c0facdf3e8fb, Gemini c047b2d4c2a6b214d5e822e3882b65dfc46b2128543e6198ba73ecb6541d6557, Claude b26bdcb5ac402f67647b8c48c3b8028b5b4486e164f75b9da7023f1ded697b51. Temporary artifacts not committed.
- Updated local/run_local_suite.py: register C07-PORTABLE (17, no deps), C07-ROUNDTRIP (2, artifact_tool), check portable module against HEAD; prior C07 remains artifact_tool dependent. 22 suites / expected 240 tests (221+19). Existing runner tests 7/7 re-run PASS (2.965s). Whole local suite and Django runtime not executed in this turn.
New unittest 19 PASS, existing regression 7 PASS, current 26 PASS / 0 FAIL; historical cumulative 238+19=257, no duplicate addition.
Local tested source hashes verified on repo:
c07_portable.py b1f54f608aad3922fc59d12ef444514be5e45798
test_c07_portable.py 3c8318edc8b749239f95a79218699ef66a724595
test_c07_portable_roundtrip.py 9e5d19034921caf796377cd7964b65d1e800bf21
run_local_suite.py d332fc2b2df5ad50b6042c880ef12d7efbe71742

## 4. Reproduction
From integration branch checkout:
```
python -S integration_platform/excel/test_c07_portable.py
python integration_platform/excel/test_c07_portable_roundtrip.py
python integration_platform/local/test_local_runner.py
```
Second command requires artifact_tool. The first needs only Python stdlib. On an appropriate synthetic fixture with the documented synthetic header/marker:
```
python -S integration_platform/excel/c07_portable.py synthetic.xlsx fixture_records.json plan.json --model GEMINI
python -S integration_platform/excel/c07_portable.py synthetic.xlsx fixture_records.json audit.json --model GEMINI --verify-copy copy.xlsx
```
JSON output is an edit plan or audit, not an executable workbook; use only synthetic input and never copy unverified data into actual template. Existing full local runner guide's 20/221 counts are historical; now 22/240 expected. A missing artifact_tool still blocks the old C07 and full XLSX roundtrip, does not block standard-library planner/verifier.

## 5. Remaining gate
G08 remains BLOCKED for actual operation. Obtain exact template and hash, inspect real headers and all formulas/format/validation/features across sheets; develop approved copy workflow bound to actual eligible immutable snapshot and test real template preservation on authorized copy. No actual AI values or original workbook edited. C09 full checkout/Django actual runtime, complete actual metadata census, B independent QA remain outstanding. Next C10-PRE read-only registration metadata census in bounded batches and eligibility evidence inventory; actual import prohibited until technical gates and explicit authorization. Do not count status registration as eligibility.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
