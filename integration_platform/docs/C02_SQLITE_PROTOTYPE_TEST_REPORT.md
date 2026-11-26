# C02 — SQLite 합성 전용 스키마 시제품 / 시험기록

2026-11-27. 기준 C01: a8bfd82524da5d9c84a19055f03985b25dc76626.
실행 파일 db/c02_sqlite.py. Git blob 6aa9704e607a5e1b53f7715a670931514feb3e53; 로컬 실행 파일과 GitHub 재조회 blob 일치.
실행: python integration_platform/db/c02_sqlite.py
SQLite 3.46.1 / in-memory / 외부 패키지 없음. 실제 사건·속성·모델 판정 적재 0. DB 파일 커밋 없음.

## ERD (논리 관계)
event → source_revision → submission → ai_review ← review_key ← attribute ← principle ← standard
submission → submission_artifact ← artifact (parent provenance)
submission → fact → fact_source; ai_review → review_source; ai_review ↔ review_fact ↔ fact (동일 submission)
submission → validation_run → validation_check; submission + validation_run → eligibility
snapshot → snapshot_slot (review_key + model + eligible submission / decision)
snapshot + review_key → consensus / expert_review; audit_event 별도.
실제 속성 표준은 합성 fixture로 대체하고, 사건 ID ROOT-* 삽입을 거부한다.

## 실행 결과
20/20 PASS:
38 events; 40 attributes; 1520 review keys; real event rejected; duplicate event; foreign key; unverified identity; premature seal; incomplete eligibility; role mismatch; cross-event review; atomic rollback; fact cross-reference; append-only review; 4560 explicit slots; missing cannot vote; sealed slots immutable; sealed snapshot immutable; foreign key check; integrity check.
슬롯 4560개는 MISSING fixture 상태로 생성; 실제 AI 투표가 아니다.
실제 승인 및 교차판정 미실행. approved=false; can_ship=false.

## C02-R1 잔여 수용시험 및 구조 보강 (C03 전에 완료)
- 합성 적격 승인 양성 경로, 잘못된 모델/사건/표준/승인 연결, HOLD/REJECTED, 검증 실패/미실행, 40행 미만/혼합 코드, eligibility 이력의 최신 유효성 시험 추가. 현재 eligibility trigger의 40행 및 PASS 체크는 실제 원본 검증·독립성 심사를 대체하지 않음.
- source_revision 및 submission 등 부모행 변경과 신규 validation_check 삽입에 따른 봉인/적격 기록 변동 방지. 직접 sealed=1 INSERT 차단, sealed 이후 review key grid 변경 방지, snapshot fingerprint 실제 계산, 표준별 완전성 및 사건/모델별 단일 revision 강제.
- D/I source/fact 필수 조건 및 출처 배열 타입·범위, artifact 종류/해시 형식/원본-파생 provenance 강화. 비적격 슬롯도 HOLD submission/decision 이력 추적 가능하게 보강.
- consensus/expert_review는 현재 저장 구조만 제공. snapshot별 키 정합, 봉인 필요, supersedes 동일 키 검증, 결과 불변 및 승인 서비스는 후속 단계. C04 판정 규칙, C06 인증/RBAC·전문가 이력과 연계.
- 운영 DB 파일, migration, Django ORM, 실제 적재·판정, 동시성·백업복원 및 배포는 미수행. 현재 메모리 DB만 지원하며 SQLite 운영 설정과 Django 버전 선택은 보류.
- C02 전체 수용을 주장하지 않음: core prototype test PASS, hardening OPEN. 실제 분석자료 사용 금지, main 자동 병합 없음.
