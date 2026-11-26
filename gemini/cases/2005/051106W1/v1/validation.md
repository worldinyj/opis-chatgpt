# 독립 분석 검증 기록 — ROOT-031 (051106W1)

## 1. 기본 및 원본 검증 정보
- **QUEUE_ID / EVENT_ID**: `ROOT-031` / `051106W1`
- **분석 모델 / 버전**: `GEMINI` / `미확인 (null)`
- **분석 수행일**: `2026-11-26`
- **원본 PDF 파일명**: `2005-11-06_월성1호기 비상발전기실 스프링클러 오작동에 의한 원자로격물 격리 신호 ᄇ.pdf`
- **원본 보고서 번호 / 발행일**: `2005-14호(051106W1)` / `2005-11-10`
- **원본 PDF 크기 / 페이지 수**: `1,996,480 bytes` / `17쪽` (중립 큐 일치)
- **SHA-256 / 확인 방법**: `32cd0b8a3ba57f7c9ee4c73c4bd7a71d2b61240dbca3eb5ab173dcab033440cb` / 로컬 바이너리 `hashlib.sha256` 직접 계산 (`BINARY_HASH_VERIFIED`)
- **판독 범위**: 전 17쪽 텍스트 추출(11,668자) 및 본문 전체(표지·조사자 명단·요약·1~6장·붙임 1~5; 붙임 1 p.12~13 스캔 이미지) 정밀 판독 완료
- **상태 플래그**: `status=INDEPENDENT_DRAFT`, `approved=false`, `can_ship=false`

## 2. 40속성 역할별 · 검토결과별 집계
- **역할별**: `D`: 5개, `I`: 3개, `A`: 0개, `H`: 0개, `P`: 1개, `N`: 31개 (총 40개)
- **검토결과별**: `선정`: 8개, `판단보류`: 0개, `미선정`: 32개 (총 40개)

## 3. 15개 항목 검증 결과 (전수 PASS)

| 검증 항목 | 결과 | 확인 내용 |
| :--- | :---: | :--- |
| 1. 필수 산출물 생성 검증 | PASS | report.md, review.json, excel_import.csv 생성 완료 |
| 2. JSON Schema 준수 검증 | PASS | independent_ai_review_v1.schema.json 통과 |
| 3. 40개 세부속성 완전성·순서 검증 | PASS | PA1~WP4 40개 속성 누락·중복 없음 |
| 4. 역할-검토결과 매핑 일치 | PASS | D/I→선정, A→판단보류, H/P/N→미선정 전수 일치 |
| 5. 사실 대장 참조·쪽번호 무결성 | PASS | GEMINI-F01~F06 참조 및 인쇄쪽 포함관계 전수 무결 |
| 6. CSV 헤더·40행 구조 검증 | PASS | UTF-8, 정확 헤더 7열 + 데이터 40행 |
| 7. JSON-CSV 40행 일치 검증 | PASS | review_key·queue_id·event_id·code·review_result·rationale(접두어 없음)·source(절/인쇄쪽/PDF쪽) 전수 일치 |
| 8. CSV 수식 인젝션 방지 검증 | PASS | 위험 접두문자(=,+,-,@) 없음 |
| 9. 보고서 6장 구성·집계 일치 | PASS | 1~6장 구성 및 JSON/CSV 집계 일치 |
| 10. 상태·승인 플래그 검증 | PASS | prompt_version=1.0, status=INDEPENDENT_DRAFT, approved=false, can_ship=false |
| 11. 모델 독립성 유지 검증 | PASS | 타 AI 산출물·통합 Excel 미열람 |
| 12. 원본 판본·SHA-256 일치 검증 | PASS | SHA-256·1,996,480 bytes·17쪽 전수 일치 |
| 13. 모델 버전 미임의기입 검증 | PASS | model.version=null 기록 |
| 14. 보고서 원문 한계 명시 | PASS | INES 미수록·시각/절번호 차이·스캔 SOE·보완요구 예정 명시 |
| 15. 미수행 외부작업 명시 검증 | PASS | GitHub 커밋·A4 PDF 렌더·통합 Excel 적재 NOT_EXECUTED 명시 |

## 4. 분석 한계 및 실제 미수행 항목 (`NOT_EXECUTED`)
- **원문 한계**: INES 등급 미수록, 격리 해제 시각 표기 차이(`07:33` vs `09:21:35`)·절 번호 `3.라.` 중복·붙임 1(SOE) 스캔 이미지, 5장 보완요구사항(`'05.12.30` 제출) 예정 상태
- **GitHub 원격 저장소 커밋·푸시**: `NOT_EXECUTED` (샌드박스 환경 GitHub 쓰기 인증 정보 부재 → ZIP 패키지 반환)
- **A4 인쇄용 PDF 렌더링 및 3AI 통합 Excel 적재**: `NOT_EXECUTED` (독립 초안 단계 범위 외)
