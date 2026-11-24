# 범용 전문형 PPT 입력 계약 V1.0

기존 16장 전문형 R1 및 12장 간결형 R3는 변경하지 않는다. 본 모듈은 독립적인 16:9 편집형 PPTX 생성 경로다. Node.js 22, npm 패키지/API/외부 전송 없음. 선택 디자인 WOLSONG_PROFESSIONAL_V1에서 추출한 9개 레이아웃 후보 구현이며, 샘플 사진/아이콘 및 마스터를 복제하지 않는다. Noto Sans CJK KR을 사용하며 글꼴 미포함.

## 실행
저장소 루트에서:

    node education/ppt/generic/generate.mjs cases/2025/250919W2/media/classroom_ppt/GENERIC_16_INPUT.json standards/safety_culture_40.json /tmp/real.pptx
    node education/ppt/generic/generate.mjs education/ppt/generic/fixtures/SYNTHETIC_12.json standards/safety_culture_40.json /tmp/test.pptx
    node education/ppt/generic/run_tests.mjs standards/safety_culture_40.json

생성 결과 PPTX 및 .prepared.json(자동 생성 속성/노트/출처 포함). 입력 수정 없음. 동일 입력과 동일 생성기/표준은 결정적 출력. PDF 렌더는 LibreOffice 별도 실행, PPT-D audit_pptx.py로 검사하고 원문·디자인·교육적 검토 별도 실시.

## 입력 데이터
- schema_version 1.0, event_id, analysis_version, standard_version 1.0, case_type REAL_DRAFT 또는 SYNTHETIC_TEST, status DESIGN_DRAFT, can_ship false.
- source: issuer, report_number, report_date, sha256(실제 사례 64자리 소문자 hex, 원본 파일의 실제 검증은 별도). 자료 제목·사건 요약·수치·단위·기간·발행 이후 현황은 내용 입력/노트에 넣는다. 실제·가상 상태는 자동 바닥글 구분.
- fact_ids: 실제 사실 원장의 ID 목록. learning: [{id,attribute_codes}], 실제 학습 원장의 참조용 투영. core_attribute_codes 및 additional_attribute_codes: 중복/교집합/미등록 코드 차단. 원장은 원본 보고서와 검토 상태를 별도 관리한다. 생성기는 제공된 ID의 내부 일관성만 검사하며, 사실의 진실성이나 원장 파일의 실물 존재를 인증하지 않는다.
- target_slides: 12~16 정수. slides: 실제 구성 순서(개수 일치), 고유 id, pattern, section, label, title, lead, cards(제목/본문 문자열 쌍), minutes(양의 정수), speaker_notes, fact_ids, learning_ids. accent(선택, 6자리 RGB), detail(FACT 필수, METRIC 및 패널 보조 설명), variant(선택, ACTION panel).
- COVER 처음·END 마지막, 모든 9개 패턴을 적어도 한 번 사용, ATTR 단 한 장. ATTR의 cards는 빈 배열, title/lead 자리표시자는 자동 대체. 코드 이름은 저장소 표준 JSON에서 읽고 원칙 제목은 표준 코드에 대응하는 교육용 축약 명칭 사용. 동일 코드의 정의나 명칭을 임의로 바꾸지 않는다. 핵심 후보만 본문, 추가 후보 목록은 노트. 0개도 명시. 2열 균형 배치와 16/15/14/13pt 순차 선택. 13pt까지도 수용 불가능하면 중단; 40개 스트레스 입력 차단 확인. 원칙 10개/속성 10개의 구성 검증은 통과. 코드를 삭제하거나 분산 장표를 자동 생성하지 않는다.
- 12~16장 구성은 작성자가 명시적으로 설계한다. Markdown 원문→슬라이드 콘텐츠의 의미 분석, 자동 축약/병합은 구현하지 않았다. 정보 보존·발표자 노트·원본 근거는 작성자가 확인해야 한다.
- 생성기는 일반 텍스트 길이의 자동 적합화, 실제 폰트 측정 또는 도형 겹침 완전 탐지 기능이 없다. 반드시 실제 렌더와 수동 검토. 긴 제목·카드·노트, 5단계 시간표, 저밀도/고밀도 레이아웃은 신규 사건별 검토.

## 9개 패턴
| 패턴 | 후보 ID | 구현 |
|---|---|---|
| COVER | LAY-COVER-01 | 입력 사건명, 메시지, 교육 목적, 출처 |
| FACT | LAY-FACT-01 | 1~4 카드와 입력 요약 |
| TIME | LAY-TIME-01 | 2~5개 단계, 균등 분배 |
| CAUSE | LAY-CAUSE-01 | 1~4개 원인 카드, 1~3열 및 2×2 |
| PRINC | LAY-PRINC-01 | 1~3개 원칙·행동 행 |
| ATTR | LAY-ATTR-01 | 자동 원칙별 후보 집계·2열 |
| METRIC | LAY-METRIC-01 | 1~5개 수치/평가 카드, 입력 보조 수치 |
| ACTION | LAY-ACTION-01 | 1~4 카드, 선택 패널 |
| END | LAY-END-01 | 1~3개 교훈 및 메시지 |

고정 색상 및 도형은 디자인 후보 구현으로 유지한다. 사건별 값은 입력에서만 공급. 기존 작성자 검토 상태, 전문가 승인, 디자인/권한 승격 상태를 바꾸지 않는다.
