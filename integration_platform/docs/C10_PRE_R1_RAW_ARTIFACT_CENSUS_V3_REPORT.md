# C10-PRE-R1 — 외부 AI 산출물 원시 바이트 전수검증 완료 V3
2026-11-27. 원본 고정 main 8775c5ae6249cf0f8bcd70d513e3296cbb46343e, 등록 메타데이터 census 65f0a7d2ca937593854f9dced404401bc579b23d. 작업 시작 C c91a880943baf051d13a1ab7ec6d51aa0fa347aa. 실제 분석자료 적재/판정/승인 금지.

## 1. 수행 범위 및 방법
이전 22개 제출/88개 산출물 기록 유지. 남은 54개 제출(27사건의 Gemini/Claude 양 모델), 216개 산출물과 54개 상태파일 원시 바이트를 신규 실측. Git 직접 clone은 DNS 실패로 사용할 수 없어 GitHub 연결에서 고정 ref의 파일을 base64 조회, 원시 바이트 복원, Git blob SHA1 및 SHA256 재계산. 각 배치 SHA256 abc/빈 Git blob 테스트 벡터 검증. 상태파일 blob은 기존 census 고정값 대조, model/queue/event 및 승인 금지 플래그 대조. 산출물은 기존 tree blob 및 상태파일 선언 SHA256과 비교. 파일 본문 재저장하지 않고 해시/크기/식별정보만 저장. 실제 조회의 상태파일 JSON은 일반 파서로 읽었으므로 중복키/전체 스키마 독립 검증을 완료했다고 주장하지 않는다.

## 2. 결과
| 검증항목 | 이전 | 신규 | 누적 |
|---|---:|---:|---:|
| 제출자료 | 22 | 54 | 76 |
| 상태파일 원시 바이트 | 22 | 54 | 76 |
| 산출물 blob 일치 | 88 | 216 | 304 |
| 선언 SHA256 일치 | 84 | 216 | 300 |
| 미선언 SHA256 신규 실측 | 4 | 0 | 4 |
| SHA256 불일치 | 0 | 0 | 0 |
| 남은 제출 | 54 | -54 | 0 |

총 38개 사건 양 모델의 유일 모델-queue 76개, 모델 간 사건 ID 일치, 사건 ID 38개 유일성 확인. 산출물 바이트 누적 7,726,163; 상태파일 바이트 누적 230,687. 파일럿/기존 확대 검증 22건은 이번 중복 재해싱하지 않음. 신규 19개 raw 기록 저장 및 readback A(30제출/120산출물)/B(24제출/96산출물)에서 승인 금지/고정 ref/유일 키/4종 산출물/실측과 선언 hash 일치를 확인. 기존 V2의 11개 기록과 신규 19개 기록의 30개 path/blob을 고정 개발 tree와 대조, 누락/추가 raw 기록 없음. 집계 acceptance/C10_PRE_R1_RAW_ARTIFACT_CENSUS_V3.json commit 077df41d53f1ddf370809c1b7f4c878a9c045c5e. 76건 전체 상태파일/304개 산출물 원시 바이트 검증 완료(3회 누적); local git cat-file runner 전체 실행은 미수행. 신규 코드 및 unittest 없음, 누적 이전 시험 268 유지.

## 3. 예외 및 운영 제한
Claude ROOT-038 4개 산출물은 SHA256 선언 없이 신규 실측(기존 기록 그대로), Git blob 일치. 상태 RAW_BYTES_MATCH_WITH_DECLARATION_GAPS. 원본 ZIP 바이트/PDF 판본과 독립성/의미 타당성은 이번 범위 아님. Gemini HOLD7은 여전히 HOLD, PENDING_INTEGRATION31. Claude38 HOLD. ChatGPT 기준선38은 이 외부 AI 76건 전수검증 대상 아님. 실제 적격 승인 0, 실제 DB 적재 없음. 원시 바이트 동일성은 원인분석 정확성 또는 독립 QA 승인 아님. 304개 hash 일치/실측의 검증기록을 바탕으로 원본 파일 연결성 확보. C10-PRE-R2에서 114개 제출의 적격성 심사 자료 구성 및 승인 차단 사유를 정리할 것. 실제 C09-F4 로컬 실행, Django, Excel 실제 양식, B08 독립 QA, PDF/ZIP 원본 증거 및 운영 적격성 구현은 별도 잔여. 기존 수용표 3 scoped PASS/9 BLOCKED 유지.
approved=false / can_ship=false / main_merge=false / actual_data_import=false / acceptance_go=false.
