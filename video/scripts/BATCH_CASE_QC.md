# Phase 2-B/C 전체 사건 일괄 기술 QC

기존 final_case_qc.py를 재사용하고 intake_queue.json과 events.json을 대조해 대상 경로를 계산한다. 승인·사건 인덱스·원본 파일은 변경하지 않는다. 전체 사건은 37건이며 별도 원본 범위 밖 사건은 제외한다.

## 실행

저장소 루트에서 Python 3.10 이상, Node.js, LibreOffice 및 Python 의존성(jsonschema, python-pptx, lxml, pymupdf)을 설치하고 A4 의존성은 [A4_REPORT_QC.md](A4_REPORT_QC.md)에 따라 준비한 뒤:

```sh
python video/scripts/batch_case_qc.py --contracts-only --out ../opis-qc-contracts-01
python video/scripts/batch_case_qc.py --out ../opis-qc-render-01
python video/scripts/batch_case_qc.py --case ROOT-028 --case ROOT-037 --out ../opis-qc-retry-01
```

매 실행은 새 외부 출력 디렉터리를 사용한다. 각 사건 qc.json, 표준출력·오류 로그, PDF 렌더 및 페이지 PNG(렌더 모드), 전체 summary.json/CSV를 보존한다. 실패한 사건도 다음 사건 실행을 막지 않으며 종료코드 1로 표시한다. 반복 selector로 재검사한다. 계약 검증 14/14와 실제 렌더 파일 생성 여부를 구분하며 수동 화면 검토는 남는다. 렌더 플래그는 통과로 집계하지 않는다.

Phase 2-C에서 기존 worker와 독립적인 A4 렌더러를 일괄 실행기에 연결했다. 계약 전용 모드는 A4를 생략하며 렌더 모드는 A4 PDF·QC·PNG 및 별도 상태를 집계한다. 자동 검사는 전문가 승인을 의미하지 않는다. 계약 검사에서 사용한 파일 해시와 HEAD는 개별 qc.json에 남는다. 원본 데이터나 실제 영상 생성 호출 없음. can_ship=false.

현재 채팅 실행환경에서 GitHub DNS 연결이 실패하여 전체 실제 체크아웃 통합 테스트는 대기 상태다. 실행 스크립트 신규 등록 자체를 검증 완료로 집계하지 않는다.
