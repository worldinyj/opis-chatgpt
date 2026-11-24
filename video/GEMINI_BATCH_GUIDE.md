# MEDIA-005 Gemini Tasks 외부 배치 제작 MVP

사용자가 Gemini Tasks에서 실행하는 외부 작업에 대한 입출력 계약이다. Gemini 연결/API/실제 지원 옵션은 확인하지 않았으며 서비스 호출이나 유료 생성을 하지 않는다. JSON을 외부 작업에 전달할 수 있는 제작 명세로 사용한다.

## 1. 내보내기
```sh
m=cases/2025/250919W2/media/safety_culture_learning/production.json
python3 video/scripts/media_v2.py batch-export "$m" /tmp/gemini-batch --root "$(dirname "$m")"
```
GEMINI_TASKS_BATCH 장면만 선택. 이미지 또는 I2V 요청 종류, 프롬프트, 장면·작업 ID, 시도, 화면비, 파일명, manifest revision 기록. CONTROLLED_GRAPHIC은 배치 금지. 실제 참조가 있는 경우 승인·파일 존재·SHA-256 확인. 결과물 batch_job.json 및 reference_inventory.json은 참조 파일의 명세이며, 실제 참조 파일을 복사하거나 서비스에 업로드하지 않는다.

## 2. 외부 작업 지시
사용자 실행 시 batch_job.json, 참조 목록, 실제 승인 참조 이미지를 외부 작업에 제공. 각 작업의 장면 ID/종횡비/개념 일러스트 조건을 유지하며 생성 글자 대신 후반 편집을 사용한다. 영상 생성 기능을 지원하지 않으면 이미지 생성으로 전환하되 manifest와 job revision을 갱신한다. 결과 파일명은 expected_filename에 맞춘다. API나 UI의 특정 기능이 지원된다고 가정하지 않는다. 수동 실행 전 상세 시각 brief/대본/참조를 준비하고 내용을 검토한다.

## 3. 수입
```sh
python3 video/scripts/media_v2.py batch-import "$m" /tmp/batch_import.json --batch /tmp/gemini-batch/batch_job.json --root /path/to/results
```
사건/산출물/manifest revision/비율, 장면/작업 ID 및 경로 경계 확인. 이미지 무결성·비율 또는 영상 실제 해상도/fps/길이와 SHA-256 검사. 파일 없으면 PENDING, 기술적 불합격 REJECTED. 정상 파일은 경로와 해시를 기록하되 PENDING 유지. 기술 합격은 시각 승인 아님. 사람이 실제 자산을 보고 결과·검수 상태·시도 이력을 기록한 후 MEDIA-003 validateBatch 등으로 재검증. 기존 결과 파일을 덮어쓰지 말고 수정 배치는 별도 폴더/manifest revision 또는 새 attempt로 관리. 자동 재시도 및 실제 서비스 전송은 후속 개발.

## 4. 제작 이후
STILL_MOTION: 승인 이미지 → 느린 줌/팬 → 후반 오버레이. I2V: 승인 영상 → 규격 확인 → 편집. HYBRID: 승인 자산 + 통제형 요소. 외부 결과에 있는 원본 사실, 교육 해석, 가상 장면, 캐릭터 일관성, 가독성을 사람이 검토한다.
