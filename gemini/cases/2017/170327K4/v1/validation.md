# 독립 분석 검증 기록 — ROOT-014 (170327K4)

## 1. 기본 및 원본 검증 정보
- **QUEUE_ID / EVENT_ID**: `ROOT-014` / `170327K4`
- **분석 모델 / 버전**: `GEMINI` / `미확인 (null)`
- **분석 수행일**: `2026-11-26`
- **원본 PDF 파일명**: `2017-03-28_고리4호기_증기발생기_A_수실_배수관_배수_밸브_용접부_누설부위_정비를_위한_원.pdf`
- **원본 보고서 번호 / 발행일**: `2017-2호(170327K4)` / `2018-04-05`
- **원본 PDF 크기 / 페이지 수**: `375,547 bytes` / `17쪽` (중립 큐 일치)
- **SHA-256 / 확인 방법**: `28bf6cf2a650b8281d56edc2a49c968e36fa8a3887d7077042c1f37806eb23c2` / 로컬 바이너리 `hashlib.sha256` 직접 계산 (`BINARY_HASH_VERIFIED`)
- **판독 범위**: 전 17쪽 텍스트 추출(15,540자) 및 본문 전체(표지·요약·1~6장) 정밀 판독 완료
- **상태 플래그**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 40속성 역할별 · 검토결과별 집계
- **역할별**: `D`: 11개, `I`: 8개, `A`: 2개, `H`: 0개, `P`: 1개, `N`: 18개 (총 40개)
- **검토결과별**: `선정`: 19개, `판단보류`: 2개, `미선정`: 19개 (총 40개)

## 3. 15개 항목 검증 결과 (전수 PASS)

| 검증 항목 | 결과 | 확인 내용 |
| :--- | :---: | :--- |
| 1. 필수 산출물 생성 검증 | PASS | report.md, review.json, excel_import.csv 생성 완료 |
| 2. JSON Schema 준수 검증 | PASS | independent_ai_review_v1.schema.json 통과 |
| 3. 40개 세부속성 완전성·순서 검증 | PASS | PA1~WP4 40개 속성 누락·중복 없음 |
| 4. 역할-검토결과 매핑 일치 | PASS | D/I→선정, A→판단보류, H/P/N→미선정 전수 일치 |
| 5. 사실 대장 참조 무결성 | PASS | GEMINI-F01~F07 참조 무결 및 선정/보류/긍정 근거 연결 |
| 6. CSV 헤더·40행 구조 검증 | PASS | UTF-8, 정확 헤더 7열 + 데이터 40행 |
| 7. JSON-CSV 40행 일치 검증 | PASS | review_key·queue_id·event_id·code·review_result 전수 일치 |
| 8. CSV 수식 인젝션 방지 검증 | PASS | 위험 접두문자(=,+,-,@) 없음 |
| 9. 보고서 6장 구성·집계 일치 | PASS | 1~6장 구성 및 JSON/CSV 집계 일치 |
| 10. 상태·승인 플래그 검증 | PASS | prompt_version=1.0, status=INDEPENDENT_DRAFT, approved=false, can_ship=false |
| 11. 모델 독립성 유지 검증 | PASS | 타 AI 산출물·통합 Excel 미열람 |
| 12. 원본 판본·SHA-256 일치 검증 | PASS | SHA-256·375,547 bytes·17쪽 전수 일치 |
| 13. 모델 버전 미임의기입 검증 | PASS | model.version=null 기록 |
| 14. 보고서 원문 한계·수치 차이 명시 | PASS | INES 미수록·집수조 증가율 표기 차이·2011년 면담 미수록·장기대책 예정 명시 |
| 15. 미수행 외부작업 명시 검증 | PASS | GitHub 커밋·A4 PDF 렌더·통합 Excel 적재 NOT_EXECUTED 명시 |

## 4. 분석 한계 및 실제 미수행 항목 (`NOT_EXECUTED`)
- **원문 한계**: INES 등급 미수록, 집수조 수위증가율 절간 수치 차이, 2011년 고진동 미조치 상세 경위 미수록, 장기대책 4건 이행 예정('18.11~'20.12)
- **GitHub 원격 저장소 커밋·푸시**: `NOT_EXECUTED` (샌드박스 환경 GitHub 쓰기 인증 정보 부재 → ZIP 패키지 반환)
- **A4 인쇄용 PDF 렌더링 및 3AI 통합 Excel 적재**: `NOT_EXECUTED` (독립 초안 단계 범위 외)
