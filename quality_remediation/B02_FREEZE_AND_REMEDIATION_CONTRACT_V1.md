# B02 — 원본 동결 재검증 및 보완 입력 계약 V1

2026-11-27 / B01 manifest blob 5c79edd86f4bcbd9d8ac648b389967610d43802d
원본 기준 fa145c17aff92e3ccf21ded05d0e85f545b0ab22
비교 대상 main 고정 ref 8775c5ae6249cf0f8bcd70d513e3296cbb46343e

## 실행 결과
B01 manifest의 각 경로를 비교 대상 ref에서 직접 fetch하고 반환 blob SHA를 대조했다. 35/35 원본·접수 파일, 4/4 기준 파일 일치(39/39). 15+15+9 경로로 분할 조회; 불일치 0. 파일의 전체 바이너리 SHA-256 재계산 및 PDF 검증은 미수행. 이 결과는 해당 ref에만 유효하다.
대상 ROOT-004,014,015,017,018,019,020. 280행에 대한 B01 진단은 유지한다. HOLD 해제 0.

## B03/B04 입력 및 출력 규약
- 입력은 B01 manifest source_ref에서만 읽는다. 실행 직전 모든 blob 재검증, 원본 byte SHA-256은 실제 bytes로 별도 계산하고 기록값과 비교한다. 실패 또는 미확인이면 해당 사건 파생본 생성 중지. 경로는 manifest allowlist만 허용; 심볼릭 링크·경로 탈출 금지.
- JSON은 UTF-8, 중복 키 금지, Draft 2020-12 schema + format checker, 표준 40개 코드/명칭/키/역할 매핑, 사건 ID 문자열과 모델별 사실 ID 연결 검증. CSV는 엄격한 RFC4180 parser, 정확한 7열 헤더, 40행, 빈/중복/초과 키 금지. BOM은 명시 검출·기록. 원본 CSV와 JSON의 사건·키·판정·사실 ID 집합이 다르면 중지.
- rationale은 JSON 문자열 그대로. 원래 CSV가 JSON과 정확히 일치하거나 [해당 역할]+공백만 추가된 경우에만 형식 보완 허용. 그 외 차이는 HOLD.
- source는 보고서 번호(기록된 경우), 각 source_ref 순서대로 section, printed_pages, pdf_pages를 분리 직렬화하고 fact_ids를 기록 순서대로 포함. 여러 위치는 세미콜론으로 분리. 페이지 값·절·사실 ID 생성 또는 추정 금지. summary는 원본 JSON에 보존하며 위치로 대체하지 않는다.
- source_refs와 fact_ids가 모두 빈 배열일 때만 정확히 '해당 원문 근거 없음' 사용. 한쪽만 비어 있으면 수동 검토로 보류한다. D/I의 근거 누락, 존재하지 않는 사실 ID, 연결된 사실에 없는 페이지는 형식 보완으로 해소하지 않는다.
- CSV 수식 주입 검사: 모든 셀의 선행 공백 제거 후 =,+,-,@ 및 탭/CR/LF 등 위험 접두어를 탐지하면 자동 수정 없이 보류. CSV quoting만으로 보호된다고 가정하지 않는다.
- ROOT-004 DM3의 p.68,69 ledger gap 및 PDF 판본·물리쪽·붙임 검증은 별도 B05 필수. 원래 판단·근거는 수정 금지. ROOT-004는 자동 보완 배치에서 제외.
- 결과는 quality_remediation/derived/<queue_id>/v1/ 하위에만 작성. derived CSV, row_diff.json(키별 변경 전후와 규칙 ID), provenance.json(source_ref, original_review_blob, original_csv_blob, original byte SHA-256, derived_csv_sha256, transform_version, validation_report, authorization_reference=null), validation.json. 원본 모델·작성자와 파생 변환자 구별.
- 40개 역할/판정/JSON 사유/사실 참조 불변, 신규 오류 0, 원본 불변을 독립 재검증. 출력은 후보로만 관리. 승인 전 C의 실제 입력 및 기존 Excel 반영 금지.
- B03 검증기 회귀시험: 정상/인용 쉼표·개행/중복키/잘못된 역할/근거 누락/알 수 없는 fact/수식 접두어/원본 blob 불일치/ROOT-004 gap/부분 입력. 실제 CSV 생성은 B04, 원문 의미 검증은 별도.

## 게이트
approved=false / can_ship=false / eligible_for_three_ai_consensus=false / main_merge=false.
PDF 판독·의미 검증·보완 CSV 생성·B03 코드 실행은 이번 단계 미수행.
