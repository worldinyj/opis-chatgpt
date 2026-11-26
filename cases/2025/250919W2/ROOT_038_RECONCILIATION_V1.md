# ROOT-038 기존 산출물 인계 및 정합성 검증 V1

2026-11-26. 기존 V0.1.1 분석자료가 이미 존재함을 main 직접 조회로 확인했다. 신규 등록 메모 ROOT_038_INTAKE_V1.md는 누락 확인을 위한 임시 작업 기록으로 보존하되 정규 사실/교훈 ID 및 후보 분류의 기준으로 사용하지 않는다. 기존 V0.1.1을 통합 기준으로 유지하며 새 예비 의견은 전문가 검토 시에만 비교한다. 기존 파일 수정 없음.

## 확인된 기준
- report.md: blob 9f8e9df47bb32efdf5ec58248d26e5b3e7ded5ed
- metadata.yaml: blob bb90e76120145aa0b0e0f451d92c4500d833f027
- source.md: blob b856e6d5e286f58f31f26752ef71358190c0ce07
- media/fact_ledger.json: blob 73f31a815e836b58e78808ba7655edcde947937d
- media/learning_ledger.json: blob a8aa61b8c35a367e3a8d33d3bde443ec8cd5c492
- ROOT_038_INTAKE_V1.md: blob fb46c2bdc09fb6c229a147dc4dddbd57a01014c6

## 검증
- all_40: PASS
- core_match: PASS
- additional_match: PASS
- fact_ids_unique: PASS
- learning_ids_unique: PASS
- learning_fact_refs: PASS
- learning_attribute_refs: PASS
- all_core_in_lessons: PASS
- page_mapping: PASS
- hash_record_consistency: PASS
- no_approval: PASS
- cause_refs_in_report: PASS

40속성: 핵심 12, 추가 12, 기타 16; 사실 12, 교훈 3. 핵심은 교육용 후보이며 직접·간접 미진 역할로 확정하지 않는다.

임시 등록안과 기존 핵심 후보의 차이: QA2는 기존 핵심 유지, LA5는 기존 추가검토 유지. 임시안의 F01–F15/L01–L05와 기존 F01–F12/L01–L03은 동일 ID라도 의미가 다를 수 있으므로 혼용 금지. 기존 원장은 파생 콘텐츠 연결의 기준이다. 추가 세분화는 기존 ID를 유지한 별도 개정과 검증을 통해서만 진행한다.

## 남은 범위
- 기존 기록의 PDF 40쪽 및 SHA-256 fb3348d2725396a03689556b717876d8d65c72a79dce6716ae1d8471fe6cec83은 파일간 일치 확인; 새 Drive 파일의 바이너리 동일성이나 페이지 이미지 재검증은 미실시.
- 원본 p.11 작업 날짜 불일치 유지. 최종 INES 및 발행 후 대책 이행 미확인.
- ROOT 37건 통합 인덱스 누락 원인 및 기존 교육 산출물 확인, 40속성 역할 정규화 및 전문가 패키지, 전체 인덱스 갱신 필요.
- 구조 검증은 전문가 의미 검토와 다름. can_ship=false, approved_attributes=[], expert_status=PENDING.
