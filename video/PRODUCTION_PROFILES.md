# 가변 제작 프로필 및 입출력 계약 (설계)

## 출력
| 항목 | 기본/선택 |
|---|---|
| 비율 | 9:16 모바일 / 16:9 집합교육, 각각 독립 출력 |
| 예시 해상도 | 480×854 / 854×480 (480급); 720×1280 / 1280×720; 실제 지원 확인 |
| 길이 | 사건 이해 120~150초, 안전문화 약120초, 숏폼 30초 기본. 구간 가변 |
| 음성 | 한국어 별도 트랙, BGM 별도 |
| 프레임률 | 실제 제작 및 납품 기준 기록 |

## 장면 모드
| render_mode | 입력 및 결과 | 필수 검수 |
|---|---|---|
| I2V | 기준 이미지 + 지원 입력모드 + 영상 | 3컷 설계/검수 목표, 구조·동작·실제 길이 |
| STILL_MOTION | 승인 정지 이미지 + 시작/끝 크롭·줌·팬 | 잘림/불필요 흔들림/가독성/실제 길이 |
| CONTROLLED_GRAPHIC | 편집 가능한 텍스트·도형·이미지 | 원본 수치/코드/문구, 읽는 시간 |
| HYBRID | 위 자산과 통제형 레이어 | 레이어별 검수 및 최종 합성 |

경로는 별도 필드 generation_route = INDIVIDUAL / GEMINI_TASKS_BATCH / LOCAL_EDIT. 배치도 개별 결과 승인 필수. 비율 전환은 자산 재생성 또는 안전한 재프레이밍; 실제 지원 확인.

## Gemini Tasks (외부 작업 방식)
입력: job ID, 사건·산출물 ID, manifest revision, 목적, aspect_ratio, 각 scene ID와 독립 프롬프트, 참조 파일/해시, 요청 종류(이미지 또는 지원되는 영상), 목표 규격, 결과 파일명 규칙, 금지 사항. 출력: scene ID, 실제 생성 파일/해시, 도구·설정, 시도/실패 사유, 검토 상태. 일괄 실행을 허용하되 실패를 자동 승인하거나 파일명만으로 일치 판단하지 않는다. 미지원 영상 기능은 이미지 제작과 후반 슬로우 줌/편집으로 대체 가능. API 직접 연동은 미확정.

## manifest 설계 필드
event_id, artifact_id, type, source_version, analysis_version, revision, profile(width,height,aspect_ratio,fps), timing(target_seconds,overlap), scenes(id, duration_seconds, scene_type, fact_ids, learning_ids, principle_codes, attribute_codes, render_mode, generation_route, refs, narration, overlay, transition, actual_seconds, review_status), approvals, attempts. 가변 구간은 절대 타임라인으로 계산하고 겹침 전환 반영. 상세 JSON Schema와 검증 구현은 MEDIA-003~004에서 수행.

## 구현 계약
[JSON Schema 및 교차검증 계약](CONTRACT.md)으로 확정. 실제 미디어 생성/합성은 MEDIA-004 이후. 예제의 scene은 학습 구간으로 6초 I2V 클립 분할은 제작 설계 단계에서 수행한다.
