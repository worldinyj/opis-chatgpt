# C03-R1 — 정식 입력 구조 어댑터 및 DB 연결 구현
2026-11-27. 실제 외부 AI 판단자료 적재 금지; 합성 fixture ROOT-999 / FIXTURE-E999만 허용하고 내부 키 SYNTHETIC-999로 분리한다.

## 구현
- importer/c03_r1_adapter.py: 고정 Git commit 및 3개 계약 blob 검증 로더, 외부 AI Draft 2020-12 schema + date format, 40코드/명칭, 역할·판정·사유·사실 ID·쪽/절·CSV 직렬화 교차검증. 기존 B04의 source 표기 규칙을 사용한다. 실제 원본 CSV의 모든 허용 표기 형식을 지원한다고 보지 않는다.
- ChatGPT baseline 6열 CSV 어댑터: 40행, 검토키 및 역할 검증, 미제공 rationale은 NULL. DB baseline 적재 연결은 미구현.
- 외부 모델 DB bridge: C02-R2의 event/review_key/submission/artifact/source_revision/fact/source_ref/ai_review/validation/audit 관계에 연결하는 SQL 구현. 4개 artifact에 합성 Git ref sentinel을 사용한다. 원본 바이트는 입력 ZIP에서 해시 계산하되 DB bridge에는 해시/정규화 내용만 저장; 보관 위치 및 원본 바이트 보존 정책은 후속 게이트. 원본 PDF 없음, identity/independence NOT_EXECUTED, evidence HOLD, eligibility 행 생성 없음. 동일 개정판/내용 NOOP, 상이한 개정판 내용 충돌 기록, 전체 트랜잭션 롤백.
- importer/test_c03_r1_adapter.py: 실제 branch checkout에서 pinned contract 및 c02_r2.connect()로 실행하는 테스트 엔트리포인트.

## 이번에 실제 실행한 시험
Python jsonschema 4.26.0. GitHub 고정 스키마 JSON 내용과 40개 실제 표준 명칭을 로컬 복사하여 합성 자료만 검증했다. SQLite는 C02 기본 DDL의 관계 및 제약을 재현한 로컬 호환성 harness 사용; 전체 C02-R2 모듈의 실제 실행은 아님.
16/16 PASS (0.375s): baseline_null, claude, csv_source, date, gemini, name, page_gap, real_id, schema_approval, section, conflict, noop, positive, revision, rollback, two_models.
로컬 실행 파일 및 GitHub readback blob 일치:
- adapter ccdf82131716704b642dff1984b614a630d1a964
- tests f397becfac6be55bebfccb339221509582f64102
로컬 schema canonical (sorted keys, compact UTF-8) SHA256 326114a38cf2dcfe07d6d2204dec47f16d5bbde6a46a81445f7d26a259798f0c; 원본 Git blob의 byte hash와 다른 직렬화 지문이다.

## 미실행/잔여
실행 환경 DNS 제약으로 full clone 실패. 따라서 read_contract()의 실제 Git clone 로더와 C02-R2 전체 트리거를 포함한 시험은 미실행. C03-R1 전체 수용 완료로 승격하지 않는다. 실행 명령(저장소 develop/integration-platform checkout): python integration_platform/importer/test_c03_r1_adapter.py --repo .
C03 잔여: 실제 구조에 맞는 intake/provenance adapter, baseline DB bridge, 파생본의 원본 연결과 엄격한 출처 형식 호환, typed quarantine/failure handling, ZIP 중복/symlink/CRC 등 추가 시험, 전체 38x40x3 E2E. 위 기능은 합성 데이터로만 검증한다. C04 순수 교차판정 엔진은 이 연결 검증과 별개로 개발 가능하되 실제 snapshot 연결과 데이터 적재는 승인 전 금지.
approved=false / can_ship=false / main_merge=false.
