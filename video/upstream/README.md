# V02 원본 보존 경로

원본 ZIP SHA-256: d4fcd9f11703c756d8566f66e56866dc3f06c8f019ef7c5d1885df9a7b3e2483. 43,185 bytes. 26개 파일(매니페스트 포함), 대상 25/25 SHA-256 및 크기 일치. 실제 ZIP으로 로컬 이식 및 재조회 검증 완료. GitHub에는 원본 14/26 파일(매니페스트 포함)을 바이트 동일성 검증 후 등록했다. 남은 12개 원본은 ZIP에 보존되어 있고 GitHub 등록 대기. 현재 로컬 환경의 직접 git 네트워크 연결은 DNS 해석 실패. 아래 명령으로 원본을 변형 없이 이식한다(Python 3.9+).

```sh
python3 video/scripts/import_upstream.py /path/to/incident-video-starter-20261030-v02.zip --repo .
git add video/upstream/incident-video-starter-20261030-v02
git commit -m "Preserve verified upstream V02 snapshot"
git push origin main
```

확장 구현은 video/ 아래 별도 경로에서만 수행한다. 원본의 자격증명은 제외되어 있으며 .env.example은 빈 값. 원본 워크플로의 9:16 및 6초 고정값은 확장본에서 기본값으로만 취급한다. 본 이식 절차는 원본 실행이나 생성 API 호출을 하지 않는다.
