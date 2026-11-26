# validation.md — ROOT-012 / 190121W3 / CLAUDE v1

실행 일시: 2026-11-26 (Asia/Seoul). 실제로 실행한 검사만 PASS 또는 FAIL, 실행하지 못한 검사는 NOT_EXECUTED로 표시한다.

| # | 검사 | 결과 | 내용 |
|---|---|---|---|
| 01 | 원본 사건 ID·보고서 번호 일치 | **PASS** | 큐 ROOT-012/190121W3/2019-02와 review.json 일치. 원본 표지 '2019-02호(190121W3)'는 Drive 텍스트 추출본을 읽어 직접 확인(수동). |
| 02 | 원본 판본 및 페이지 확인 | **NOT_EXECUTED** | 판본: Drive 파일 크기 1,635,578 bytes가 큐 기대값과 일치(메타데이터 대조만). SHA-256 미계산(바이너리 접근 불가, 다운로드 프록시 차단) → PDF_READ_HASH_UNAVAILABLE. 물리 페이지 수(기대 55)는 미확인, 인쇄쪽 최대 52만 확인. 판본·쪽수 검증 완료를 주장하지 않으며 통합 판본 확인 대기. |
| 03 | 40속성 완전성 | **PASS** | 속성 40개, 표준 40개와 집합 일치 |
| 04 | 40속성 중복 여부 | **PASS** | 코드·검토키 중복 없음 |
| 05 | 표준 코드·명칭 일치 | **PASS** | name은 표준 JSON과 완전 일치, review_key=ROOT-012-<코드> |
| 06 | 역할별 집계 합계 40 | **PASS** | D2 I5 A2 H1 P3 N27 |
| 07 | 역할과 검토결과 매핑 | **PASS** | D/I→선정, A→판단보류, H/P/N→미선정 |
| 08 | 선정 속성의 원문 근거 | **PASS** | 선정 7개 모두 fact_ids·source_refs(인쇄쪽 포함) 1개 이상 |
| 09 | Claude 사실 ID 참조 | **PASS** | 사실 9개(고유), 속성이 인용한 사실 8개, 본문 내 사실 ID 참조 모두 원장에 존재, GEMINI 등 타 모델 ID 없음: True |
| 10 | 원문 페이지 범위 | **PASS** | 인쇄쪽 1~47(허용 1~52), 속성 source_refs=연결된 사실의 source_refs 합집합. PDF 물리쪽은 미확인(빈 배열)으로 범위 검증 불가 |
| 11 | JSON Schema 검증 | **PASS** | Draft 2020-12 검증, 오류 0건 |
| 12 | report.md와 review.json 일치 | **PASS** | 40행 표(코드·명칭·역할·결과) 일치 불일치=[], 6장 구성=True, 머리말 표기=True, 집계 문구 일치=True, 선정 7개 상세 절 일치=True |
| 13 | review.json과 CSV 일치 | **PASS** | 헤더 정확, 데이터 40행, review_key·코드·결과·사유 일치, source에 사실 ID 포함, 허용값 준수. 불일치=[] |
| 14 | CSV 수식 주입 위험 검사 | **PASS** | 모든 셀의 첫 글자가 = + - @ 탭 CR 아님, UTF-8(BOM 없음), RFC4180 인용 사용. 위반=[] |
| 15 | 독립성 및 미승인 상태 | **PASS** | approved=false, can_ship=false, INDEPENDENT_DRAFT. 타 AI 분석·원장·통합 Excel·등평위 자료 미열람. 단 세션 앞부분(ROOT-038)에서 교육용 영상 전사문 1건을 열람(ROOT-012 분석 근거 미사용, 독립성 집계 여부는 사용자 판단; 경고 사항으로 기록) |

## 추가 사항

- report.md 길이 16,735자(공백 포함). 실제 A4 렌더링·인쇄 쪽수는 확인하지 않았다(NOT_EXECUTED).
- 원문 페이지 검증은 인쇄쪽 기준이다. PDF 물리쪽(1부터)은 PDF 바이너리를 읽지 못해 확인하지 못했고 source_refs.pdf_pages는 빈 배열이다.
- 형식 오류 수정: 검사 중 발견된 형식 오류는 없었다(분석 판단 변경 없음).
- 저장 상태: GitHub 직접 저장은 수행하지 않았다. 실행환경의 GitHub 토큰(GH_TOKEN)이 유효하지 않아 쓰기가 불가능했다. 상태 EXPORTED_PENDING_UPLOAD (ZIP 제공).
- 승인·배포를 주장하지 않는다. approved=false, can_ship=false.
