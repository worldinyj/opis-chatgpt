# B07 — Gemini HOLD 7건 종합 품질평가 및 승인 준비
2026-11-27. 품질 브랜치 전용. 원본 모델 분석·공식 Excel·main은 변경하지 않는다.
## 1. 결과 요약
B01~B06 기록 종합: 실제 원본 7건 280속성, 39개 Git blob 동결 확인(B02), 28개 원본 산출물 SHA256 일치(B03-R1), 6건 240속성 파생 CSV(B04), 6건 240행 별도 형식 재검증 오류 0(B06). 6건 형식 보완 후보, 1건 원문/근거 수동 검토 대상. 원래 7건 모두 HOLD이며 별도 적격 결정 없음.
| 사건 | 선정 | 판단보류 | 미선정 | 보완 | 후속 |
|---|---:|---:|---:|---|---|
| ROOT-004 / 240319W3 | 23 | 5 | 12 | 미생성 | DM3 사실 대장 및 독립판독 범위 |
| ROOT-014 / 170327K4 | 19 | 2 | 19 | 형식 PASS | 원본 PDF/독립 QA |
| ROOT-015 / 161220HU5 | 13 | 2 | 25 | 형식 PASS | 원본 PDF/독립 QA |
| ROOT-017 / 150903K4 | 17 | 2 | 21 | 형식 PASS | 원본 PDF/독립 QA |
| ROOT-018 / 141017Y3 | 19 | 2 | 19 | 형식 PASS | 원본 PDF/독립 QA |
| ROOT-019 / 141001Y12 | 19 | 2 | 19 | 형식 PASS | 원본 PDF/독립 QA |
| ROOT-020 / 140617W4 | 18 | 2 | 20 | 형식 PASS | 원본 PDF/독립 QA |
| 합계 | 128 | 17 | 135 | 240행 | 7건 HOLD |
위 집계는 HOLD 대상 원래 Gemini 역할별 수이며 타 모델 비교, 전문가 확정 또는 공식 취약성 통계가 아니다.
## 2. 판본·근거
ROOT-004 실제 PDF 11,276,268 bytes/88 physical pages/SHA256 일치(B05); 인쇄쪽 68~69의 협의 기록 확인. 원 제출 F14에는 해당 페이지와 협의 요약 연결이 누락되어 있다. P/미선정 판단 자동 변경 금지. 제출자의 당시 붙임 14~16 미열람 제한 역시 보존. B03-R1에서 ROOT-004의 28개 절 문자열 차이가 기록되어 있으며 의미적 동등성 판단 미완료. 독립 수정 제출 또는 전문가 검토 필요. 기타 6건은 원본 PDF 실측 및 의미 검증 미실행; 모델의 보고된 검증과 본 감사의 검증을 구별한다.
## 3. 승인 게이트(B08)
건별 고정 원본/파생 해시와 provenance 확인, 실제 PDF 판본 검증, 독립 QA 검토자·시각·결론·근거 기록, 작성자 독립성 확인, 원본 JSON 판단 불변 여부 확인, 명시적 적격성 결정. 6건은 형식 보완 심사에 회부 가능하나 자동 승인 금지. ROOT-004는 수정 개정판 또는 전문가 근거 검토 후 새 검증 실행. 기존 31건 또한 STORED/PENDING_INTEGRATION과 적격은 별개. 사용자의 승인만으로 미충족 기술/독립성 게이트를 PASS 처리하지 않는다.
## 4. 근거 및 제한
- HOLD_MANIFEST_V1.json (B01); B03_R1_ACTUAL_INPUT_AUDIT.json; B04_FORMAT_CANDIDATE_REPORT.json; B05_ROOT004_SOURCE_REINSPECTION.md; B06_FORMAT_RECHECK_REPORT.json.
- 기준 원본 ref fa145c17aff92e3ccf21ded05d0e85f545b0ab22, 후보 ref 15bf4b48799a10e057cf3586e9d7d9a53080ddb4, B06 ref 215275e9f0c4cf53bf9398a118966c3459405664.
- B03-R1은 별도 JS 검증이며 실제 Python CLI 미실행. B06은 같은 assistant의 별도 재검증으로 독립 인적/모델 QA 아님. 새로운 원문 판독은 이번 B07에서 미실행. B08은 승인 대기 상태이지 자동 활성화가 아님.
approved=false / can_ship=false / eligible_for_three_ai_consensus=false / main_merge=false.
