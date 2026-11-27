# C09-F1/F2 — 38건 합성 적재, 원본 아카이브 및 스냅샷 관리
2026-11-27. 평가 기준 c051dc3799fc0262413a9721087abfec11e30bb4. 실제 AI 데이터 미사용, 운영 NO-GO 유지.

## F1: 입력 계약과 아카이브
기존 C03-R1 실제 고정 스키마 및 40 code/name 순서를 재사용. ROOT-900~937 / FIXTURE-E900~937 / SYNTHETIC-900~937만 허용. 새 sidecar는 fixture='SYNTHETIC_ONLY', queue_id, event_id, model, revision, status='STORED', artifact_sha256 4종 정확 매핑. 기존 ZIP 4파일 + 별도 INTAKE_STATUS.json 선택; 운영의 기존 상태파일 실형식 호환 인증은 아님. 외부 ZIP 크기/안전경로, JSON 스키마 및 중복키, 정확한 표준명·40코드·CSV 판단/사유/출처, fact ID/절/페이지 정합, 위험 수식 차단; PDF 미실측 상태만 허용. 기준선 CSV 1520행 전체 exact grid, 원문 사유/반증 NULL 보존. 합성 source UNVERIFIED, validation SCHEMA PASS/IDENTITY NOT_EXECUTED/INDEPENDENCE NOT_EXECUTED/EVIDENCE HOLD.
SQLite 신규 intake_archive는 정상/동일 판본 충돌 원본 ZIP 및 별도 sidecar 또는 기준선 원본 bytes와 SHA256 묶음 fingerprint를 보관. artifact_bytes는 개별 5종 원본 파일 또는 공통 baseline CSV, intake_binding은 submission→archive 연결. 기준선 한 파일을 38개 제출과 연결. 정상 import와 audit은 동일 transaction; 실패 시 archive까지 rollback. 동일 raw ZIP/sidecar 또는 CSV는 NOOP, 동일 identity/revision 다른 바이트는 충돌 원본 보관(정상 submission 수정 금지). 따라서 ZIP 메타데이터 변경만으로도 충돌할 수 있다는 보수적 선택. 잘못된 형식의 제출은 validate 단계에서 거부되며 quarantine에는 미보관; malformed-input 격리 정책 별도. 원본 파일의 수정/삭제 차단 trigger, recursive trigger 적용. 실제 PDF 원본은 미사용, 합성 sentinel Git ref.
실제 full fixture 실행: 38사건×3 제출=114, 4560 ai_review, 76 외부 ZIP/상태 파일 쌍 + 1 기준선 CSV = 77 archive, 114 binding, 381 unique artifact_bytes (76×5+1); 저장 ZIP/sidecar 바이트 전수 동일, artifact hash/SHA1 blob 381/381 일치, eligibility 0. FK check 비어 있음, SQLite integrity ok. 1520 consensus 모두 PENDING_INPUT / selected_count NULL / responded_count 0. 실제 선정값·적격 승격 없음.

## F2: 명시적 결정 및 스냅샷
QA role + fixture actor + 이유 + latest submission 및 latest validation_run 연결, HOLD/REJECTED만 명시적 append-only 결정; 동일 결정 재호출 NOOP. ELIGIBLE 요청 거절(원문/독립성 미검증인 F1 입력을 승격하지 않음). 기존 C02 합성 eligible fixture의 명시적 decision은 읽을 수 있음. snapshot builder는 최신 제출 revision과 최신 eligibility decision을 사용하여 ELIGIBLE/HOLD/MISSING/INCOMPLETE를 분리하고, REJECTED는 HOLD 슬롯에 원래 decision_status로 보존. 최신 동일 fingerprint면 새 draft 정리 후 기존 snapshot 반환 NOOP, 과거 snapshot 재활성화 거절, 새 fingerprint면 append-only seal/audit. 기존 봉인 fingerprint 변동 없음. 38사건 full import에서 재봉인 후 snapshot 1개; 새 HOLD 결정 이후 다른 snapshot 생성, 과거 보존. 기존 9사건 core fixture(직접 SQL, F1 import 아님)에서 4 availability 혼합, 동일 snapshot NOOP, 360 판정 생성 PASS. 새로운 latest revision이 pending이면 예전 REJECTED/eligible 판단 자동 사용 금지.

## 시험 및 재현성
신규 test_f1f2.py 10/10 PASS (최종 전체 회귀 실행 1.870초): archive_immutable, bad_sidecar, baseline_conflict, conflict, decision_snapshot, full, latest_revision, mixed_core, real_id, rollback. C09-FINAL의 95개 시험 12 모듈 재실행 전부 PASS(기존 93 + 수용시험2). 이번 105개 PASS/0 FAIL, 신규 10, 과거 누적 207→217(재실행 중복 가산 안 함); 기존 112개 시험은 이번 미재실행.
Git 저장과 실제 시험 코드 blob 일치:
- importer/c09_f1_intake.py c232295c6940990a3743170ba59f5428d401c6b2
- db/c09_f2_snapshot.py d7adc2d02f8da6a0d1f5fd982cbbd48be13b682b
- tests/test_f1f2.py 5f447a0b872d8f877fe5c232bd41ea5e7b636dca
재현(전체 clone):
PYTHONPATH=integration_platform/db:integration_platform/consensus:integration_platform/importer:integration_platform/analytics:integration_platform/dashboard:integration_platform/tests python integration_platform/tests/test_f1f2.py
이번 로컬 실행은 C09-FINAL에서 확인한 복원 runtime, OPIS_CONTRACT_FIXTURE=/mnt/data/opis_c09c의 schema.json/names.json. 테스트 시작시 canonical SHA256 대조(기존 C09 기록과 일치). 실제 git read_contract 기본 경로는 작성되어 있지만 여전히 실행하지 않음. 전체 저장소 checkout/전체 회귀 아님.

## 남은 차단 요건
G04 38사건 합성 intake/5종 검증/원본 보존/충돌 격리는 범위 내 통과; 실제 등록 INTAKE_STATUS.json 형태/판본별 실제 metadata, baseline manifest 및 실제 38 queue/standard definitions 핀 검증, 파생 B provenance, 실제 계약 pin loader, 악성/invalid quarantine, archive backup restore/reopen/identity binding 재검증, 원본 ZIP bytes fingerprint와 core snapshot 연계(현재 artifact hash는 포함되나 intake_archive raw ZIP 묶음 hash는 미포함), 운영 파일/권한/용량 제한 미완료.
G05 synthetic HOLD/REJECTED/latest mixed/idempotent PASS, 실제 검증 근거·승인자에 의한 ELIGIBLE 생성 미구현; 검증 불충분 source는 immutable하므로 검증 증거가 포함된 새 revision 설계 필요. 기존 core digest에서 decision 없는 pending validation 기록 미반영 위험, explicit active snapshot pointer 및 stale 전문가 검토 표시, 모든 동일 내용/과거 재활성화 케이스 추가 시험 필요. QA role 인자는 인증 경계가 아니며 fixture clock 고정.
C06-R1 Django, C07-R1 실제 Excel, C08-R1 웹 연계, C09-F3 운영 수용/전체 회귀, B08 독립 QA 미완료. 전체 운영 수용표의 3 scoped PASS/9 BLOCKED 유지(G04/G05 합성 부분 개선만, 운영 gate 해제 아님). 실제 분석자료 통합 금지.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
