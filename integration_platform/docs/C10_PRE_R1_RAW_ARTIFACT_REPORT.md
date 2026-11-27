# C10-PRE-R1 — 원시 바이트 무결성 우선검증 및 일괄 실행기
2026-11-27. 원본 고정 main 8775c5ae6249cf0f8bcd70d513e3296cbb46343e, C10-PRE 전수점검 기준 65f0a7d2ca937593854f9dced404401bc579b23d. 실제 분석자료 DB 적재/적격 결정/원본 수정 금지.

## 1. 이번 실제 검증 범위
우선 선정한 6개 제출(Claude ROOT-038: 개별 SHA256 선언 누락, ROOT-005: 비교 대상; Gemini ROOT-038: 일반 통합대기, ROOT-004: HOLD, ROOT-016/021: 활성 v2)에서 상태파일과 네 필수 산출물의 원시 바이트를 고정 commit으로 조회. GitHub base64 응답을 디코딩하고 Git blob SHA1 (blob header 포함) 및 SHA256을 재계산. abc SHA1/SHA256 및 빈 Git blob 테스트 벡터 확인. 이전 전수점검의 고정 blob과 실제 해시 비교. 상태파일 6개도 원시 바이트의 blob 일치 및 SHA256 실측. 파일 본문 재저장하지 않고 해시/크기/식별정보만 기록. 상태파일 일반 JSON parser를 사용한 실제 connector 파일럿이므로 duplicate JSON key에 대한 독립 검증 완료로 주장하지 않음.
- 6/76 제출, 24/304 개별 산출물; blob 24/24 일치; 기존 SHA256 선언 20/20 일치; 미선언 4개 신규 실측; SHA256 불일치 0. 산출물 838,364 bytes, 상태파일 16,312 bytes. 70제출/280산출물은 이번 원시 바이트 검증 미수행.
- ROOT-038 Claude 신규 관측 SHA256: report.md 695432a6da1294682ed4ee2ca3bbe20c5e2440d57f42060011afd17feb022987; review.json 883c038093a84860eafb6e0b2416ac2f296e85528fd79242848fe6420740808e; excel_import.csv 28ff718c8f8e602b1b36dec17c1c7c24ce488d86c1fc1093fa916a68139fc1a7; validation.md 89cae8659ee36f889af21bf312e39b81556dcc050c1c0d8d9fc008e04757c2e4. 모두 과거 blob과 일치하나 원본 SHA256 미선언이므로 NEW_MEASUREMENT_NO_DECLARATION. 기존 상태파일을 수정하거나 과거 ZIP 원본의 SHA256과 동일하다고 주장하지 않는다.
- 3개 파일럿 기록 readback 및 6개 모델-queue 유일 키/24개 산출물/고정 ref와 승인 금지 플래그 대조. 집계 acceptance/C10_PRE_R1_RAW_ARTIFACT_PILOT_SUMMARY_V1.json (commit 206916c50b28b615f96509c2821628b370cf4fef). B 단계에서 기존에 수행된 해시 비교는 이번 실측 집계에 가산하지 않음.

## 2. 일괄 검증기
acceptance/c10_raw_audit.py blob 9c220fad738b05f233a69a7d7b9c0f31f8a3b084. Python 표준 라이브러리와 Git만 사용. C10-PRE 집계/10개 shard를 고정 commit 및 blob에서 readback, 76개 모델-queue 그리드, 38 사건 고유 ID 및 모델 간 매핑 확인, status와 산출물 고정 tree path/regular blob/size limit 8MiB, cat-file 원시 바이트 SHA1/SHA256 계산. Git replace objects 비활성화 및 literal pathspec. JSON duplicate keys와 nonfinite number 거부. LFS pointer 거부. 3개 결과 상태 MATCH / NEW_MEASUREMENT_NO_DECLARATION / MISMATCH. 76개 전체 및 304개 blob/해시 상태를 충족하지 못하면 INCOMPLETE_OR_MISMATCH와 비정상 종료. 원본 repo 밖 신규 JSON 파일만 기록; 실제 자료 적재/승인 없음. 이미 존재하는 파일 덮어쓰지 않음.
acceptance/test_c10_raw_audit.py blob d39a467b4d9346141e826e2543b10c8b7e8b1f90. 실제 임시 Git 저장소 합성 파일 시험 11/11 PASS(최종 0.451초): binary/CRLF/UTF8 원시 bytes, worktree 수정 무시, missing SHA256, mismatch, pinned blob, approval flag, scope/path, duplicate JSON, partial 및 duplicate summary, full summary status. Full summary는 합성 record projection으로 시험, 실제 76개 git objects 실행 아님. 로컬 실행 파일과 저장소 blob 2/2 일치. 불완전 checkout CLI에서 0 검증 및 INCOMPLETE_OR_MISMATCH/exit 1/report.json 생성 확인. 실제 고정 source/census commit 전체 clone이 없어 load_census의 실제 10개 shard/76개 원본 full execution은 미수행. 신규 unittest 11개, 누적 보고 257→268; 이전 시험 재실행하지 않음.

## 3. 로컬 전체 재현
개발 branch 최신본과 main의 고정 commit을 포함한 전체 Git history가 있는 checkout에서 실행. 기존 C09-F4 실행환경을 이용할 수 있으며 별도 package 필요 없음. Windows PowerShell (repo root):
```powershell
git fetch origin main develop/integration-platform
# 새 검증용 clone 또는 변경사항 없는 develop/integration-platform 최신 checkout 사용
py -3.12 integration_platform/acceptance/test_c10_raw_audit.py
py -3.12 integration_platform/acceptance/c10_raw_audit.py --repo . --report "$HOME\opis-c10-raw-audit-001.json"
```
Mac/Linux는 python3.12, report 경로 "$HOME/opis-c10-raw-audit-001.json". 이전 결과 덮어쓰지 않도록 매번 새 경로. 전체 수행 결과 JSON에 SHA256 선언 누락이 있으면 RAW_BYTES_MATCH_WITH_DECLARATION_GAPS로 별도 기록. 어떤 결과도 적격 승인 아님. 보고서에 원본 본문/비밀키는 넣지 않음.

## 4. 다음 단계 및 차단
전체 76건 원시 바이트 일괄검증 결과 확보 후 C10-PRE-R2 적격성 심사 자료 구성. 실제 PDF hash/pages 독립 확인, source ZIP bytes 검증, schema/CSV/사실대장/의미 검토, 독립성 판단, B08 별도 독립 QA 및 명시적 승인, 실제 sidecar 운영 adapter, 실제 Django 및 Excel 양식 검증은 여전히 미완료. 원본 Git blob의 일치와 안전문화 분석 타당성은 별개. 현재 31 Gemini PENDING_INTEGRATION, Gemini 7 HOLD, Claude 38 HOLD, 실제 적격 0. 
approved=false / can_ship=false / main_merge=false / actual_data_import=false / acceptance_go=false.
