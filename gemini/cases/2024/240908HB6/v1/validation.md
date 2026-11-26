# OPIS 독립 안전문화 분석 검증 기록 (validation.md)

## 1. 사건 및 모델 정보
- **QUEUE_ID**: `ROOT-002`
- **EVENT_ID**: `240908HB6`
- **EVENT_NAME**: 한빛6호기 기체방사성물질 배출운전 중 격납건물 배기감시기를 통한 연속감시 미수행
- **ANALYZER**: `GEMINI`
- **실제 사용한 모델 버전**: 미확인 (`review.json` 내 `model.version: null` 기록)
- **REVISION**: `v1`
- **분석 수행일**: `2026-11-26`
- **적용 기준**: `workflow_version=1.1`, `prompt_version=1.0`, `standard_version=1.0`, `schema_version=1.0`
- **문서 상태**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 원본 PDF 판본 및 해시 검증
- **원본 PDF 파일명**: `2024-12-27_한빛 6호기 기체방사성물질 배출운전 중 격납건물.pdf`
- **원본 보고서 번호 / 발행일**: `2024-13호(240908HB6)` / `2025-07-07`
- **원본 PDF 페이지 수**: `42`쪽 (큐 기대값 `42`쪽과 일치)
- **원본 PDF 파일 크기**: `3,300,962` bytes (큐 기대값 `3,300,962` bytes와 일치)
- **원본 PDF SHA-256**: `62a1417f0743f9fd1d81ef4c93a83b81f77daf27547ff58922cc0bac2fdba7b3` (큐 기대값과 100% 일치)
- **실제 확인 방법**: Google Drive에서 다운로드한 원본 PDF 바이너리에 대해 Python `hashlib.sha256`으로 해시를 직접 계산(`BINARY_HASH_VERIFIED`)하고 `pdfplumber`로 텍스트·표를 추출하였으며, 텍스트층이 누락된 핵심 이미지 본문 2쪽(PDF 9·12쪽)을 `pdftoppm`으로 렌더링해 시각 판독함.

## 3. 40속성 역할별 집계
| 구분 | 역할 | 개수 | 해당 속성 코드 |
| :--- | :---: | :---: | :--- |
| 선정 | `D` | 9 | `QA4`, `LA5`, `DM1`, `DM2`, `PI1`, `WP1`, `WP2`, `WP3`, `WP4` |
| 선정 | `I` | 4 | `PA1`, `PA2`, `QA1`, `QA2` |
| 판단보류 | `A` | 3 | `PA3`, `CO1`, `CL1` |
| 미선정 | `H` | 3 | `QA3`, `LA7`, `CL2` |
| 미선정 | `P` | 2 | `CO3`, `PI3` |
| 미선정 | `N` | 19 | `CO2`, `CO4`, `LA1`, `LA2`, `LA3`, `LA4`, `LA6`, `LA8`, `DM3`, `WE1`, `WE2`, `WE3`, `WE4`, `CL3`, `CL4`, `PI2`, `PI4`, `RC1`, `RC2` |
| **합계** | **전체** | **40** | **선정 13개 / 판단보류 3개 / 미선정 24개** |

## 4. 15개 품질검증 항목 결과
| 번호 | 검증 항목 | 결과 | 세부 확인 내용 |
| :---: | :--- | :---: | :--- |
| 1 | 원본 사건 ID 일치 | PASS | `240908HB6` (`2024-13호(240908HB6)`) 일치 |
| 2 | 원본 판본 정보 확인 | PASS | 파일 크기 3,300,962 bytes, 42쪽, SHA-256 큐 기대값 100% 일치 (`BINARY_HASH_VERIFIED`) |
| 3 | 40속성 누락 검사 | PASS | 40/40 속성 존재, 누락 0건 |
| 4 | 40속성 중복 검사 | PASS | 유일 코드 40건, 유일 `review_key` 40건, 중복 0건 |
| 5 | 표준 코드 및 명칭 일치 | PASS | `standards/safety_culture_40.json`과 40개 코드·표준 명칭 100% 일치 |
| 6 | D/I/A/H/P/N 집계 일치 | PASS | D:9, I:4, A:3, H:3, P:2, N:19 (합계 40) 전 파일 일치 |
| 7 | 선정 결과와 역할 매핑 일치 | PASS | D/I→선정(13), A→판단보류(3), H/P/N→미선정(24) 100% 일치 |
| 8 | D/I 선정 근거 존재 | PASS | 선정 13개 속성 모두 1건 이상의 `fact_ids` 및 `source_refs` 보유 |
| 9 | 사실 ID 참조 유효성 | PASS | `GEMINI-F01`~`GEMINI-F12` 외 미등록 참조 0건 |
| 10 | 원문 페이지 범위 확인 | PASS | 모든 `pdf_pages` 1~42쪽, `printed_pages` 1~40쪽 범위 내 |
| 11 | JSON 스키마 검증 | PASS | Python `jsonschema` (`independent_ai_review_v1.schema.json`) 통과 |
| 12 | `report.md`와 `review.json` 일치 | PASS | 6장 구성 및 40속성 요약표 코드·명칭·역할·검토결과 100% 일치 |
| 13 | `review.json`과 CSV 일치 | PASS | UTF-8, 정확히 40행, 헤더·검토키·결과·사유 100% 일치 |
| 14 | CSV 수식 주입 위험 검사 | PASS | `=`, `+`, `-`, `@` 시작 셀 0건 |
| 15 | 독립성 및 미승인 상태 확인 | PASS | `other_ai_outputs_seen: false`, `INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false` |

- **산출물 3종 SHA-256**:
  - `report.md`: `eaeb40f70a7dd82aa19d6c8b8473a0107ac111d21fc8f66725ba3d14729f90dc`
  - `review.json`: `889781dac8acf037dc5b89d73ca55e8e91cb6fbf1e5c98f7a5509d233f478546`
  - `excel_import.csv`: `23f2d0fc96d440a1ab6b81afad43794101583e52fbc9947ea21a8f601243e7f7`

## 5. 분석 한계 및 미실행 항목 (`NOT_EXECUTED`)
- **분석 한계**: 비공개 가림 정보 미복원, 2.1절 요일 오기('(화)' vs 실제 일요일) 및 3.2.1절 점검일자 오기('24.12.26.' vs 실제 '24.12.24.') 보존, INES 최종 등급 미확정(기초 0등급).
- **미실행 항목 (`NOT_EXECUTED`)**:
  - GitHub 직접 커밋·푸시 및 원격 재조회: `NOT_EXECUTED` (GitHub 쓰기 인증 미설정; 사용자 직접 반영 예정)
  - `report.md` A4 실제 인쇄/PDF 렌더링 검증: `NOT_EXECUTED`
  - 기존 통합 엑셀 파일 실제 적재 및 수식 평가: `NOT_EXECUTED` (독립성 유지를 위해 미열람)
