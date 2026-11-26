# C03 — ZIP/JSON/CSV synthetic staging importer

2026-11-27. implementation: importer/c03_staging.py.
Local execution: python /mnt/data/opis_c03/c03_staging.py; 18 tests ran in 0.036s, OK.
Git blob 557d7247bb01c3711ea9a217b5438863c23cfb89 matches executed local file and GitHub readback.

## Scope
Synthetic fixture contract only; no production data, no approval, no automatic integration. In-memory staging SQLite is separate from C02-R2 core DB. Exact four submitted files: review.json, excel_import.csv, report.md, validation.md. Intake record and production schema adapters are subsequent work. ZIP read in memory, no extraction, exact flat names, bounded compressed and expanded size, regular unencrypted files, supported compression. JSON duplicate keys, 40 standard code keys, role/result consistency, fact membership, source page range and ledger page coverage, CSV quoting/header/rows and JSON alignment, formula prefixes. Artifact bytes and SHA256 stored unchanged. Deterministic content fingerprint; same revision and content is NOOP, changed content is conflict audit (hash only, not persisted conflicting archive). Entire valid submission transaction atomic.

## 18 executed tests
approval, conflict, csv_mismatch, duplicate, duplicate_json, expansion, fact, formula, ledger_gap, noop, partial, positive, real_identity, revision, role, rollback, source_range, traversal: 18/18 PASS.
No real input, production schema validation, C02-R2 bridge, actual consensus or expert decisions executed.

## C03-R1 remaining
Use pinned neutral queue/standard/schema, genuine external review format and baseline-specific adapter with synthetic fixtures conforming to production shape, without loading real submissions. Integrate atomic staging-to-C02-R2 mapping for source revisions, immutable artifacts, facts, reviews and validation; preserve pending eligibility. Check all expected artifacts and original/derived provenance; no reliance on model self-attestation. Implement bounded/typed failure and quarantine record, explicitly decide whether rejected bytes may be stored. Test duplicate ZIP names, symlink/encryption, bad CRC, wrong type, section/CSV location equivalence, and transaction failure at bridge. Harden staging against direct SQL mutation (including REPLACE via recursive triggers and late child inserts); current app-level prototype is not a production authorization boundary. 38x40x3 end-to-end staging test deferred. C04 consensus engine after adapter milestone; actual import only C10 with approval.

approved=false / can_ship=false / main_merge=false.
