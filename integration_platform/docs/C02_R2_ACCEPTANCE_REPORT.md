# C02-R2 — 판본·근거·보류 추적 및 전체 규모 합성시험

2026-11-27. 기존 C02 및 R1 파일을 보존하고 db/c02_r2.py 보강 모듈을 추가했다.
실행: python integration_platform/db/c02_r2.py
SQLite 3.46.1, in-memory, synthetic only. 실행 파일 Git blob f5e1b969fc4a33e170d753c60bce2ae12dace633과 GitHub 재조회 일치.

## 실행 결과
C02 20/20, R1 19/19, R2 22/22, 총 61/61 PASS.
R2: NULL observed hash, NULL observed page, missing original artifact, invalid JSON location, physical page out of range, duplicate physical pages, empty location, missing fact source, 4560 slots, missing pending trace, wrong pending model, provenance changes digest, full grid seal, eligible 3040, hold 1440, missing and incomplete 40 each, sealed pending delete, sealed incomplete append, replace parent, digest stable, foreign key integrity, SQLite integrity.

합성 38개 사건 × 40개 속성 × 3모델 슬롯 4560개:
ELIGIBLE 3040 / HOLD 1440 / MISSING 40 / INCOMPLETE 40.
실제 사건·원본 보고서·AI 분석결과·전문가 승인 적재 없음. 이 분포는 fixture 값이며 프로젝트 실제 통계가 아님.

## 보강 기능
- VERIFIED 원본의 양쪽 SHA256 및 정수 물리쪽수 완전 일치 요구; NULL 우회 차단.
- 출처 위치 JSON 배열, 양수·중복·물리쪽 범위 및 빈 위치 검증. 사실의 위치 존재 확인. 적격 제출의 원본 artifact 최소 1개 및 파생 부모 링크 필요.
- HOLD/INCOMPLETE의 별도 pending_trace와 제출·개정판·모델·판정 연결. MISSING과 구별. 봉인 전 슬롯 균질성 및 최신 판정 점검. 봉인 후 trace 및 불완전 제출 근거 변경 차단.
- 사건/속성 정의, 제출 개정판, 원본 및 파생 artifact hash, 사실·검토·판정 이력을 포함하는 자연키 기반 SHA256 지문. surrogate ID에 직접 의존하지 않음.
- recursive_triggers 활성화로 REPLACE에 의한 부모행 변경 방지.

## 범위 및 후속 게이트
C02 계열 핵심 합성 수용시험 완료; C03 데이터 적재기 개발로 전환한다.
현재 스키마는 합성 전용이며 실제 입력의 필수 artifact 종류별 완전성, 모델별 입력 계약, Git blob/원본 PDF 해시의 실측 검증, 사실-속성 근거의 의미 일치·출처 위치 대조는 C03 및 전문가 게이트에서 검증한다. SQL 등록 값 자체를 원본 검증 증거로 간주하지 않는다.
자연키 지문의 동일 내용/상이한 DB ID 간 재현성 별도 시험, 새 표준·사건 버전 관리, 운영 DB 동시성·권한·백업, migration은 C09/후속 운영 전 검증 대상으로 유지. INCOMPLETE 상태의 미결 검증 이력 전체를 fingerprint에 포함하지 않으므로 C03에서 별도 provenance 계약 필요. 실제 판정 로직은 C04, 전문가는 C06. Django 배포와 실제 분석자료 사용은 미승인.
approved=false / can_ship=false / main_merge=false.
