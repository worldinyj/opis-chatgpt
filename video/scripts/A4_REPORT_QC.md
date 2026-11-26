# Phase 2-C: A4 및 PPT 통합 QC

설치: 기존 계약/PPT 의존성에 아래 A4 의존성 및 시스템 Fontconfig, Pango/WeasyPrint 런타임, Noto Sans CJK KR Regular/Bold 필요. macOS에서도 해당 폰트와 fc-match를 먼저 확인한다. 폰트 파일은 저장소에 포함하지 않는다.

```sh
python -m pip install -r video/requirements-a4.txt
fc-match 'Noto Sans CJK KR'
python video/scripts/render_report_a4.py cases/2011/110419K34/report.md --out ../opis-a4-sample
python video/scripts/batch_case_qc.py --out ../opis-qc-full-01
python video/scripts/batch_case_qc.py --contracts-only --out ../opis-qc-contracts-02
python video/scripts/batch_case_qc.py --case ROOT-027 --out ../opis-qc-retry-02
```

A4는 210×297mm, 10.5pt 본문, 9.5pt 표, 19/18/18mm 여백, 페이지 번호 및 미승인 표기. 표 머리글 반복, 행 분할 억제. 외부 리소스 로드 차단, 링크는 표시 텍스트만 보존, 이미지가 있으면 대체 텍스트와 경고를 남긴다. 원문 Markdown은 변경하지 않는다. 내용 축약 및 최대 페이지수 강제 없음.

새 외부 출력 폴더: 기존 qc.json, classroom_render.pdf, pages/ 외에 a4/report_a4.pdf, a4/report_a4_qc.json, a4/page-*.png 및 A4 로그를 저장한다. summary.json/CSV에 A4 상태·페이지·경고 및 기존 계약/PPT 상태를 별도로 집계. A4 실패 또는 경고가 기존 성공 상태를 숨기지 않도록 별도 필드와 종료코드로 확인. 원래 계약 실패 및 PPT 오류가 있어도 A4 검사는 독립 진행. 계약 전용 모드는 A4를 생략.

텍스트 블록 검사는 휴리스틱이며 의미 정확성, 모든 표 셀의 시각적 잘림, 그림, 승인 상태를 보증하지 않는다. 모든 결과는 can_ship=false. 실제 PDF/PNG는 외부 출력 폴더에 보관. 파일 해시와 QC 결과만 저장소에 등록.

로컬 GitHub DNS 실패로 실제 전체 체크아웃의 37건 통합 실행은 아직 대기. 실제 PILOT-28 Markdown 1건과 긴 표 가상 문서, 가상 worker 통합 테스트 결과를 별도 JSON에 기록한다.
