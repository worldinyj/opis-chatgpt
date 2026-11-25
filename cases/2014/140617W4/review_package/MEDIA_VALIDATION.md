# 영상 3종 설계 검증

영상 3종은 설계 초안만 등록. 표준 JSON 스키마의 사용 키워드를 구현한 JS 검사 및 원장/시간/배치 참조 자체 검사 10개 통과(정식 Python/jsonschema 전수 14개 계약 검사는 최종 단계 대기). 음성 실측, 에셋 생성, PPTX, A4 및 전문가·독립 검토 미수행.

| 검사 | 결과 |
|---|---|
| schema incident_understanding/production.json | PASS |
| relations incident_understanding/production.json | PASS |
| schema safety_culture_learning/production.json | PASS |
| relations safety_culture_learning/production.json | PASS |
| schema shorts/SHORT-01/production.json | PASS |
| relations shorts/SHORT-01/production.json | PASS |
| schema safety_culture_learning/batch_job.example.json | PASS |
| batch safety_culture_learning/batch_job.example.json | PASS |
| schema shorts/SHORT-01/batch_job.example.json | PASS |
| batch shorts/SHORT-01/batch_job.example.json | PASS |

전체 43장면 270초. IU F01–F17 전체 포함, SC L01–L03 및 핵심 5속성 18초 카드, SHORT L02 집중. 실제 영상·음성 생성·외부 제출·유료 호출 0. can_ship=false.
