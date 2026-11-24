# MEDIA-008 검증 기록

첨부 PDF 원본 해시 및 40쪽 로컬 확인. 작성자 재대조 및 GitHub에서 재조회한 R3/R2 데이터에 기존 validate_contract.mjs 함수를 JavaScript 실행환경에서 직접 사용. 28/28 검증 통과. PPTX R3 실제 로컬 생성 및 LibreOffice PDF 12/12 렌더, 219개 native shape, 노트 12/12 일치, 경계 이탈 0, 렌더링 텍스트 누락 0. PowerPoint 및 교육장 투사 미실시. 파일 SHA-256 a00c753be915f31ba2d512e169b4d1bb94ccd81fe5da31f94fdb25d387101c93 / Git blob 4c42896f4fe0cb781a4083b9f4d5394cf83049ec: GitHub 생성값 일치. 기존 생성기 사용. 독립 검토 및 전문가 승인 없음, 실제 유료 생성 0.

| 검사 | 결과 |
|---|---|
| fact_ledger 250919W2 schema | PASS |
| learning_ledger 250919W2 schema | PASS |
| production IU-250919W2 schema | PASS |
| production SC-250919W2 schema | PASS |
| production SM-250919W2-01 schema | PASS |
| ppt PPT-250919W2 schema | PASS |
| discussion_action DA-250919W2 schema | PASS |
| IU-250919W2 relations | PASS |
| SC-250919W2 relations | PASS |
| SM-250919W2-01 relations | PASS |
| PPT-250919W2 relations | PASS |
| DA-250919W2 relations | PASS |
| IU-250919W2 batch schema | PASS |
| IU-250919W2 batch relations | PASS |
| SC-250919W2 batch schema | PASS |
| SC-250919W2 batch relations | PASS |
| SM-250919W2-01 batch schema | PASS |
| SM-250919W2-01 batch relations | PASS |
| 40 code partition | PASS |
| all approvals pending | PASS |
| no generated assets | PASS |
| PPT notes 38min | PASS |
| facts page offset | PASS |
| all narration filled | PASS |
| positive response source | PASS |
| source evaluation unit consistent | PASS |
| discussion 3 questions 2 hypothetical scenarios 6 actions | PASS |
| all analysis revisions | PASS |

실제 검증 범위: 스키마 사용 키워드의 부분집합 및 교차관계. 기존 Node CLI의 전체 재실행, 실제 배치/영상/음성, 보고서 A4 출력, 교육 의미의 독립적 검증은 수행하지 않음.
