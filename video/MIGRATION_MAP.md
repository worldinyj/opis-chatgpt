# V02 → OPIS v2 이식 매핑

| 원본 항목 | v2 확장 위치 | 유지/변경 |
|---|---|---|
| WORKFLOW / START_HERE / AGENTS | AGENTS, CONTRACT, PRODUCTION_PROFILES | 원본 고정·사실 대조·자산 승인·실제 결과 검수 유지; 모드별 가변 규격 |
| source / fact_ledger.md | fact_ledger.schema.json | 사실·조사 판단·평가·원본 한계, 인쇄/PDF 페이지 분리 |
| production.json spec/timing/cards/clips | production.schema.json scenes/profile/timing | 인트로/본편/아웃트로 통합; 구간별 길이와 경계 overlap |
| references, appearance, location_id | references / scene reference_ids / visual_brief | 참조 파일·해시·승인과 장소·연속성; 세부 시각 프롬프트는 MEDIA-006 |
| input_mode / frames / previous_end | input_mode / attempts / references | I2V 입력 지원 확인; 3컷은 설계·QC 목표; 정지형엔 강제 금지 |
| attempts / accepted_revision / actual_seconds | attempts / accepted_take | revision·take·실제 길이·해시·반려 기록 유지 |
| edit_overlay / cards.narration / learning_log | scene overlay/narration / review template | 통제형 텍스트, 음성 별도, 개선 기록 |
| 기존 제작 스크립트 | 원본 보존 경로 + 신규 scripts | 원본 기능 변경 금지; 실제 렌더링·음성·프롬프트 빌드는 MEDIA-004 |
| 신규 안전문화 학습 원장 | learning_ledger.schema.json | 40속성 분석, 10원칙 중심 전달, 1장 전체 후보 속성 카드 |
| Gemini Tasks / PPT / 숏폼 | batch_job, ppt, production, discussion_action | 외부 작업 패키지와 편집 가능한 PPT, 독립 제작 유형 |

보존 대상은 실제 ZIP 26파일이며 원본 전체의 GitHub 등록은 대기. 기존 패키지의 fixed and stable, 단일 장소·동작, 실제 승인 참조, 실제 영상 끝 프레임 사용, 가려진 정보 비추정, 음성 시간 검수, 통제형 편집, 시도 기록은 유지한다. 현장 설비/작업 재현이 아닌 안전문화 교육용 개념 표현에 적용한다. 원본과 새 계약의 자동 변환은 후속 작업이다.
