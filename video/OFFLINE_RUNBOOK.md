# MEDIA-004 오프라인 제작 도구 v0.4

## 환경
Python 3.9 이상, Pillow, FFmpeg/FFprobe(libx264), Node.js(MEDIA-003 계약 검증), 한글 폰트 파일. macOS에서 brew install ffmpeg, Python 가상환경에서 pip install Pillow를 필요에 따라 실행. 폰트는 사용권이 확인된 로컬 폰트를 명시. 테스트는 Linux의 NanumGothic 고정 경로를 사용했으므로 macOS 테스트에서는 그 경로를 환경에 맞게 수정한다. API 키는 필요 없다.

## 사용 순서
저장소 루트에서 다음 명령. m은 첫 사건 교육영상의 기획 manifest이다. 실행용 대본 및 자산은 아직 준비되지 않았다.

```sh
m=cases/2025/250919W2/media/safety_culture_learning/production.json
node video/tests/validate_pilot.mjs
python3 video/scripts/media_v2.py build "$m" /tmp/opis-build
python3 video/scripts/media_v2.py card "$m" /tmp/summary.png --groups cases/2025/250919W2/media/safety_culture_learning/attribute_summary.json --font /path/to/KoreanFont.ttf
python3 video/scripts/media_v2.py render-still "$m" /tmp/S02.mp4 --scene S02 --image /path/to/approved.png
python3 video/scripts/media_v2.py voice-plan "$m" /tmp/voice_plan.json --root /path/to/wav
python3 video/scripts/media_v2.py assemble "$m" /tmp/output.mp4 --root /path/to/clips --audio /path/to/wav
python3 video/scripts/media_v2.py probe "$m" /tmp/output.mp4
```

build는 STORYBOARD.md, NARRATION.md, IMAGE_PROMPTS.md, I2V_PROMPTS.md, timeline.json을 생성. 대본이 없으면 NOT WRITTEN 표시. I2V 프롬프트는 I2V 구간만 출력. 자동 생성 프롬프트는 구간의 시각 brief에 의존하며 세부 제작 프롬프트 및 3컷 검수 설계는 MEDIA-006에서 구체화한다.

card는 지정된 JSON 그룹의 한글 문구를 PNG로 통제형 렌더링하며 화면을 벗어나는 텍스트는 거부. 원칙별 12속성 시범 데이터는 분석 초안에서 가져왔다. 카드 PNG를 영상으로 만들려면 정지 이미지 렌더러에 사용(고정 스케일 1). 실제 화면의 폰트·읽는 시간·초안 표기는 인간 검토.

render-still: 줌인/줌아웃/팬, 1~2배, FFmpeg zoompan. 영상 원본 오디오 없음. 입력은 반드시 승인 이미지와 선택된 출력비율에 맞는 안전 프레이밍. 현재 중앙 크롭을 사용하므로 중요한 부분이 잘리지 않는지 확인한다.

voice-plan: scene ID별 WAV를 확인해 실제 길이, 타임라인 시작, SHA-256을 기록. 내용이 있는 구간에 WAV 누락 시 차단, 구간을 넘는 음성 차단. 실제 한국어 TTS는 호출하지 않는다.

assemble: 모든 장면의 ID.mp4 및 선택 WAV를 입력, 목표 규격과 구간 길이를 확인하고 하드컷으로 연결, WAV를 타임라인에 배치. 겹침 전환은 계산하되 실제 합성은 명시적으로 거부. BGM, 자막 자동 합성, 영상 승인, v1 자동 마이그레이션은 미구현. 빈 narration의 음성은 생략 가능; 초안 완성이나 교육 승인으로 해석하지 않는다. 실제 산출물/시험 미디어는 저장소에 넣지 않는다.

## 테스트
```sh
PYTHONPATH=video/scripts python3 video/tests/test_media_v2.py
```
오프라인 검증 기록: [MEDIA004_005_RESULTS](tests/MEDIA004_005_RESULTS.md). 
