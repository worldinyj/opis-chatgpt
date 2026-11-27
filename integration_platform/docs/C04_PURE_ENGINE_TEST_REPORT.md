# C04 — 3AI 순수 교차판정 엔진 합성시험
2026-11-27. C01 계약 blob 05e458c5172a8956e743ad5d6f76c4eccab9d4c3, rule_version 1.0. C03-R1 전체 DB 연동 검증을 대체하지 않는 별도 모듈.
## 실행 및 검증
python integration_platform/consensus/c04_consensus.py
로컬 실제 실행: 14/14 unittest PASS (0.108s). 실행 파일 Git blob f3dabfdfc3076593130a99e81d50eb6876182e59, SHA256 af2b829b33ac6b6cb4c018cde2dd2e4f8a30e5ec7c1cbc6795903090e7e92b0d. GitHub readback blob 일치.
- 6역할의 순서 있는 216개 조합 전수: D/I 선정, A 응답하되 선정 아님, H/P/N 미선정.
- 4 availability 상태의 64개 조합 전수: 세 모델 모두 ELIGIBLE이어야 집계 가능. 그 외 PENDING_INPUT, selected_count=NULL; responded_count는 적격 응답만 계산. deferred_count는 적격 A 수.
- 세 모델 모두 선정이면 INTERNAL_CONSENSUS_SELECTED (내부 합의 후보), 0~2개 선정이면 EXPERT_REVIEW_REQUIRED. 0표 자동 미선정 금지.
- 중복 모델, 누락 슬롯, 역할-결과 불일치, HOLD 표 입력, 적격 provenance 누락, 실제 ROOT 키, STORED 상태, 불완전 전체 grid를 차단. 입력 순서 독립 결과와 digest 및 역할 변경 감지 시험.
- 38x40x3 합성 전체 규모: 1520 keys / 4560 slots; 520 내부 합의 후보, 520 전문가 검토, 480 입력 대기. 이는 인위적 fixture 분포로 실제 분석 통계가 아니다.
## 남은 범위
현재 pure engine은 synthetic key와 fixture 참조만 허용한다. 호출자가 제공한 availability/참조의 실제 DB 적격성을 확인하지 않는다. C04-R1에서 봉인 snapshot의 정확한 fingerprint/입력 버전/slot linkage 검증, C02-R2 SQL에서 세 모델의 immutable eligibility 및 pending_trace 조회, 원본 판단 보존, 계산 결과 atomic append-only 저장 및 idempotence, snapshot 변경 시 재검토 표시를 구현·시험한다. C03-R1 full-core bridge 검증 및 ChatGPT 기준선 적재 연결은 미완료이며 C04로 우회하지 않는다. 216+64는 두 별도 전수 집합으로 모든 role/availability 교차곱 전수시험을 주장하지 않는다. 전문가 최종판정, 실제 모델 비교, 통계, 배포 미수행.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
