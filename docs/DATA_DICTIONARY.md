# 데이터 사전

| 필드 | 의미 |
|---|---|
| event_id | 공식 사건 식별번호, 없으면 별도 내부 ID |
| report_number | 조사보고서 번호 |
| event_date / report_date | 발생일 / 원본 발행일 ISO 8601 |
| opis_popup_id | 목록 상세 팝업 인수(원본 사건번호와 별개) |
| preliminary_ines / final_ines | 잠정/최종 등급, 미확인은 null |
| analysis.status | REGISTERED, DRAFT, QC_PASSED, HUMAN_REVIEWED, APPROVED, PUBLISHED |
| candidate_attributes | 교육용 AI 후보 속성, 승인 전 통계 분리 |
| approved_attributes | 승인된 속성만, 미승인 시 빈 배열 |
| source.document_url | 직접 파일 링크, 미확인 null |

연도는 사건 발생연도. 사건×속성 통계는 동일 사건에서 동일 코드를 한 번만 센다. 원인×속성 관계는 별도 집계한다.
