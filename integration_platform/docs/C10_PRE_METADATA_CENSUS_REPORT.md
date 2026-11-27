# C10-PRE — 실제 외부 AI 등록 메타데이터 전수점검 V1
2026-11-27. C07-R1 작업 복구 확인 후 진행. 원본 기준 main 8775c5ae6249cf0f8bcd70d513e3296cbb46343e, C 작업 시작 7534bc30f8c68b0c672490fb20265f68c2bb3db4. 읽기 전용 원본 확인, 통합 DB 실제 자료 적재 금지.

## 1. 수행 및 검증 범위
Gemini/Claude progress 각 38건의 활성 artifact path를 사용. 8건씩 5개 묶음(마지막 6건), 총 10개 JSON 점검 파일을 acceptance/c10_pre/에 저장. 각 INTAKE_STATUS.json 직접 조회, 고정 main의 recursive tree(잘림 없음)와 비교. 등록 모델/queue/event/status/integration 상태, approved/can_ship/eligible_for_three_ai_consensus=false, 상태파일 blob, 4개 필수 artifact 이름 및 기록 blob, role_counts 또는 reported_counts의 허용 역할 및 정수 합계 40 확인. SHA256 및 source ZIP SHA256 선언은 64자리 소문자 hex 형식 존재 확인에 한함. 개별 분석 판단이나 역할별 수치는 재저장하지 않음. 10개 점검 파일 readback, 76개 모델-queue 유일 키, 동일 source ref 및 금지 플래그 확인. 집계 C10_PRE_METADATA_CENSUS_V1.json commit e8fa934d5958682876aa15cb2c12a89412bafb52. 새 unittest는 실행하지 않았고, 이전 C07-R1 누적 257개 시험 기록 유지.

## 2. 결과
| 항목 | Gemini | Claude | 전체 |
|---|---:|---:|---:|
| 상태파일 전수 확인 | 38 | 38 | 76 |
| 개별 산출물 blob 일치 | 152 | 152 | 304 |
| SHA256 선언 형식 확인 | 152 | 148 | 300 |
| 역할 집계 합계 40 확인 | 38 | 38 | 76 |
| PENDING_INTEGRATION | 31 | 0 | 31 |
| HOLD | 7 | 38 | 45 |
| PDF 해시 검증 보고(BINARY_HASH_VERIFIED) | 37 | 0 | 37 |
| PDF 해시 확인 불가 보고 | 1 | 38 | 39 |
| 적격 승인 | 0 | 0 | 0 |

모델별 활성 판본 Gemini v1 36, v2 2 (ROOT-016, ROOT-021); Claude v1 38. 모든 상태파일의 등록 정보 및 승인 금지 플래그 점검에서 설정한 오류 조건 없음. Claude ROOT-038의 report.md/review.json/excel_import.csv/validation.md SHA256 선언 4개 없음(기록 blob 일치); source_zip_sha256 선언 형식은 76건 있음. Gemini ROOT-004 PDF 미검증 보고 상태 그대로; B05 원본 실측은 별도 기존 증거이며 현재 main 상태파일 수정/승격하지 않음. Gemini 독립성 자체 진술 38; Claude ROOT-038 사건 교육영상 노출 공개 1, 타 사건 노출 공개 37. 독립성 적합 판정이 아님. Gemini HOLD ROOT-004/014/015/017/018/019/020 유지.

## 3. 적격성 심사 준비
- Gemini 31건: 구조 등록 점검과 적격은 다름. 원본 PDF 독립 실측, 의미·사실대장·판단 근거 검토 및 독립 QA/명시적 결정 필요.
- Gemini HOLD 7건: B08 독립 QA 및 파생자료 승인/원본 링크 심사 대기. ROOT-004 DM3 근거 링크 해결 별도.
- Claude 38건: 원본 PDF 판본 검증 및 노출 관련 독립성 심사; ROOT-038 직접 노출은 새로운 독립 실행 필요 여부 판정. 타 사건 노출 진술을 모두 직접 노출로 해석하지 않음. ROOT-038 개별 파일 해시 원시 바이트 실측 우선.
- ChatGPT baseline 38건: 별도 계약으로 관리. 이 점검의 76건 외부 상태파일 모집단에는 미포함. 전체 114 제출 등록 중 실제 적격 승인 없음.

## 4. 한계 및 후속
이번에는 선언된 SHA256의 형식과 Git tree 기록 blob만 비교, 실제 304개 산출물 원시 바이트를 재해싱하지 않음. 상태파일의 JSON 일반 파서는 중복 키를 독립 검출하지 않음; 세부 schema/CSV/fact/원문 의미 검증, ZIP 원본 검증, 독립성 검토, 실제 운영 adapter 구현 미완료. 76건 상태 등록 메타데이터 일치가 실제 적격성 또는 보안 인증이 아님. 전체 운영 수용표 NO-GO 유지. C10-PRE-R1 원본 산출물 바이트 검증 및 호환성 매핑(우선 Claude ROOT-038), C09-F4 로컬 실행 결과, C07 실제 Excel 양식 확보, B08 독립 QA를 후속으로 진행. 
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
