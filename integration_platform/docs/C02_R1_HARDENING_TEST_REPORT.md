# C02-R1 — 합성 DB 무결성 보강 / 실행 기록
2026-11-27. 기존 C02 파일은 수정하지 않고 db/c02_r1.py에서 보강. SQLite 3.46.1, in-memory only.
실행: python integration_platform/db/c02_r1.py
Git blob ce6055155f16fc261ed27276f0c8fbfefcdcb7de (실행 파일과 GitHub 재조회 일치).
기존 C02 20/20 PASS; R1 19/19 PASS; 총 39/39.
R1 시험: direct sealed insert, invalid artifact hash, failed validation, positive eligibility, late check, parent mutation, late fact, wrong model, hold cannot vote, mixed revision, fingerprint mismatch, unsealed consensus, stale eligibility, sealed positive path, digest exact, master append after seal, expert wrong chain, foreign key check, integrity check.
R1 합성 양성 경로는 1사건×40속성×3모델 및 한 개의 개정판, C02 회귀는 38×40×3 MISSING 슬롯. 실제 데이터나 실제 전문가 판정은 전혀 적재하지 않았다.

## 보강 범위
원본·부모·판정 행의 변경 차단, 적격 판단 후 신규 근거/검증 행 차단, 필수 검증 체크 및 선정 근거 존재 조건, 최신 적격결정 기준 및 모델별 단일 개정판, 스냅샷 직접 봉인 차단·SHA256 fingerprint(현재 version + slot ID/상태), 전문가 revision chain 기본 검증.

## 잔여 제한 / C02-R2 게이트
- 실제 적격 심사를 대체하지 않는다. source_revision의 VERIFIED CHECK는 SQL NULL 삼치논리 때문에 observed hash/pages NULL 우회 가능성을 추가 차단하고 시험해야 한다. source 배열 및 section의 JSON 타입·양수 페이지·fact source 존재와 범위, 필수 artifact provenance 완결성 검증 필요.
- 현재 HOLD 슬롯에 제출/판정 참조가 없으므로 별도 provenance 테이블이나 제약 확장이 필요하다. 현재 fingerprint는 내부 ID와 슬롯 상태만 포함한다. 실제 고정 Git ref, 표준, 제출 및 근거 hash까지 포함하는 portable digest 필요.
- 현재 마스터 삽입 동결은 전체 DB에 적용되는 보수적 합성 시제품 정책. 이후 새 표준/사건의 명시적 버전 관리 및 스냅샷별 마스터 freeze 설계 필요. eligibility append-only 순서 및 동시 쓰기·이전 결정의 효력 시점 추가 검증.
- 38×40×3 R1 양성·혼합 상태 부하 시험, null/누락 검증, rollback, source 페이지/출처 자료, HOLD trace, revision chain 추가 시험 필요. C04 consensus 계산과 C06 권한/승인은 아직 구현하지 않았다.
- 운영 migration, 실제 자료 적재, 배포, Django 연결 미수행. C02 전체 수용 완료로 승격하지 않음. C02-R2 보강 후 C03 적재기 개발. approved=false, can_ship=false, main_merge=false.
