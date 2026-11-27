# C10-PRE-R1 — 우선순위 사건 양 모델 원시 바이트 검증 확대 V2
2026-11-27. 원본 고정 main 8775c5ae6249cf0f8bcd70d513e3296cbb46343e, 등록 메타데이터 census 65f0a7d2ca937593854f9dced404401bc579b23d, 작업 시작 C 1bc728aacb78cf102dd2bee30b15762727867665. 실제 자료 적재/판정/승인 금지.

## 1. 이번 실행
로컬 Git ls-remote 재시도 실패(DNS github.com). 기존 GitHub 연결을 통한 고정 ref base64 원시 바이트 재계산 방식 유지. abc SHA1/SHA256 및 빈 Git blob 테스트 벡터 확인. 파일별 Git blob SHA1(헤더 포함), SHA256 실측 및 등록 blob/선언 해시 비교. 상태파일도 원시 바이트 blob 및 SHA256 실측. 기존 6건에 더해 16개 제출·64개 산출물 실측, 신규 모두 blob 및 선언 SHA256 일치. 신규 8개 기록 파일 저장. 기존 3개 기록과 함께 11개 점검 JSON readback, 동일 ref/금지 플래그/22개 유일 모델-queue 및 88개 산출물 집계. 기존 6건은 이번 재해싱하지 않음. 등록 상태파일은 일반 JSON 파서 사용, 중복키 독립 검증은 이번 connector 점검 범위 아님.

## 2. 범위 및 집계
Gemini HOLD 7건(ROOT-004/014/015/017/018/019/020) 원본 자료와 대응 Claude 7건의 56개 산출물 전부 검증 완료. 일반 비교 ROOT-005/038, Gemini 활성 v2 ROOT-016/021의 대응 Claude v1도 검증. 총 11개 사건에서 양 모델 검증 완료.
| 구분 | 이전 | 신규 | 누적 |
|---|---:|---:|---:|
| 제출 | 6 | 16 | 22 |
| 산출물 blob 일치 | 24 | 64 | 88 |
| 선언 SHA256 일치 | 20 | 64 | 84 |
| 선언 없음 신규 실측 | 4 | 0 | 4 |
| SHA256 불일치 | 0 | 0 | 0 |
전체 76제출/304산출물 중 22/88 검증(28.95%). 남은 54개 제출/216개 산출물, 27개 사건의 양 모델. 실측 산출물 bytes 누적 2,326,412 및 상태파일 bytes 68,916. 신규 시험 코드/실행 없음; 이전 누적 unittest 268 그대로.
집계 및 잔여 queue: acceptance/C10_PRE_R1_RAW_ARTIFACT_COVERAGE_V2.json (commit 593035d94462857ecca949e59d00c101e56bf85c). 기존 파일럿 기록은 그대로 보존.

## 3. 제한과 후속
이번에는 우선순위 사건 양 모델의 완전한 페어를 구성하도록 작업 범위를 선택. 전체 70개 잔여 제출을 모두 처리하지 못함; 직접 clone DNS 제한으로 연결 도구의 건별 제한을 적용. 남은 54건은 이어서 검증하거나 기존 c10_raw_audit.py를 전체 Git checkout에서 실행. SHA256 신규 실측 4개는 Claude ROOT-038의 기존 선언 부재이며 원본 상태 파일에 소급 기록하지 않음. B08 HOLD 품질검토를 대체하지 않음. 실제 PDF/ZIP 원본 bytes, 독립성, 의미적 판단 및 근거, 운영 환경, 실제 Excel 원본은 여전히 미검증 또는 별도 검증 필요. 해시 일치가 적격 승인 아님. Gemini HOLD7/통합대기31, Claude HOLD38 유지. 실제 적격 0. C10-PRE-R1 전체 원시 바이트 검증 진행 중, 운영 NO-GO.
approved=false / can_ship=false / main_merge=false / actual_data_import=false / acceptance_go=false.
