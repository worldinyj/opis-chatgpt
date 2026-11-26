# C01 — OPIS 통합 분석·전문가 검토 플랫폼 아키텍처 V1

## 1. 목적 및 범위
38개 사건 × 40속성 × 3개 모델의 독립 판단을 원본·버전·판본·검증 이력과 연결하여 보존하고, 교차검토 및 전문가 판단을 지원한다. 목표 1,520개 사건-속성 키와 4,560개 모델별 판단 슬롯은 목표 규모이지 현재 적격 데이터 수가 아니다. 원전 안전문화 교육·연구 지원용이며 공식 규제 평가나 현장 조작 지침이 아니다.

기준 스냅샷: `fa145c17aff92e3ccf21ded05d0e85f545b0ab22` (ChatGPT 38건, Gemini 38건, Claude 11건 등록). 등록·통합 적격·내부 합의·전문가 승인·배포는 별개다. 현 단계는 설계 및 합성 시험 데이터만 사용; 실제 AI 판단의 통합 실행 금지.

## 2. 독립 개발과 시스템 경계
- Track A main: 모델별 원본 및 진행기록. Track B develop/gemini-quality: quality_remediation/에 파생 보완자료. Track C develop/integration-platform: integration_platform/만 수정.
- C는 B의 진행 상태나 원본 폴더를 수정하지 않는다. B의 파생 CSV는 명시적 승인 및 입력 계약 검증 이전에 사용하지 않는다. branch/path 분리만으로 접근권한 또는 독립성이 보장되지는 않으므로 Claude/Gemini 독립 분석 환경에는 타 모델 자료 및 비교 결과를 제공하지 않는다.
- 공통 표준·기준선·원본 보고서·기존 Excel 보호. 실제 파일 입력은 명시적으로 지정한 commit과 manifest에서만 읽는다. main 최신본을 자동 추종하지 않는다. 승인 없이 merge·배포하지 않는다.

## 3. 기술 선택 (제안 ADR-001)
Python 3.12 호환, Django 5.2 LTS 계열 후보, SQLite 단일 파일을 초기 로컬/소규모 검토 환경에 사용한다. 라이브러리 버전은 C02에서 설치 및 테스트 후 고정. SQLite FK ON, 트랜잭션, 짧은 쓰기, WAL은 환경 검증 후 선택; 여러 동시 편집자·네트워크 파일 공유가 필요한 배포는 PostgreSQL 전환 검토. ORM과 도메인 서비스 분리, 순수 Python 판정, SQL 백엔드 독립 인터페이스. 외부 LLM API 호출 없이 동작하는 검토 플랫폼 우선. 기존 K-NSCA에 직접 쓰지 않고 향후 읽기 전용 연계 계약 설계. 실제 웹앱/DB는 C02 이후 개발.

## 4. 입력 및 데이터 계층
| 입력 | 규약 | 처리 |
|---|---|---|
| 중립 큐 | queue_id, event_id(문자열), event_year, expected PDF metadata, order | 사건 마스터; filename은 힌트 |
| 40속성 JSON | standard_version, 원칙/코드/명칭/정의 | 버전별 속성 마스터 |
| ChatGPT baseline CSV | review_key, queue_id, event_id, attribute_code, role, chatgpt_review_result | 동결 1520행, 외부 스키마를 강제하지 않음 |
| ChatGPT baseline manifest | 기준 commit, packet blob 38건, reference blobs | 근거 추적; 후보 패킷에 없는 사유는 미제공 표시, 생성 금지 |
| 외부 AI review.json | 공통 schema v1.0, facts, attributes, source_refs, limitations | 정식 schema 및 교차검증, 원본 bytes/hash 보존 |
| report.md, CSV, validation.md, INTAKE_STATUS.json | original blob/sha, 검증 상태, 보고된 제한 | 판정과 분리한 provenance; 제출 검증만으로 적격 아님 |
| B 파생 CSV | 원본 review/CSV blob, 파생 blob/sha256, 변환 규칙, diff, 검증과 승인 이력 | 원본 JSON의 역할/결과/사유/근거 불변; 원본과 파생을 명확히 구분 |

원본 PDF는 저장소에 복사하지 않고 승인된 내부 저장소 locator와 검증 상태를 저장한다. 물리/인쇄쪽은 구분. 비공개 내용 복원 금지.

## 5. 논리 데이터 모델 (C02 ERD/DDL의 요구사항)
- event(queue_id PK, event_id unique text, event_year, source expectation); standard_version / principle / attribute(standard_version+code unique); review_key(event + attribute + standard version unique).
- source_revision: event, reported filename/report number, expected/observed hash/pages 별도, verification status, access/read scope; 실제 검증자·시각·근거.
- artifact: immutable Git ref/blob, SHA-256 provenance, path, artifact_kind, model, revision, original/derived, parent_artifact; 동일 artifact 중복 적재 방지.
- submission: event, model/provider/version/run_date, source_revision, revision, artifact set, independence declaration & limitations; 모델/사건/버전별 유일성 및 충돌 관리. source hash mismatch는 quarantine.
- ai_review: submission + review_key unique, D/I/A/H/P/N, result, rationale(nullable for baseline when unavailable), counterevidence, availability; 40행/제출 및 역할→결과 invariant. 누락은 빈 슬롯이지 가짜 N 행이 아님.
- fact: submission + local_fact_id unique, summary/kind/limitation; fact_source_ref와 review_source_ref: section, printed_pages, pdf_pages, summary; review_fact_link는 같은 submission 내부 fact만 참조.
- validation_run/check: 입력 artifact refs, validator version, check name, PASS/FAIL/HOLD/NOT_EXECUTED, details, timestamp, actor; append-only.
- eligibility_decision: submission revision + evidence of validation, independent-source and independence review, explicit decision/reason/actor/time; 승인된 입력만 snapshot 활성화. HOLD와 미확보를 혼동하지 않는다.
- integration_snapshot: frozen neutral queue/standard/baseline references and selected revision for each event/model; fingerprint; immutable after seal. Partial snapshot 허용, 부적격/누락은 별도 availability. Snapshot별 review_key당 3 slots.
- consensus_result: snapshot + review_key + rule_version unique, three vote references, selected/responded counts, status, reason; no overwriting model opinions.
- expert_review: snapshot + review_key, decision, rationale, authenticated reviewer/time, revision, supersedes, approval state; expert decision history append-only. 동일 키 신규 snapshot 입력 변경 시 기존 전문가 판단을 STALE_REVIEW_REQUIRED로 표시하고 자동 승계 금지.
- audit_event: actor, action, target, timestamp, before/after refs and reason. role based authorization (importer/QA/expert/approver/reader). 실제 RBAC 및 개인정보 보호는 웹앱 단계 구현·시험.

## 6. 처리 흐름 / 트랜잭션
1. 지정된 snapshot의 입력 ref와 blob 검증. 큐 및 표준/기준선 보호 확인. 외부 AI 검증 및 B 보완 검증 기록을 읽되 신뢰성 별도 확인.
2. Staging(원본 잠금·스키마·40코드·CSV·출처·중복·판본·독립성 기록). 전체 제출 단위 atomic transaction; 동일 키 동일 artifact는 no-op, 충돌은 quarantine; 부분 적재로 40행 미만을 완료 처리하지 않는다.
3. 적격성 검토를 append-only로 기록. STORED/PENDING_INTEGRATION은 투표 자격이 아니다. 원본 검증 및 독립성 요건 해소, 검증과 승인 기록이 있어야 별도 적격성 결정 가능. 적격성 승인은 최종 전문가 속성 승인과 별개.
4. Snapshot 봉인 후 eligible vote만 비교. 실패/보류/미확보/미검토는 pending. Snapshot 바뀌면 새 계산 및 전문가 판단 재검토. 실제 반영은 C10 이후 사용자 승인.
5. 전문가 화면: 3 모델 원본 사유·근거·제약 표시, 내부 합의/전문가 판단 구분, 원문 조회 권한, 의견 변경 이력. 0표 항목도 전문가 확인; 일괄 확인 시 대상 목록과 이유를 기록하고 누락/부적격 항목을 섞지 않는다.
6. Excel은 승인된 snapshot에서 복사본으로 내보낸다. 기존 수식/판정/ChatGPT 열을 변경하지 않으며 P/Q/R 및 S/T/U 등 계약은 C07에서 실제 양식 재확인. 다운로드는 기록; 공개 배포 금지.

## 7. 교차판정 규약 (rule_version 1.0 설계)
역할 D/I→선정, A→판단보류, H/P/N→미선정. 세 모델 각각 적격하고 완전한 판단이 있어야 비교 가능. 적격 A는 응답이지만 선정 표 아님. A가 있는 경우 자동 확정하지 않고 전문가 검토.
- 미확보·HOLD·미적격·불완전 중 하나라도 존재: PENDING_INPUT. 0표와 혼동 금지.
- 세 모델 모두 적격 + 세 선정: INTERNAL_CONSENSUS_SELECTED. 프로젝트 내부 합의 후보로 기록; 공식 최종 전문가 승인이나 배포 아님.
- 세 모델 모두 적격 + 선정 0/1/2: EXPERT_REVIEW_REQUIRED. 0은 자동 미선정이 아니다.
- 전문가 최종 판단은 별도 기록으로 관리. 사용자 승인 없이 실제 승인 플래그 true로 변경 금지.
- 일치도: 결측과 적격성 보류를 분모에 숨기지 않는다. 원 3범주와 선정 이진 지표를 구분, Jaccard 공집합 및 kappa 분모 0은 undefined/NA 명시. 전문가 확정 이후에만 성능 평가 가능. 다수결 자체는 진실값 아님.

## 8. 비기능 요구사항
로컬/승인 환경 우선, 개인·사내자료 최소화, 인증 및 역할별 권한, CSRF·입력 검증·템플릿 escaping, CSV 수식 주입 방지, Git/DB 비밀정보 배제. 임의 SQL/경로/실행 금지. DB backup/restore 검증, 감사 이력, 동시 쓰기 충돌 처리, idempotence, 명시적 snapshot. 합성 데이터는 SYNTHETIC marker 및 별도 DB 사용, 실제 데이터와 혼합 금지. DB/개인정보/원본 PDF는 Git에 커밋하지 않는다. 초기 목표는 38건 규모의 정확성; 성능 수치는 시험 후 제시.

## 9. 완료 기준 및 제한
C01은 입력 계약·논리 모델·상태 전이·수용시험 설계·로드맵 산출까지. DDL, Django 앱, 실제 적재/판정, 원문 검증, 테스트 실행, CI 및 배포는 미수행. 개발 브랜치만 생성하고 main과 B 브랜치 불변 검증. C02에서 SQLite 스키마 및 합성 데이터 FK/UNIQUE/CHECK/트랜잭션 테스트 구현. 기존 Phase 4-A 로드맵을 대체하지 않고 C02~C11과 매핑한다.

approved=false / can_ship=false
