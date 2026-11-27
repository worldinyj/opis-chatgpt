# C09-F4 / C06-R1 로컬 실행환경 및 통합시험 V1
2026-11-27. 기준 개발 ref 6aecf146a077774290e05d07b2a69155bc651dc7. 합성 시험 전용. 실제 자료 적재/승인/배포 금지.
## 1. 구성
integration_platform/local/에 run_local_suite.py, test_local_runner.py, test_full_restore.py, local_settings.py, local_urls.py, local_web.py, test_django_core.py, requirements-local.txt, templates/registration/login.html 추가. 9개 로컬 작성 파일의 git hash-object와 저장 후 tree blob 9/9 동일. 기존 개발 코드 수정 없음.
실행기: 기준 개발 commit ancestor, 기존 Python/HTML/C01 contract의 정확한 Git blob, 시험 파일의 HEAD 일치, C01 reference 8개 고정 ref의 원시 Git bytes/hash 검사. OPIS_CONTRACT_FIXTURE 및 외부 Django 설정 제거, 명시적 PYTHONPATH, 독립 프로세스, 300초 제한, 저장소 외부 신규 보고서 디렉터리. 20개 묶음, 기존 C 214개 시험 + 신규 미실행 full restore 1개 및 Django HTTP 6개 = 예상 221개. B03 17개는 별도 branch이므로 제외. C02 61개는 R2 진입점에서 base/R1/R2 한 번만 실행. 반환 코드/시험 개수/skip 검증; 차단·실패·timeout은 비정상 종료, 로그와 report.json 생성. 실행기 자체 시험 7개는 별도로 실행. 모든 합성 시험 통과도 C10 승인 아님.
## 2. 신규 시험/웹 구성
test_full_restore: 실제 F1 38건 입력과 conflict, F2 봉인, C04 계산, archive verify, 파일 backup/reopen 후 78 archives/114 bindings/381 artifacts, 4560 reviews, 1520 결과, fingerprint/consensus/NOOP 대조. 아직 실행하지 못함.
local_web: 신규 저장소 외부 workspace만 초기화, 3 합성 사건/120 키, guarded core DB 및 Django auth DB 분리, 비밀키 생성, fixture:expert 암호 직접 입력(최소12자), READY_SYNTHETIC, 루프백 127.0.0.1:8000, 실제 자료 금지. 설정은 작업공간 없을 때 disabled, factory가 합성 사건 범위 검사. 로그인, QA 읽기/쓰기 제한, CSRF, 초안 개정 충돌, pending 차단, 기본 비활성화에 대한 Django 실제 Client 시험 6개 작성. Django 설치 및 HTTP/초기화/서버 실행은 미수행. 운영 인증/배포/경로 보안 인증으로 간주 금지.
## 3. 실제 실행 결과
Python 3.13.5; Git 직접 ls-remote DNS 실패; Django import spec 없음. 기존 C02/F1 전체 로컬 소스 없음. 신규 Python 7개 py_compile 성공, 실행기 orchestration tests 7/7 PASS(2.840초): failure, missing_dependency, preflight_reject, sanitize, skip, success, wrong_count. 실제 불완전 checkout 경로로 CLI 실행 결과 BLOCKED_PREFLIGHT 및 exit=1, report.json 확인. 유효한 전체 Git checkout 사전검증/전체 221시험/새 DB 복원/웹시험 실행은 미수행. 이전 231개 시험 기록을 재실행하지 않음. 누적 개별 시험 통과 기록 238개(신규 7). 신규 두 전체시험 파일의 7개 예상 시험은 미실행이므로 가산하지 않음.
## 4. 로컬 재현 (Windows PowerShell)
Python 3.12 및 Git 설치/저장소 읽기 권한 필요. 기존 작업폴더를 변경하지 않고 새 clone 사용. Git history 필요(--depth 금지), LF 유지.
```powershell
git clone --branch develop/integration-platform --config core.autocrlf=false https://github.com/worldinyj/opis-chatgpt.git opis-integration
cd opis-integration
py -3.12 -m venv "$HOME\opis-venv"
$py = "$HOME\opis-venv\Scripts\python.exe"
& $py -m pip install -r integration_platform/local/requirements-local.txt
& $py integration_platform/local/test_local_runner.py
& $py integration_platform/local/run_local_suite.py --report-dir "$HOME\opis-tests-001"
```
Mac/Linux: git clone 동일, python3.12 -m venv "$HOME/opis-venv"; "$HOME/opis-venv/bin/python" -m pip install -r integration_platform/local/requirements-local.txt; 동일 python으로 runner 실행 --report-dir "$HOME/opis-tests-001". 디렉터리 이름은 실행마다 신규로 변경.
기존 C07은 artifact_tool 의존성이 있는 환경에서만 실행; 일반 로컬 pip 설치 가능 여부 미확인이라 요구사항에 넣지 않았으며 미설치시 BLOCKED_DEPENDENCY, 전체 PASS 아님. Django/통계 패키지 버전 범위는 설치 후 검증 필요; lockfile 아님. Git clone/venv/pip 설치는 사용자 로컬에서 실행 필요.
웹 합성 데모(핵심 시험 로그 검토 후):
```powershell
& $py integration_platform/local/local_web.py init --workspace "$HOME\opis-web-fixture-001"
& $py integration_platform/local/local_web.py run --workspace "$HOME\opis-web-fixture-001"
```
브라우저 http://127.0.0.1:8000/ ; fixture:expert와 직접 설정한 암호. Ctrl+C 종료. workspace 및 report 디렉터리(비밀키/DB 포함)는 Git에 넣지 않음. 공용 네트워크 공개 금지. 실패 시 report.json과 해당 단계 log를 검토하되 비밀키/암호/실제 PDF 공유 금지.
## 5. 잔여 게이트
기존 수용표 3 scoped PASS/9 BLOCKED 그대로. 전체 checkout과 실제 runtime 시험 결과를 받아 수용 검증할 필요. 새 runner는 기존 파일 변경 시 의도적으로 차단하므로 수정 후 pin 재설정 및 검토 필요. Windows LF 변환 차단, 로컬 Git 및 패키지 인증/권한 필요. 전체 상태파일 내용 검증/실제 원본 bytes, eligibility 구현, archive-snapshot digest 연계, 실제 Excel 원본 및 C07 환경, 전문가 웹 인증·세부 사실대장, B 독립 QA 잔여. C10 실제 적재 승인 없음.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
