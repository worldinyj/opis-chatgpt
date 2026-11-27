# C09-C / C09-R2 — 적재기 및 보호 DB 전문가 초안 연결 검증
2026-11-27. 기준 C branch 78312ba8687b61c8663bcd5154f3a78e84441ef5. 합성 입력 전용. 실제 AI 자료/전문가 승인 없음.

## C09-C 입력부터 판정 및 통계까지
기존 C03-R1 adapter 전체 파일을 복원하여 git hash-object ccdf82131716704b642dff1984b614a630d1a964 일치. staging의 def validate 이전 실행 부분 SHA256 98f525e63ede82c50f2ec140ae7407142d0cd9afb24988cb682e482e52ab6887, zip_bytes 함수(종료 LF 하나) 89ed32120d0ce3d5b59052f6525cb4f58c2dbff6fd8fbb438f2f4734144d50a9 각각 GitHub 원문 동일 부분과 일치. staging 전체 파일이나 이전 18개 시험 재실행은 아님.
고정 원본 ref fa145c17aff92e3ccf21ded05d0e85f545b0ab22의 실제 schema JSON 전체(정렬/compact UTF-8 canonical SHA256 326114a38cf2dcfe07d6d2204dec47f16d5bbde6a46a81445f7d26a259798f0c) 및 standard 원칙 순서별 40 code/name 배열(UTF-8 compact JSON SHA256 b003748ae407fd953ee12727dd9862ae735238cc307c976dd286b44bc6fc42b1) 로컬 복원 및 원문과 대조 일치. Git clone 불가로 read_contract의 실제 git cat-file 실행은 여전히 미실행; 큐 전체나 표준 정의 전체를 로컬로 복제하지 않았음. C02/R1/R2는 이전 C09에서 원문과 대조한 runtime prefix 재사용. jsonschema 4.26.0.
신규 importer/c09_import.py blob 61034fdd69a5be06536513517df0873d06726368, tests/test_c09_import.py blob df2cfacfd33e7907921db5c0ba504a5657c49397.
- 외부 모델 production-shape 합성 ZIP 두 개를 기존 adapter로 schema/CSV/근거 구조 검증 후 실제 C02-R2 핵심에 저장. ChatGPT 합성 6열 baseline CSV를 신규 baseline bridge로 저장; rationale/counterevidence NULL 유지. 원본 파일의 hash와 Git blob 형식 기록, 합성 sentinel ref. 적격 판정 생성 금지.
- 보류 전용 seal_pending: 가상 사건 ROOT-999→SYNTHETIC-999 하나, 모델별 최신 제출판본(개정번호 최대) 조회, 아직 적격 결정 없는 제출은 INCOMPLETE(통합 준비 미완료 의미), 제출 미확보는 MISSING, 모두 봉인 provenance 유지. 모든 실제 eligibility 결정이 있는 DB는 이 함수에서 거부. 데이터가 존재함과 적격 응답을 분리.
- 3개 제출/120개 ai_review/120 slots/40 consensus, 전체 PENDING_INPUT, selected_count NULL, responded_count 0, 통계 완전사례 0. Gemini만 있을 때 INCOMPLETE 40/MISSING 80. 합성 데이터라 PDF 검증/독립 검토/의미 판정 미수행이므로 정상적인 차단 결과.
- 신규 7/7 PASS (최종 0.418초): baseline, eligibility_denied, external, external_conflict, missing, rollback, three_model_pipeline. 두 모델 적재, baseline 중복/충돌, 외부 개정판/중복/충돌, 40행 rollback, 적격 우회 거절, 판정/통계 연계. 실제 38사건 ZIP 적재는 아님.
- 재현(완전 clone): PYTHONPATH=integration_platform/db:integration_platform/consensus:integration_platform/importer:integration_platform/analytics python integration_platform/tests/test_c09_import.py --repo .
- 이번 로컬 실행은 --local-fixture (대조된 schema.json 및 names.json이 작업 디렉터리에 존재). 이 로컬 모드는 repo 계약 파일의 실제 pin 조회를 대체하지 않음. 신규 두 소스의 로컬 실행 파일 Git blob = GitHub readback.
제한: 기존 C03 staging DB를 거치지 않고 C03-R1이 ZIP/CSV 검증 후 core에 직접 적재. 원본 바이트 보관/격리 아카이브 미구현(충돌 해시 및 감사만), full queue/multi-event importer/정식 적격 결정 및 snapshot builder 미구현. 동일 입력 seal_pending 반복시 동일 fingerprint unique 충돌 가능(자동 NOOP 미구현). baseline에는 원문 근거/판단 사유 없는 상태를 보존. 실제 적격 promotion을 수행하지 않는다.

## C09-R2
db/c09_connection.py blob c193979a59a4dff52eabc2428faef5b5a6976b83, tests/test_c09_connection.py blob fb15b6c747d236d9e740931e4ff2b154e77a8266. 신규 synthetic connect()에서 C09 guard 기본 설치, reopen()에서 FK/recursive trigger, location/digest/guard UDF 등록과 필수 트리거 이름 및 FK 검사. 기존 C02-R2 connect 자체는 변경하지 않음. 핵심 expert_review 및 audit_event 동일 DB에 atomic 초안 저장, EXPERT role, fixture actor, 현재 봉인 snapshot(max id라는 합성 정책) 및 해시, revision, pending gate. 승인 상태 DRAFT만 기록. 시각은 합성 고정값.
8/8 PASS (0.420초): conflict, default, draft_revision, pending, reopen, role, rollback, stale. stale 시험은 제출 fingerprint 불일치; 실제 새 snapshot 전환 및 기존 검토 표시 시험은 후속. 재개방 트리거 제거시 차단. 로컬 실행 파일 blob = GitHub readback.
재현: PYTHONPATH=integration_platform/db:integration_platform/consensus:integration_platform/analytics:integration_platform/dashboard:integration_platform/tests python integration_platform/tests/test_c09_connection.py
제한: 역할/actor는 호출 인자이고 웹 인증 아님. 기존 C06 Django adapter 전환/실행, 실제 DB 파일 연결 보안 경계/허용 경로, trigger 정의 해시·스키마 migration 검증, 관리 SQL 차단, 현행 snapshot 명시 지정 정책, 새 snapshot에 대한 stale 표시, 동시성/운영 부하 시험 잔여. reopen은 트리거 이름 확인이지 정의 인증이 아님. 직접 SQL 관리자 보안 경계가 아니다. 실제 승인 권한 미구현.

## 후속
신규 unittest 15개 PASS; 누적 205개(각 단계 개별 시험 합계). C09-A/B/R1의 38사건 core→analytics→dashboard 시험은 직접 fixture SQL, 이번 C09-C는 1사건 실제 합성 ZIP/CSV→core→판정/통계. 이를 합쳐 38사건 full-import E2E 완료라 주장하지 않는다. C07-R1 실제 Excel 원본 미확보, C06-R1 Django 실행 미수행, C09-FINAL 통합 수용 및 회귀시험 대기. Track B 7 HOLD/독립 QA 및 명시 적격 결정 대기. C10 실제 반영 금지.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
