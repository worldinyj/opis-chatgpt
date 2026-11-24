# Gemini Tasks 외부 배치 초안 R2

2개 이미지 요청. 실행 금지 상태: 기준 이미지 승인·경로·해시 미확정, 콘텐츠 검토 대기. 먼저 REFERENCE_PROMPTS.md로 참조 후보를 준비하고 승인한 뒤 실제 manifest에 경로와 해시를 기록. 기존 batch-export는 미승인 참조를 차단한다. 아래 draft JSON은 수동 검토용이며 실행용 패키지가 아님. 이후 공식 exporter로 다시 출력. 파일명·scene ID·revision·비율을 유지하고 결과는 자동 승인하지 않음.

| 작업 | 장면 | 참조 | 파일 |
|---|---|---|---|
| J01 | S06 | LOC-B, CHAR-A, CHAR-B, OBJ-A | S06_take01.png |
| J02 | S08 | LOC-A, CHAR-A, OBJ-A | S08_take01.png |
