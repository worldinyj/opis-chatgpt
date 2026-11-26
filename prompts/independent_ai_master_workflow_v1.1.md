# OPIS Gemini / Claude 자동 독립 분석 작업관리 V1.1

## 1. 자동 대상 결정
프로젝트 worldinyj/opis-chatgpt, main. 현재 실행 중인 제공자를 확인하여 GEMINI 또는 CLAUDE로 설정한다(모델 버전 모르면 null). 입력으로 사용자 제공 원본 PDF 폴더 또는 로컬 원본 파일 디렉토리를 사용한다. 공통 입력은 index/independent_source_queue_v1.json, prompts/independent_ai_review_v1.0.md, standards/safety_culture_40.json, standards/independent_ai_review_v1.schema.json. 전체 repo를 탐색하거나 다른 모델의 판정을 읽지 않는다. 중립 큐의 order 및 cases가 작업 대상의 유일한 기준이다. 이 큐로 QUEUE_ID, EVENT_ID, EVENT_YEAR를 자동 결정한다. 기존 자리표시자는 입력 요구 사유가 아니다. 순서는 ROOT-038, ROOT-005, 나머지 관리번호 오름차순.

## 2. 진행 상태 복구
자기 모델 폴더 gemini/ 또는 claude/ 및 자기 모델의 체크포인트, 현재 대화에서 실제 생성한 파일만 확인한다. 완료 메시지만으로 저장 완료를 간주하지 않는다. 상태는 NOT_STARTED, IN_PROGRESS, EXPORTED_PENDING_UPLOAD, STORED, BLOCKED_SOURCE, BLOCKED_VALIDATION으로 구분한다. 기존 4개 산출물이 실제 존재하고 정합하면 STORED. 기존 3개 산출물이 있으면 재분석하지 말고 validation.md 보완 후 확인한다. 저장 전 실제 4개 파일/ZIP을 사용자에게 제공한 경우 EXPORTED_PENDING_UPLOAD이며 재생성하지 않는다. ROOT-038의 기존 Gemini 결과를 확인 가능하면 보존하고 validation.md/ZIP 반환 후 다음 미완료 사건으로 전환. Claude는 Gemini의 완료 상태를 승계하지 않는다. 새로운 세션에서 상태가 불확실하면 저장소의 자기 경로 및 사용자 제공 체크포인트를 먼저 확인한다. 기록을 확인할 수 없으면 미확인 상태를 명시하며 덮어쓰지 않는다.

## 3. 원본 자동 탐색
선택된 사건의 drive_filename_hint, expected_size_bytes, report_number, event_id, expected_pdf_pages, expected_sha256로 사용자 제공 폴더/로컬 원본을 검색한다. NFC 정규화, 공백/밑줄 차이 허용. 날짜·파일명만으로 확정하지 않는다. PDF를 직접 읽어 표지/본문의 식별 정보 및 페이지 수 확인. 실제 바이트 접근 가능 시 SHA-256 대조. 다르면 BLOCKED_SOURCE, 다른 후보를 검색하되 다른 사건으로 대체하지 않는다. 해시 계산 불가면 실제 읽은 원문을 근거로 PDF_READ_HASH_UNAVAILABLE 및 한계 기록, 제출은 가능하나 통합 시 판본 확인 대기. ROOT-024/025는 파일명이 비슷하므로 큐의 다른 크기/해시/사건 번호로 구별. 동일 파일을 중복 처리하지 않는다. 파일 접근 실패, 다중 후보 해소 실패, 판본 불일치는 해당 사건만 기록·건너뛰고 다음 미완료 사건을 시도한다. 전체 공통 입력 또는 원본 폴더 자체 접근 불가 시에만 구체적인 접근 제한을 설명하고 필요한 파일/권한 요청.

## 4. 실행
원본 PDF, 중립 큐의 해당 사건 정보, 공통 프롬프트 V1.0, 표준 JSON, 출력 스키마만으로 분석한다. 독립 40행 양식이 없어도 표준의 40개 코드로 직접 만들 수 있다. 다른 AI 결과는 열람 금지. 기존 V1.1 산출물 관리 절차(6장 report.md, review.json, excel_import.csv, validation.md)를 적용한다. D/I→선정, A→판단보류, H/P/N→미선정. 40개 코드 모두 판단 및 원문 근거·한계. JSON은 기존 schema의 prompt_version=1.0 유지; 본 문서는 작업관리 규칙이다. 실제 설비 조작/상세 우회 방식, 비공개 정보 재현 금지. 원문 근거 없는 추정 금지. CSV 헤더 review_key,queue_id,event_id,attribute_code,review_result,rationale,source. 실제 40행, JSON과 일치. 정식 스키마와 교차검증을 실제 실행한 범위만 보고하며 미실행은 NOT_EXECUTED. approved=false, can_ship=false.

## 5. 저장
<자기모델>/cases/<연도>/<event_id>/v1/ 아래 report.md, review.json, excel_import.csv, validation.md. 기존 파일과 충돌하면 동일성 확인, 임의 덮어쓰기 금지. GitHub 쓰기 권한이 실제 있을 때 해당 모델 경로만 저장하고 재조회 및 commit SHA 보고. 쓰기 불가면 해당 구조를 담은 MODEL_ROOT-xxx_EVENTID_v1.zip 또는 4개 실제 파일 제공. 저장 상태와 파일 제공 상태 구분. 원본 PDF, 다른 AI 분석, 비공개 주소/토큰을 공개 저장소에 복사하지 않는다. 통합 Excel, 기존 cases, 다른 모델, 공통 표준 수정 금지.

## 6. 체크포인트 및 다음 실행
자기 모델의 progress.json(또는 다운로드 파일)에는 모델, queue_id, event_id, 상태, 산출물 경로, 실제 GitHub commit SHA 또는 ZIP명, 확인 가능한 검사 결과/제약만 기록. 취약 후보 및 타 모델 결과는 포함하지 않는다. 사건마다 파일 생성 및 체크포인트 기록 후 순서대로 다음 실행. 현재 환경의 한 응답에서 실제 처리 가능한 사건만 진행한다. 기본 1건씩 완결하며, 에이전트 환경에서 여러 건 순차 실행 가능하면 중간 사용자 승인 요구 없이 반복한다. 시스템/권한/시간 제한은 준수하며 백그라운드 작업을 주장하지 않는다. 종료 시 분석완료(저장/반환 구분), 미완료, 차단, 다음 처리 사건을 출력. 사용자가 '다음', '계속', '이어 진행'이라고 하면 이 절차를 처음부터 복구하여 다음 미완료 사건을 실제 분석한다. 대상 정보 자리표시자 때문에 STOP_INPUT_REQUIRED를 내지 않는다. 전체 대상이 완료되면 ALL_ANALYSES_COMPLETED 또는 ALL_AVAILABLE_EXPORTED로 구분하며 차단 사건이 있으면 PARTIAL_BLOCKED로 보고한다.
