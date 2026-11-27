# C06 및 C05-R1 — 전문가 검토 서비스와 그룹 통계
2026-11-27. 합성 시험 전용. 실제 분석·적격성·전문가 승인·배포 없음.

## C06
expert_review/c06_review.py (Git blob c0096ba0554d29ac75752dfc25050a198366f310). 독립 in-memory SQLite 서비스, 기존 C02-R2 DB와 아직 연결하지 않음. EX­PERT/QA/READER 역할별 접근, EXPERT만 초안 작성, 현재 스냅샷 일치 및 예상 revision 검증, 보류 입력의 판단 기록 금지, 이유 필수, 이전 검토 연결, 새 snapshot에서 이전 판단 자동 승계 금지, 초안/감사 원자적 기록. 변경/삭제 방지 트리거, REPLACE 대응 recursive_triggers 설정. 승인 상태 DRAFT만 허용.
실제 실행: python integration_platform/expert_review/c06_review.py. 10/10 PASS (0.012s): conflict, denied, empty_reason, immutable, no_real, pending, read_roles, revision_chain, rollback, stale. 실행 파일의 Git blob과 GitHub readback 일치.
Django adapter: expert_review/django_views.py, templates/opis_fixture/review.html, __init__.py, requirements.txt. 로그인·활성 fixture 계정 및 단일 그룹 역할 확인, CSRF 보호 데코레이터, POST 초안 기록, GET 상세 화면, 템플릿 기본 escape 사용. Django 미설치; pip install Django>=5.2,<5.3 실패 (사용 가능한 배포판 없음). Django 코드와 템플릿은 작성만 했고 실행/렌더링/CSRF/인증/URL 테스트 미수행. 실행 가능한 프로젝트 설정, DB connection factory(동일 합성 DB 유지), Django 마이그레이션/테스트클라이언트, 실제 C02-R2 snapshot bridge, 전체 3AI 근거 비교 화면, 이력 전체 조회, DB 수준 insert 제약과 검토시각/인증 감사, 다중 사용자 동시성 및 RBAC 테스트 필요. 현재 서비스 role/actor는 호출자가 제공하는 값이며 실제 인증 경계가 아님. 실제 배포 금지.

## C05-R1
analytics/c05_r1_groups.py (Git blob f1823fc80224979089775316b63d98a985f7e716).
합성 38사건/1520키/4560슬롯, 10원칙, 40속성, 3개 가상 발전소, 2개 가상 연도, 사건별 집계. 그룹별 키와 완전 사례 합계가 전체와 일치. 모델별 pairwise와 공통 3AI complete-case 분모를 구분. 미확보·HOLD·불완전은 분모에서 제외하고 상태와 응답 수 기록. 실제 발전소명 및 실제 큐 자료 입력 금지.
실제 실행: PYTHONPATH=integration_platform/consensus:integration_platform/analytics python integration_platform/analytics/c05_r1_groups.py. 6/6 PASS (1.271s): common_denominator, metadata, partitions, real_plant, reference_cohen, reference_fleiss. sklearn Cohen kappa/Jaccard, statsmodels Fleiss kappa 예제 대조 일치. GitHub readback blob과 실행 파일 일치. 실제 DB 및 통계 신뢰구간/군집 보정 미수행; 외부 라이브러리 대조는 예제 기준이지 전수 수치 검증 아님. 그룹 메타데이터는 가상 이름/연도, 실제 발전소 매핑 미검증.
## 후속
C06-R1 Django 실행 및 C02-R2/전문가 검토 연결, C03-R1/C04-R1 전체 core 통합시험, C05-R2 DB 연계; C07 Excel 복사본 설계 및 시험은 독립 진행 가능. 신규 실행 시험 16개 통과. 누적 수는 개별 단계 시험의 합이며 전체 통합 통과가 아님.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
