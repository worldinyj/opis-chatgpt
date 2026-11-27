# C04-R1 및 C05 — 스냅샷 연결 및 일치도 분석 합성시험
2026-11-27. C01 계약 1.0 기준. 실제 입력, 승인, merge 없음.
## C04-R1
consensus/c04_r1_bridge.py (blob d3cad0c57b9e62b047e45105fd8e191b5c045ee7), test_c04_r1_bridge.py (bd1b40619d73a12ec58d1119ea35e77118c27cd9).
봉인 및 fingerprint 재계산 확인, FK 활성 여부 확인, 사건별 40속성/3모델 grid, 제출·적격결정·pending_trace 연결, 모델별 개정판/상태 일관성 검사. C04 순수 엔진 호출; consensus.reason에 스냅샷 fingerprint와 판정 JSON 및 result_sha256을 보존. 동일 결과 재실행 NOOP, 기존 불완전/상이 결과 거부, 전체 저장과 audit 원자적 트랜잭션.
실제 실행: python integration_platform/consensus/test_c04_r1_bridge.py
9/9 PASS (0.136s): bad_link, digest, mixed, noop, partial, pending_trace, positive, rollback, unsealed. 3 사건/120 키/360 슬롯에서 40 내부 합의 후보, 40 전문가 검토, 40 입력 대기. 합성 결과.
제약: C02-R2 실제 전체 모듈/트리거가 아닌 해당 테이블 열 구조를 재현한 in-memory compatibility harness, 별도 fixture digest 함수. 따라서 전체 core 수용시험 아님. production DB 권한 경계 및 직접 SQL 삽입 방지는 별도. result 참조에 로컬 ID 포함, DB 간 이식 재현성 미검증. 이전 스냅샷 전문가 검토의 stale 표시, 38사건 bridge E2E, 실제 C02-R2 digest 및 trigger 통합시험 잔여. C03-R1 core 및 baseline bridge도 미완료.
## C05
analytics/c05_agreement.py (blob 9f5a0247476c6dc57ded332d8951d32f043bd5aa).
실행: PYTHONPATH=integration_platform/consensus python integration_platform/analytics/c05_agreement.py
9/9 PASS (0.298s): all_missing, all_negative, deferred_separate, full_grid, grid_missing, negative_kappa, partial, perfect_balanced, real_key.
- 모델별 적격/보류/미확보/불완전 상태 및 적격 3범주 응답 집계.
- 두 모델이 동시에 적격인 키에서 pairwise confusion matrix, 관측 일치율, Cohen kappa, 선정 Jaccard; 세 모델이 모두 적격인 키에서 만장일치율, 평균 쌍별 일치율, Fleiss kappa.
- 선정/판단보류/미선정 3범주와 선정/비선정 응답 이진 통계 별도. 이진에서는 적격 A를 비선정 응답으로 분류하되 실제 미선정 판단과 구별한다. 비적격 상태는 분모 제외, 제외 수와 coverage 표시. 분모 0 또는 기대 일치율 1은 None, 빈 선정 합집합 Jaccard=None. 음의 kappa 보존.
- 38사건/1520키/4560슬롯, 760 완전 키와 760 입력 대기 키의 인위적 fixture 시험. 실제 분석 통계 아님.
제약: 전체 집계 순수 함수만 구현. 원칙/속성/발전소/연도별 집계, 스냅샷 DB 연계, 통계 신뢰구간/사건내 군집 고려, 외부 라이브러리 교차검증, 전문가 최종판정 기반 성능 평가 미실행. pairwise 비교의 분모가 서로 다를 수 있어 직접 비교 주의. C05-R1에서 공통 완전사례/그룹 집계와 DB 기반 재현성 검증을 진행한다.
## 저장 확인
3개 실행 파일 Git blob이 GitHub 재조회 값과 일치. 신규 18개 unittest PASS. 기존 단계와 합산한 수는 서로 다른 시험 항목의 누적이며 통합 재실행을 뜻하지 않는다.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
