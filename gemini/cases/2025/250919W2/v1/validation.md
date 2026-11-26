# OPIS 독립 안전문화 분석 검증 기록 (validation.md)

## 1. 사건 및 모델 정보
- **EVENT_ID**: `250919W2`
- **QUEUE_ID**: `ROOT-038`
- **ANALYZER**: `GEMINI`
- **REVISION**: `v1`
- **실제 사용한 모델 버전**: 미확인 (`review.json` 내 `model.version: null` 기록)
- **분석 수행일**: `2026-11-26`
- **적용 기준**: `prompt_version=1.0`, `standard_version=1.0`, `schema_version=1.0`
- **문서 상태**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 원본 PDF 판본 및 해시 검증
- **원본 PDF 파일명**: `2025-09-19_월성2호기 감속재정화계통 누설_사건조사보고서_최종.pdf`
- **원본 보고서 번호**: `2025-07호(250919W2)`
- **원본 보고서 발행일**: `2026-03-23`
- **원본 PDF 페이지 수**: `40`쪽 (표지 1쪽, 조사자 명단 1쪽, 본문·붙임·비공개 사유서 인쇄쪽 1~38)
- **원본 PDF SHA-256**: `fb3348d2725396a03689556b717876d8d65c72a79dce6716ae1d8471fe6cec83`
- **실제 확인 방법**: Google Drive에서 다운로드한 원본 PDF 바이너리(1,114,807 bytes)에 대해 Python `hashlib.sha256`으로 직접 해시를 계산(`BINARY_HASH_VERIFIED`)하고, `pdfplumber`로 전 40쪽 텍스트·표를 추출하였으며, `pdftoppm` 렌더링으로 핵심 도면(PDF 13쪽 `SG1` 높이차 3.3m, PDF 18쪽 `ME-28` 높이차 0.72m)을 시각 확인함.

## 3. 40속성 역할별 집계 (기존 분석결과 보존)
| 구분 | 역할 | 개수 | 해당 속성 코드 |
| :--- | :---: | :---: | :--- |
| 선정 | `D` | 9 | `CO1`, `DM1`, `CL1`, `PI1`, `PI2`, `PI3`, `WP1`, `WP3`, `WP4` |
| 선정 | `I` | 6 | `PA1`, `QA2`, `QA4`, `LA5`, `DM2`, `WP2` |
| 판단보류 | `A` | 4 | `PA2`, `PA3`, `QA3`, `LA6` |
| 미선정 | `H` | 6 | `QA1`, `LA2`, `LA3`, `CL2`, `CL4`, `PI4` |
| 미선정 | `P` | 1 | `CO3` |
| 미선정 | `N` | 14 | `CO2`, `CO4`, `LA1`, `LA4`, `LA7`, `LA8`, `DM3`, `WE1`, `WE2`, `WE3`, `WE4`, `CL3`, `RC1`, `RC2` |
| **합계** | **전체** | **40** | **선정 15개 / 판단보류 4개 / 미선정 21개** |

## 4. 무결성 및 형식 검증 결과
- **JSON 스키마 검증**: **PASS** — Python `jsonschema` 라이브러리를 사용하여 `review.json`이 저장소 공식 스키마(`standards/independent_ai_review_v1.schema.json`, Draft 2020-12)에 완전히 부합함을 확인함.
- **40속성 누락 및 중복 확인**: **PASS** — `standards/safety_culture_40.json`의 40개 표준 코드 및 표준 명칭과 순서·철자가 100% 일치하며, 누락 0건, 중복 0건, 유일 `review_key`(`ROOT-038-PA1`~`ROOT-038-WP4`) 40건 확인.
- **사실 ID 참조 검증**: **PASS** — `review.json` 내 사실 원장 21건(`GEMINI-F01`~`GEMINI-F21`)이 모두 유효한 접두사(`GEMINI-F`)와 출처 위치(절, 인쇄쪽, PDF 물리쪽)를 보유하며, 40개 속성이 참조하는 모든 `fact_ids`가 사실 원장 내에 존재함(미등록 참조 0건). `D`/`I` 15개 속성 모두 1건 이상의 `fact_ids`와 `source_refs`를 보유함.
- **보고서·JSON·CSV 일치 여부**: **PASS** — `report.md`(6장 구성, 40속성 요약표), `review.json`(40속성 객체), `excel_import.csv`(UTF-8, 헤더 `review_key,queue_id,event_id,attribute_code,review_result,rationale,source`, 데이터 40행) 간 코드·명칭·역할·검토결과·판단근거(`rationale`)가 100% 일치하며, CSV 셀의 수식 주입(formula injection) 위험 문자(`=`, `+`, `-`, `@`) 시작 사례 0건을 확인함.
- **산출물 3종 SHA-256 (패키징 시점 보존 해시)**:
  - `report.md`: `7396c1ae3b242d1840c697dc3bfcb640d5458580b2e87b5adf17e560e76789b4`
  - `review.json`: `53d36e26e6b48a0810d12f8770e86bd92ba3107af9d0bda484d0005b19cb2b91`
  - `excel_import.csv`: `e1331d084feff5b4f81b027232c6d6ac5448ffdfd6f8daf0c668c5923188395c`

## 5. 독립성 유지 여부
- **독립성 유지 확인**: **PASS (`other_ai_outputs_seen: false`)**
- 기존 ChatGPT 분석자료(`cases/2025/250919W2/` 하위 보고서·원장·검토 패키지, `index/phase3*` 후보 목록, 통합 엑셀) 및 다른 AI 모델 결과는 일절 열람하지 않았으며, 기존 저장소의 어떤 파일도 수정하지 않았다.

## 6. 분석 한계
- **비공개 가림 처리(13개소)**: 원본 인쇄쪽 38(PDF 40쪽) 비공개 처리 사유서(법률 제6조제1항 제3호)에 따라 가림 처리된 절차서 번호, 밸브 표면경화재질 명칭, 제작사 명칭 등은 복원하지 않았다.
- **원본 내부 날짜 오기 보존**: 원본 인쇄쪽 11(PDF 13쪽) '작업 승인 절차 이행 미흡' 항목에 날짜가 `9.19.`로 오기되어 있으나, 2.2절(인쇄쪽 3) 및 3.1절(인쇄쪽 7)의 `9.18.`이 실제 일자임을 `GEMINI-F07`에 한계로 기록하였다.
- **미확정 사항**: 최종 INES 등급은 원전 사건등급평가위원회 결정 예정(기초등급 0등급)이며, 중장기대책 8건의 실제 이행 완료 여부는 본 원본으로 확인할 수 없다.
- **AI 초안 성격**: 본 산출물은 전문가 검토 지원용 독립 초안(`INDEPENDENT_DRAFT`)이며, 공식 규제기관 조사결과나 한수원 공식 안전문화 평가가 아니다.

## 7. 실제 검증을 수행하지 못한 항목
1. **GitHub 직접 커밋·푸시 및 원격 재조회**: 현재 실행 환경에 GitHub 쓰기 인증(`GITHUB_TOKEN`/`GH_TOKEN`, SSH 키 등)이 설정되어 있지 않아 `worldinyj/opis-chatgpt` `main` 브랜치에 직접 커밋·푸시 및 원격 커밋 SHA 재조회를 수행하지 못했다. (읽기 전용 `git fetch`로 원격 `gemini/cases/2025/250919W2/v1/` 경로가 아직 존재하지 않음만 확인함.)
2. **보고서 A4 실제 인쇄·PDF 렌더링 검증**: `report.md`는 마크다운 원고 상태로 작성·검증되었으며, 별도 A4 PDF 변환 및 시각적 쪽수·레이아웃 검증은 수행하지 않았다.
3. **통합 엑셀 파일 실제 적재 테스트**: 독립성 유지를 위해 기존 통합 엑셀(`OPIS_38건_3AI_교차검토_전문가판정_V1.xlsx`)을 열람하지 않았으므로, `excel_import.csv`의 실제 통합 엑셀 반영 및 수식 재계산 테스트는 수행하지 않았다.
4. **전문가 승인 및 현장 사실 추가 검증**: 공개 조사보고서 외의 미공개 면담록·현장 기록 확인 및 원자력안전문화 전문가 검토·승인은 수행되지 않았다.
