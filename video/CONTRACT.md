# 멀티미디어 제작 계약 v2.0

JSON Schema Draft 2020-12 여섯 종류: production(세 영상 유형), fact_ledger, learning_ledger, ppt, discussion_action, batch_job. 모든 산출물은 사건 ID와 원본 판본에 연결. 교육 파생물은 분석 버전 및 표준 버전과 연결하고 사건 이해 영상은 AI 해석과 분리한다. 경로는 문서 위치 기준 상대경로로 관리(원본 document_path는 사건 media 공통 기준; manifest provenance 경로는 각 산출물 폴더 기준으로 설정, 중첩 숏폼은 아래 예제의 경로 보정 참조). 승인 전 PLANNED/DRAFT. 실제 파일 경로/해시/검토자는 생성·확인 이후 채운다.

- 사실 원장: F ID, 유형, 원문 절, 인쇄쪽과 PDF쪽, 판단 한계 및 검토 상태.
- 학습 원장: L ID, 사실·원인·보고서 절, 원칙/속성, 교육 목표, 추가 후보 분리. 코드 정의는 standards/safety_culture_40.json 기준.
- 영상: 9:16/16:9, 실제 width/height/fps, 구간별 길이 및 겹침, 제작 모드와 경로 분리. 시간 = sum(duration-overlap); 마지막 overlap=0. I2V 입력 모드, 정지 이미지 motion_plan, 통제형 속성 카드, 시도/채택 기록. 속성 카드 1개에 핵심 후보 전체를 묶는다. PPT도 동일. 실제 화면 가독성·음성·내용은 인간 검수.
- 배치: 장면·revision·비율·작업/시도 ID 매핑, 실제 결과와 해시 및 승인. 서비스 자동 연동 아님.
- PPT: 네이티브 편집 가능 요소, 슬라이드별 근거/학습 ID/노트. PPTX 생성은 후속.
- 토론: 3 질문, 2 가상 시나리오, 개인/팀 실천과 확인.

검증: JSON Schema(표준 준수는 독립 jsonschema 도구 권장) 및 저장소 자체 교차검증기. 자체 검사기는 이 저장소에서 사용하는 JSON Schema 키워드 부분집합만 지원한다. 상태 전이, 실제 파일 존재·해시, 프롬프트 빌드, 미디어 기술 사양 및 의미 검수는 후속 구현. `node video/tests/validate_pilot.mjs`로 시범 문서를 구조 및 관계 검사한다. 스키마는 형식 계약이지 승인/정확성 보증이 아니다.
