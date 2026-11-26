# 독립 분석 검증 기록 — ROOT-010 (200719HU6)

## 1. 기본 및 원본 검증 정보
- **QUEUE_ID / EVENT_ID**: `ROOT-010` / `200719HU6`
- **분석 모델 / 버전**: `GEMINI` / `미확인 (null)`
- **분석 수행일**: `2026-11-26`
- **원본 PDF 파일명**: `2020-07-19_한울 6호기 원자로냉각재펌프 2대 정지로 인한 원자로 자동정지.pdf`
- **원본 보고서 번호 / 발행일**: `2020-02호(200719HU6)` / `2020-10-07`
- **원본 PDF 크기 / 페이지 수**: `1,597,832 bytes` / `54쪽` (중립 큐 일치)
- **SHA-256 / 확인 방법**: `ea3b42066aaf35d3e9d9fc8ebb61aad118afb20954f2dab8d3901e045237cabc` / 로컬 바이너리 `hashlib.sha256` 직접 계산 (`BINARY_HASH_VERIFIED`)
- **판독 범위**: 전 54쪽 텍스트 추출 및 본문·핵심 붙임(붙임 3, 4, 12~14 등) 판독 완료
- **상태 플래그**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 40속성 역할별 · 검토결과별 집계
- **역할별**: `D`: 12개, `I`: 9개, `A`: 3개, `H`: 0개, `P`: 0개, `N`: 16개 (총 40개)
- **검토결과별**: `선정`: 21개, `판단보류`: 3개, `미선정`: 16개 (총 40개)

## 3. 15개 항목 검증 결과 (전수 PASS)

| 검증 항목 | 결과 | 확인 내용 |
| :--- | :---: | :--- |
| 1. JSON 스키마 검증 | PASS | standards/independent_ai_review_v1.schema.json 정식 검증 통과 |
| 2. 40속성 누락·중복 검증 | PASS | 총 40개, 고유 40개 |
| 3. 역할-검토결과 매핑 일치 | PASS | D/I→선정, A→판단보류, H/P/N→미선정 전수 일치 |
| 4. 사실 ID 참조 무결성 | PASS | 사실 원장 15건(GEMINI-F01~F15) 참조 유효 |
| 5. 선정 속성 근거·출처 구비 | PASS | 선정 21개 모두 fact_ids 및 source_refs 구비 |
| 6. CSV 헤더·행수·UTF-8 검증 | PASS | 헤더 일치, 데이터 40행 |
| 7. JSON-CSV 40행 일치 검증 | PASS | review_key·queue_id·event_id·code·review_result 전수 일치 |
| 8. CSV 수식 인젝션 방지 검증 | PASS | 위험 접두문자(=,+,-,@) 없음 |
| 9. 보고서 6장 구성·집계 일치 | PASS | 1~6장 구성 및 JSON/CSV 집계 일치 |
| 10. 상태·승인 플래그 검증 | PASS | prompt_version=1.0, status=INDEPENDENT_DRAFT, approved=false, can_ship=false |
| 11. 모델 독립성 유지 검증 | PASS | 타 AI 산출물·통합 Excel 미열람 |
| 12. 원본 판본·SHA-256 일치 검증 | PASS | SHA-256·1,597,832 bytes·54쪽 전수 일치 |
| 13. 모델 버전 미임의기입 검증 | PASS | model.version=null 기록 |
| 14. 익명·미수록 정보 미추정 검증 | PASS | 익명 참여자 미추정 및 INES 미수록 한계 명시 |
| 15. 미수행 외부작업 명시 검증 | PASS | GitHub 커밋·A4 PDF 렌더·통합 Excel 적재 NOT_EXECUTED 명시 |

## 4. 분석 한계 및 실제 미수행 항목 (`NOT_EXECUTED`)
- **원본 익명 처리·INES 미수록**: 원문 유지(임의 추정 없음)
- **GitHub 원격 저장소 커밋·푸시**: `NOT_EXECUTED` (샌드박스 환경 GitHub 쓰기 인증 정보 부재 → ZIP 패키지 반환)
- **A4 인쇄용 PDF 렌더링 및 3AI 통합 Excel 적재**: `NOT_EXECUTED` (독립 초안 단계 범위 외)
