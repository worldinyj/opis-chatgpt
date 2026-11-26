# OPIS 독립 안전문화 분석 검증 기록 (validation.md)

## 1. 사건 및 모델 정보
- **QUEUE_ID**: `ROOT-005`
- **EVENT_ID**: `250314SH2`
- **EVENT_NAME**: 신한울2호기 보조건물 관리구역 정상배기 공기정화기 입구 방사선감시기 경보 발생
- **ANALYZER**: `GEMINI`
- **실제 사용한 모델 버전**: 미확인 (`review.json` 내 `model.version: null` 기록)
- **REVISION**: `v1`
- **분석 수행일**: `2026-11-26`
- **적용 기준**: `workflow_version=1.1`, `prompt_version=1.0`, `standard_version=1.0`, `schema_version=1.0`
- **문서 상태**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 원본 PDF 판본 및 해시 검증
- **원본 PDF 파일명**: `2025-03-14_신한울2호기 보조건물 관리구역 정상배기 공기정화기 입구 방사선감시기 경보 발생 사건조사 보고서_OPIS.pdf`
- **원본 보고서 번호 / 발행일**: `2025-03호(250314SH2)` / `2025-08-13`
- **원본 PDF 페이지 수**: `35`쪽 (큐 기대값 `35`쪽과 일치)
- **원본 PDF 파일 크기**: `997,678` bytes (큐 기대값 `997,678` bytes와 일치)
- **원본 PDF SHA-256**: `c79f5dab8a197d8b17e0addb985cf4a43640f610a74e0d5b188576dfc2589d4f` (큐 기대값과 100% 일치)
- **실제 확인 방법**: Google Drive에서 다운로드한 원본 PDF 바이너리에 대해 Python `hashlib.sha256`으로 해시를 직접 계산(`BINARY_HASH_VERIFIED`)하고 `pdfplumber`로 전 35쪽 텍스트·표를 전수 판독함.

## 3. 40속성 역할별 집계
| 구분 | 역할 | 개수 | 해당 속성 코드 |
| :--- | :---: | :---: | :--- |
| 선정 | `D` | 3 | `CO1`, `PI1`, `WP3` |
| 선정 | `I` | 7 | `PA3`, `QA1`, `QA2`, `QA4`, `DM2`, `PI2`, `WP1` |
| 판단보류 | `A` | 4 | `DM1`, `CL3`, `PI4`, `WP2` |
| 미선정 | `H` | 4 | `PA2`, `QA3`, `LA5`, `PI3` |
| 미선정 | `P` | 2 | `CL1`, `WP4` |
| 미선정 | `N` | 20 | `PA1`, `CO2`, `CO3`, `CO4`, `LA1`, `LA2`, `LA3`, `LA4`, `LA6`, `LA7`, `LA8`, `DM3`, `WE1`, `WE2`, `WE3`, `WE4`, `CL2`, `CL4`, `RC1`, `RC2` |
| **합계** | **전체** | **40** | **선정 10개 / 판단보류 4개 / 미선정 26개** |

## 4. 15개 품질검증 항목 결과
| 번호 | 검증 항목 | 결과 | 세부 확인 내용 |
| :---: | :--- | :---: | :--- |
| 1 | 원본 사건 ID 일치 | PASS | `250314SH2` (`2025-03호(250314SH2)`) 일치 (표지 날짜 오기 `2024.03.14.` 한계 기록) |
| 2 | 원본 판본 정보 확인 | PASS | 파일 크기 997,678 bytes, 35쪽, SHA-256 큐 기대값 100% 일치 (`BINARY_HASH_VERIFIED`) |
| 3 | 40속성 누락 검사 | PASS | 40/40 속성 존재, 누락 0건 |
| 4 | 40속성 중복 검사 | PASS | 유일 코드 40건, 유일 `review_key` 40건, 중복 0건 |
| 5 | 표준 코드 및 명칭 일치 | PASS | `standards/safety_culture_40.json`과 40개 코드·표준 명칭 100% 일치 |
| 6 | D/I/A/H/P/N 집계 일치 | PASS | D:3, I:7, A:4, H:4, P:2, N:20 (합계 40) 전 파일 일치 |
| 7 | 선정 결과와 역할 매핑 일치 | PASS | D/I→선정(10), A→판단보류(4), H/P/N→미선정(26) 100% 일치 |
| 8 | D/I 선정 근거 존재 | PASS | 선정 10개 속성 모두 1건 이상의 `fact_ids` 및 `source_refs` 보유 |
| 9 | 사실 ID 참조 유효성 | PASS | `GEMINI-F01`~`GEMINI-F13` 외 미등록 참조 0건 |
| 10 | 원문 페이지 범위 확인 | PASS | 모든 `pdf_pages` 1~35쪽, `printed_pages` 1~30쪽 범위 내 |
| 11 | JSON 스키마 검증 | PASS | Python `jsonschema` (`independent_ai_review_v1.schema.json`) 통과 |
| 12 | `report.md`와 `review.json` 일치 | PASS | 6장 구성 및 40속성 요약표 코드·명칭·역할·검토결과 100% 일치 |
| 13 | `review.json`과 CSV 일치 | PASS | UTF-8, 정확히 40행, 헤더·검토키·결과·사유 100% 일치 |
| 14 | CSV 수식 주입 위험 검사 | PASS | `=`, `+`, `-`, `@` 시작 셀 0건 |
| 15 | 독립성 및 미승인 상태 확인 | PASS | `other_ai_outputs_seen: false`, `INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false` |

- **산출물 3종 SHA-256**:
  - `report.md`: `71d4e6a50c28f058f77d6c0e571416161d940466536481969f2316245ae4e609`
  - `review.json`: `689e3e6001f57d6524950e502b070c36802add012bfb3e82021bc1e52ee54872`
  - `excel_import.csv`: `d03f78b85797cddc2c0c6fe1a56c793ce1dc2591c6ddae83d6cc1e77c558470c`

## 5. 분석 한계 및 미실행 항목 (`NOT_EXECUTED`)
- **분석 한계**: 원본 표지(PDF 1쪽) 날짜 오기(`2024.03.14.` vs 실제 `2025.03.14.`) 보존, 비공개 가림 12개소 미복원, INES 기초등급 숫자 미기재 및 최종 등급 미확정, 중장기조치 1건(`~25.10`) 이행 완료 여부 미확인.
- **미실행 항목 (`NOT_EXECUTED`)**:
  - GitHub 직접 커밋·푸시 및 원격 재조회: `NOT_EXECUTED` (실행 환경에 GitHub 쓰기 인증/토큰 미설정)
  - `report.md` A4 실제 인쇄/PDF 렌더링 검증: `NOT_EXECUTED`
  - 기존 통합 엑셀 파일 실제 적재 및 수식 평가: `NOT_EXECUTED` (독립성 유지를 위해 미열람)
