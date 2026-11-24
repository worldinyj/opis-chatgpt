# MEDIA-004~005 오프라인 실행 검증 (2026-11-24)

Python 3.13.5 / FFmpeg 7.1.5 / Pillow 12.3.0 / Linux. 실제 Python unittest 9/9 PASS (1.689초). 생성형 API·Gemini·ElevenLabs 호출 0. 테스트는 합성 단색 이미지 및 테스트 WAV(사인파), 한국어 속성 카드에 한정한다. 사건 영상이나 교육 승인 결과가 아니다.

| 테스트 | 결과 |
|---|---|
| batch_export/import: 누락·정상 이미지·잘못된 화면비 | PASS |
| build: 스토리보드·프롬프트·미작성 음성 표시 | PASS |
| 16:9/9:16 한글 6그룹·12속성 카드 PNG 렌더링 | PASS |
| 잘못된 overlap 차단 | PASS |
| 배치 파일 경로 이탈 차단 | PASS |
| 가로/세로 2개 장면 렌더·줌인/줌아웃·팬 필터 실행·WAV 합성·FFprobe | PASS |
| stale batch 차단 | PASS |
| 가변 타임라인 overlap 계산 | PASS |
| WAV 길이 초과 차단 | PASS |

실제 영상 테스트: 320×180, 180×320, 24fps, 각 2초, AAC 음성 스트림 확인. 카드 테스트: 1280×720, 720×1280. 단색 테스트 이미지이므로 모션 필터 실행/기술 규격 확인이며 실제 시각적 줌 효과·프레이밍의 인간 QC는 아님. 테스트 카드 확인 과정에서 파일 핸들 미종료 ResourceWarning 1회(검사는 통과). 실제 내용/가독성 검수, BGM, overlap 합성, 참조 파일 묶음, TTS, 실서비스 및 실제 첫 사건 렌더는 미수행.

로컬 실행 소스 SHA-256: c64acbef7398e62aa731b4d5302052b1914f320070274aa48f261fbd9caba0da. Git blob: 94ef8431e86b9538f1d5efd0cd2c3d678f4d0251.
테스트 SHA-256: 852252d4b5d747e93dd88185df50714a32a4980aa7a34fe41caedf4df86a92c3. Git blob: aeccf6c1e24bb702c7de8c9c4b4820d88443f172.
GitHub create_blob 반환값은 로컬 파일 계산값과 일치. 기존 MEDIA-003 검증 기록은 별도 보존.
