# OPIS 독립 안전문화 분석 검증 기록 (validation.md)

## 1. 사건 및 모델 정보
- **QUEUE_ID**: `ROOT-003`
- **EVENT_ID**: `240513W4`
- **EVENT_NAME**: 월성4호기 계획예방정비 중 등급3전원 모선 저전압에 의한 자동순차접속신호 미발생
- **ANALYZER**: `GEMINI`
- **실제 사용한 모델 버전**: 미확인 (`review.json` 내 `model.version: null` 기록)
- **REVISION**: `v1`
- **분석 수행일**: `2026-11-26`
- **적용 기준**: `workflow_version=1.1`, `prompt_version=1.0`, `standard_version=1.0`, `schema_version=1.0`
- **문서 상태**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 원본 PDF 판본 및 해시 검증
- **원본 PDF 파일명**: `2024-06-01_월성4호기_계획예방정비_중_등급3전원_모선_저전압에_의한_자동순차접ᄉ.pdf`
- **원본 보고서 번호 / 발행일**: `2024-7호(240513W4)` / `2024-08-19`
- **원본 PDF 페이지 수**: `77`쪽 (큐 기대값 `77`쪽과 일치)
- **원본 PDF 파일 크기**: `1,924,381` bytes (큐 기대값 `1,924,381` bytes와 일치)
- **원본 PDF SHA-256**: `697459378f08da7fde030ed8521f9e95e31698704b12ce39b2e593cf6591b7a0` (큐 기대값과 100% 일치)
- **실제 확인 방법**: Google Drive에서 다운로드한 원본 PDF 바이너리에 대해 Python `hashlib.sha256`으로 해시를 직접 계산(`BINARY_HASH_VERIFIED`)하고 `pypdf`/`pdfplumber`로 본문 전수·붙임 12·비공개 처리 사유서(40개소)를 판독함.

## 3. 40속성 역할별 집계
| 구분 | 역할 | 개수 | 해당 속성 코드 |
| :--- | :---: | :---: | :--- |
| 선정 | `D` | 14 | `PA1`, `QA4`, `CO1`, `CO3`, `LA6`, `DM1`, `DM2`, `CL4`, `PI1`, `PI2`, `WP1`, `WP2`, `WP3`, `WP4` |
| 선정 | `I` | 5 | `PA2`, `PA3`, `QA1`, `LA4`, `LA5` |
| 판단보류 | `A` | 4 | `QA2`, `LA3`, `LA8`, `RC1` |
| 미선정 | `H` | 3 | `QA3`, `LA7`, `CL2` |
| 미선정 | `P` | 1 | `PI3` |
| 미선정 | `N` | 13 | `CO2`, `CO4`, `LA1`, `LA2`, `DM3`, `WE1`, `WE2`, `WE3`, `WE4`, `CL1`, `CL3`, `PI4`, `RC2` |
| **합계** | **전체** | **40** | **선정 19개 / 판단보류 4개 / 미선정 17개** |

## 4. 15개 품질검증 항목 결과
| 번호 | 검증 항목 | 결과 | 세부 확인 내용 |
| :---: | :--- | :---: | :--- |
| 1 | 원본 사건 ID 일치 | PASS | `240513W4` (`2024-7호(240513W4)`) 일치 |
| 2 | 원본 판본 정보 확인 | PASS | 파일 크기 1,924,381 bytes, 77쪽, SHA-256 큐 기대값 100% 일치 (`BINARY_HASH_VERIFIED`) |
| 3 | 40속성 누락 검사 | PASS | 40/40 속성 존재, 누락 0건 |
| 4 | 40속성 중복 검사 | PASS | 유일 코드 40건, 유일 `review_key` 40건, 중복 0건 |
| 5 | 표준 코드 및 명칭 일치 | PASS | `standards/safety_culture_40.json`과 40개 코드·표준 명칭 100% 일치 |
| 6 | D/I/A/H/P/N 집계 일치 | PASS | D:14, I:5, A:4, H:3, P:1, N:13 (합계 40) 전 파일 일치 |
| 7 | 선정 결과와 역할 매핑 일치 | PASS | D/I→선정(19), A→판단보류(4), H/P/N→미선정(17) 100% 일치 |
| 8 | D/I 선정 근거 존재 | PASS | 선정 19개 속성 모두 1건 이상의 `fact_ids` 및 `source_refs` 보유 |
| 9 | 사실 ID 참조 유효성 | PASS | `GEMINI-F01`~`GEMINI-F14` 외 미등록 참조 0건 |
| 10 | 원문 페이지 범위 확인 | PASS | 모든 `pdf_pages` 1~77쪽, `printed_pages` 1~75쪽 범위 내 |
| 11 | JSON 스키마 검증 | PASS | Python `jsonschema` (`independent_ai_review_v1.schema.json`) 통과 |
| 12 | `report.md`와 `review.json` 일치 | PASS | 6장 구성 및 40속성 요약표 코드·명칭·역할·검토결과 100% 일치 |
| 13 | `review.json`과 CSV 일치 | PASS | UTF-8, 정확히 40행, 헤더·검토키·결과·사유 100% 일치 |
| 14 | CSV 수식 주입 위험 검사 | PASS | `=`, `+`, `-`, `@` 시작 셀 0건 |
| 15 | 독립성 및 미승인 상태 확인 | PASS | `other_ai_outputs_seen: false`, `INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false` |

- **산출물 3종 SHA-256**:
  - `report.md`: `dd6b2ef45cd8349e3346cbaf5307995434c69024d3df06b4e3d020472c40d5f7`
  - `review.json`: `01adf7dba150b9cb807b9ef5e985bbf079118701957a4357f1b78f0fa5adcf26`
  - `excel_import.csv`: `1100db85c5060c104e574aacb459039aa4bf9ee79f3a07bd23ee8c286b7ca2b8`

## 5. 분석 한계 및 미실행 항목 (`NOT_EXECUTED`)
- **분석 한계**: 비공개 가림 40개소 미복원, 4장 결론 `BUA-03` 오기(실제 `BUE-03`) 보존, INES 최종 등급 미확정(기초 0등급), 중장기대책 9건(`24.08~26.12`) 이행 완료 여부 미확인.
- **미실행 항목 (`NOT_EXECUTED`)**:
  - GitHub 직접 커밋·푸시 및 원격 재조회: `NOT_EXECUTED` (GitHub 쓰기 인증 미설정; 사용자 직접 반영 예정)
  - `report.md` A4 실제 인쇄/PDF 렌더링 검증: `NOT_EXECUTED`
  - 기존 통합 엑셀 파일 실제 적재 및 수식 평가: `NOT_EXECUTED` (독립성 유지를 위해 미열람)
