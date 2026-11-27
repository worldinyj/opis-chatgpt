# C09-A/B 및 C09-R1 — 실제 핵심 DB 연결과 무결성 시험
2026-11-27. 기준 integration branch edfab9518ed4aa3f1d0dffbe7cb03556f1158312; 실제 AI 자료 사용 금지.

## 재현 환경
직접 Git clone DNS 실패. 로컬에 남은 C04~C08 Python 실행 파일 10개의 Git blob을 기존 등록값과 확인. C02, C02-R1, C02-R2의 GitHub 원본에서 def selftest(): 앞의 전체 실행 코드(DDL, connect, digest, location_ok 등)를 로컬 복원하고 원본과 prefix SHA256 대조. 기존 selftest 함수는 복원/재실행하지 않았으므로 전체 파일 재현 또는 기존 61시험 재실행으로 계산하지 않는다.
| 모듈 | 원본 blob | 실행 prefix SHA256 |
|---|---|---|
| c02_sqlite.py | 6aa9704e607a5e1b53f7715a670931514feb3e53 | f60182e47816071bdddf0401a748f7f48f623eacf0943366b20c917cf8510bb0 |
| c02_r1.py | ce6055155f16fc261ed27276f0c8fbfefcdcb7de | 76afe41deb411945bc82824239005013ee1927736594e137df26b5876a602a83 |
| c02_r2.py | f5e1b969fc4a33e170d753c60bce2ae12dace633 | b29f023523b1caa77ee8c44fa09773081478306a331b624e0f47952247b5657b |
세 prefix 모두 정확히 일치. C04-R1 bridge 실제 blob d3cad0c57b9e62b047e45105fd8e191b5c045ee7. C05-R1 f1823fc80224979089775316b63d98a985f7e716, C08 90ebc352165c13df209fbf08bdac2911366dec95.

## C09-A/B 결과
tests/c09_core_e2e.py blob 3e403df9481196204fc246618202e323d566891d. 실제 C02-R2 DDL/trigger + C04-R1 + C05-R1 + C08. 합성 레코드를 DB 직접 주입(실제 importer 제외). 38 사건, 10 원칙, 40 속성, 4560 slots, 봉인 및 저장 1520 consensus, 520 내부합의 후보/520 전문가 검토/480 입력 대기(selected_count NULL). ELIGIBLE/HOLD/MISSING/INCOMPLETE 네 상태 존재. 저장 reason JSON에서 votes 재구성하여 1040 완전사례 통계 및 HTML 생성.
9/9 unittest PASS, 1.554초: analytics_dashboard, atomic_rollback, backup_restore, full_core, immutable, integrity, noop, portable_snapshot_digest, writer_lock. 파일 백업 후 연결별 FK/recursive trigger 및 UDF 재등록, fingerprint/전체 consensus row 동일, FK/SQLite integrity check, 두 파일 연결의 BEGIN IMMEDIATE 잠금 및 재시도 확인. 별도 3사건 DB surrogate ID offset 변경시 snapshot digest 동일(결과 digest의 로컬 ID 의존은 잔여).
실행: PYTHONPATH=integration_platform/db:integration_platform/consensus:integration_platform/analytics:integration_platform/dashboard python integration_platform/tests/c09_core_e2e.py

## 확인된 결함 및 보완 C09-R1
기존 C02-R2에서 직접 SQL로 입력 대기 키에 잘못된 3표 INTERNAL_CONSENSUS_SELECTED 삽입, 해당 키 expert draft 삽입 각각 성공하는 결함을 실제 재현. C04-R1/C06 서비스의 검증만으로 DB 직접 삽입을 막지 못함. 기존 파일 보존, db/c09_guard.py (blob 3b7383d3dbc10dba7724f8df3a3fbbb219f11a01) 선택적 보완 모듈 추가. 신규 결과 저장소에서만 install; 저장 consensus status/count/판정 JSON의 canonical 값 재계산과 일치 검사, expert draft는 완전한 판정 존재 및 이유/fixture actor 제한, 복원 연결에서 UDF 미등록시 consensus INSERT 차단. 기존 result store 자동 인증 금지. test_c09_guard.py blob c25dce5bbe45067b83cf97189009cdf100bd2127.
7/7 unittest PASS, 0.375초: existing_store_rejected, expert_draft, expert_pending, forged_reason, invalid_consensus, positive_and_noop, restore_fail_closed. 추가 수동 실행 38사건/4560슬롯/1520결과, guard 설치 후 정상 저장 및 NOOP, 1040 완전사례, HTML 생성 PASS; fingerprint 2f9024e470b0ea256b16dbe9653ffab2caca81142a1c4d23aef43493632b6738. 신규 unittest 16개 + 전체 규모 보완 재실행 1회(별도, 누적 unittest에 미포함). 새 소스 3개 로컬 실행 Git blob과 GitHub readback 모두 일치.
실행: 동일 PYTHONPATH python integration_platform/tests/test_c09_guard.py

## 남은 수용조건
C04-R1 full core bridge 실제 시험 완료(합성). C03-R1 실제 core 및 baseline bridge 미완료; C09는 직접 SQL fixture라 ZIP→staging→실 DB E2E 미완료. C05/C08 DB 결과 사용 합성 통합시험 완료; 운영용 DB 연결/조회 API, 신뢰할 수 있는 source metadata, 재계산 후 analytics_input 호출 정책, 웹 권한 및 실시간 화면 미구현. C06 Django 미설치; 전문가 서비스는 별도 DB이며 이번 guard의 SQL draft 시험이 Django/C06 통합은 아님. C07 실제 양식 미확보, 전체 파일 시험 미완료. Guard는 명시 설치 및 UDF 재등록 필요; DB 관리자/임의 SQL/트리거 제거·UDF 재정의/PRAGMA 변경 공격에 대한 보안 경계 아님. 앱 연결 기본 정책·권한·감사 원자성·DB 마이그레이션 필요. 두 연결 잠금 시험은 동시성 제한된 사례, WAL/운영 부하·실제 복구 훈련 미실행. 전체 시스템 수용 PASS로 기록하지 않는다. B08 독립 QA 대기, C10 실제 적재 금지.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
