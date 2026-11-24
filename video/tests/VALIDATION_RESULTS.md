# MEDIA-003 계약 검증 기록 (2026-11-24)

실제 커밋에 사용할 객체와 동일한 검증 함수로 JavaScript 실행환경에서 검증하였다. 26/26 PASS(정상 형식/관계, 오류 차단 포함). 이는 원본 사실 독립검토, JSON Schema 전체 사양 준수 시험, Node CLI 실행, 실제 자산/음성/미디어 제작 테스트 또는 전문가 승인이 아니다. Node runner는 후속 로컬 재현용으로 제공한다.

| 검사 | 결과 |
|---|---|
| OPIS production manifest v2 SC-250919W2 | PASS |
| OPIS production manifest v2 IU-250919W2 | PASS |
| OPIS production manifest v2 SM-250919W2-01 | PASS |
| Editable classroom PPT manifest PPT-250919W2 | PASS |
| Discussion and action manifest DA-250919W2 | PASS |
| Fact ledger v2 250919W2 | PASS |
| Learning ledger v2 250919W2 | PASS |
| External batch job contract SC-250919W2 | PASS |
| SC-250919W2 relations | PASS |
| IU-250919W2 relations | PASS |
| SM-250919W2-01 relations | PASS |
| PPT-250919W2 relations | PASS |
| DA-250919W2 relations | PASS |
| batch relations | PASS |
| reject bad attribute | PASS |
| reject timing | PASS |
| reject missing summary | PASS |
| reject wrong ratio | PASS |
| reject premature approval | PASS |
| reject missing fact | PASS |
| reject incomplete summary | PASS |
| reject duplicate scene | PASS |
| reject invalid overlap | PASS |
| reject stale accepted take | PASS |
| reject unsupported input mode | PASS |
| reject unreviewed batch result | PASS |
