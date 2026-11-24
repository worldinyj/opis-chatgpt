# 기존 사건 이해 영상 체계 이식 기록

원본: incident-video-starter-20261030-v02.zip, 2026-10-30, 26파일(매니페스트 포함). ZIP SHA-256: d4fcd9f11703c756d8566f66e56866dc3f06c8f019ef7c5d1885df9a7b3e2483. 원본은 이번 문서 검토에 사용했으며 저장소로 전체 이식하지 않았다.

| 원본 | 이식/확장 방향 |
|---|---|
| AGENTS.md / WORKFLOW.md / START_HERE.md / STATE.json | 작업 단계와 재개/정지, 원본 사실, 자산 승인·버전·검수, 실제 생성 확인 |
| LESSONS_LEARNED.md | 브릭 연속성, 단일 시작 이미지, 실제 지원 키프레임, 통제형 편집, 나레이션 길이, 비가시 현상 과장 금지 |
| docs/style_guide.md / production_schema.md / project_review.md | 화면비별 레이아웃, manifest v2, 유형별 사실·교육 검토 |
| scripts/production.py | 기존 버전 보존; 경로/사양/타임라인/모드별 check 개선 |
| scripts/generate_elevenlabs_vo.py / assemble_voiceover.py / doctor.py | 실제 구간 manifest, 선행 여백, 합성 검증, 환경 탐지 |
| templates/* | 사건 폴더 연계; 사실 원장과 학습 원장 분리, 프롬프트/스토리보드/편집/학습 로그 |
| .env.example / requirements.txt | 비밀값 제외, 환경별 의존성 확인 |

원본 WORKFLOW는 480p/9:16/6초 I2V, 실제 지원되는 입력 모드(단일 시작/시작·끝/3키프레임), 3컷 독립 생성, 실제 끝 프레임 기반 연속성, 인트로/아웃트로 통제형 편집을 명시. 원본 템플릿 목표 150초. 기존 규칙의 화면비 고정은 새 가변 프로필로 대체하며 익명화 지침은 영상 기본값으로 유지(사건 인덱스·출처는 원래 명칭). 실제 발전소명 표시가 필요한 경우 교육 목적과 정책에 맞춰 별도 설정. 원본의 고정 길이 및 3컷 강제 검증은 제작 모드별로 일반화. 모든 콘텐츠 유형에 적용할 수 있도록 설계. 생성 도구/서비스 실측 및 코드 테스트는 후속 작업.
