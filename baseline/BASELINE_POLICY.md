# ChatGPT 분석 기준선 동결 정책 V1

## 기준선
- 기준 커밋: 859512721debe4f5441accec97c8aa64f030c1fd
- Phase 3-E 검증 커밋: 9cab7d2d84143b335f601c28c9550d09cd504a05
- 38건 / 40속성 / 1520행 / D 173, I 80, A 717, H 40, P 4, N 506.
- 미진 후보 253, 판단보류 717, 미선정 550. 확정 및 전문가 승인 아님.
- GitHub compare로 Phase 3-E 이후 10개 변경 파일 확인. 기존 cases/와 당시 표준·분석 인덱스 변경 없음.
- 기준선은 Git 커밋의 전체 cases/ 트리, manifest에 명시된 11개 기준 파일과 38개 전문가 검토 패키지의 blob으로 식별한다. 각 보고서·원장·교육자료의 독립 해시 목록은 이번 원격 작업에서 새로 수집하지 않았으며, 검증기가 로컬 Git 트리에서 직접 읽는다.
- [manifest](CHATGPT_BASELINE_V1.json), [long-format CSV](CHATGPT_BASELINE_V1.csv).

## 독립성 보호
Gemini/Claude 폴더는 본 기준선 검증의 보호 범위 밖이며, 각 모델 작업을 읽거나 수정하지 않는다. 외부 모델에는 중립 큐/표준/공통 프롬프트/스키마/원본만 제공하고 baseline/ 및 기존 분석자료를 제공하지 않는다. 폴더 분리는 권한 통제가 아니므로 독립 작업환경을 유지한다.
기존 cases/ 및 지정 기준 파일의 추가·삭제·변경은 금지. 후속 검증기/DB/분석/교육 디자인 작업은 별도 경로에 작성. 분석 판단 재분류는 3AI 독립 제출 및 전문가 처리 이후 별도 버전으로만 수행. 기준선 CSV는 원래 매트릭스의 역할을 재표현한 것이며 신규 원문 재판독 결과 아님.

## 검증기
저장소 전체 이력이 있는 로컬 clone의 루트에서:
```bash
python scripts/verify_baseline.py
```
특정 커밋 또는 원격 추적 브랜치 검사:
```bash
git fetch origin
python scripts/verify_baseline.py --ref origin/main --committed-only
```
테스트:
```bash
PYTHONPATH=scripts python -m unittest discover -s tests -p test_verify_baseline.py -v
```
Windows PowerShell: 먼저 `$env:PYTHONPATH="scripts"` 설정 후 동일 unittest 명령 실행.
검증은 읽기 전용. exit 0 PASS, 1 FAIL(변경/불일치), 2 ERROR(입력/Git 오류). 보호 트리의 기준 커밋 및 대상 커밋 비교, 지정 blob 검증, baseline CSV의 원래 매트릭스와 일치 확인, 기본적으로 현재 작업트리의 보호 경로 변경 및 일반 비추적 파일 탐지. --committed-only는 작업트리 검사 제외. Git에서 무시된 비추적 파일과 기준선 manifest 자체의 변조는 이 검증기만으로 보증하지 않음. 신뢰하는 manifest를 별도로 보존하고 --manifest로 지정 가능. 실제 원본 PDF 동일성, 분석 의미 타당성, 외부 AI 분석의 독립성, 출판 승인을 판정하지 않는다.
이번 개발은 임시 로컬 Git 저장소의 가상 테스트 8/8 통과. 실제 전체 저장소 clone에서 스크립트 실행은 미실시. 원격 비교 및 CSV 구조 검증은 별도로 수행.
GitHub 브랜치 보호/CI/자동 실행 설정 변경 없음. 동결은 기준 커밋 및 검증 정책이며 물리적 쓰기 금지가 아니다. 변경 감지 시 수동 조사; 자동 복구·강제 push 금지.

approved=false / can_ship=false
