# PPT-D 외부 제작 결과 수입 및 품질검증 MVP

현재 로컬 파일에 대해 audit/compare 명령 실행 가능. ChatGPT, Genspark 등 제작 도구에 종속되지 않는다. 외부 서비스에 접속/제출/유료 생성하지 않는다. 독립 검토와 배포 승인을 자동 수행하지 않는다.

## 1. 수입
제출자가 제공한 PPTX와 필요 시 동일 판본에서 로컬로 렌더한 PDF, 공통 프롬프트, 원본/학습 원장 버전, 선택 템플릿 SHA, 제작 도구 주장 및 실행 근거, 자산 권리, 제출 권한을 기록. 원본 바이트는 SHA-256 하위 로컬 intake 폴더에 복사하고 원본 변경 금지. 외부 결과는 사용자 허용 경로에서만 취급하며 권한 미확인 원본 바이너리, 노트, 추출 텍스트, 그림 및 전체 감사 JSON은 공개 GitHub에 자동 저장하지 않는다. 저장소에는 합의된 요약과 설계 패턴만 등록.

## 2. 검사
파이썬 3.10+; python-pptx, lxml, PyMuPDF. 설치는 사용자의 로컬 가상환경에서. ZIP 크기/개수/경로/CRC, XML DTD/entity, 매크로, ActiveX, 임베디드 객체, 외부 관계 검사. 임베디드 객체(정상적인 차트 workbook 포함)나 외부 링크도 보수적으로 별도 검토 대상으로 중단한다. 안전 보증/악성코드 검사기는 아님. 미신뢰 문서는 네트워크 차단된 격리 환경에서 별도 보안 검토 후 렌더; 프로그램 자체는 렌더 명령·매크로·외부 관계를 실행하지 않음. 원본과 PDF의 일치성은 별도 해시 기록/렌더 절차로 증빙; 페이지 수 일치만으로 동일 판본을 증명할 수 없음.

    python education/ppt/quality/audit_pptx.py audit <reference.pptx> --role REFERENCE --producer USER_SUPPLIED_UNKNOWN --pdf <reference.pdf> --archive /local/intake --out /local/reference.json
    python education/ppt/quality/audit_pptx.py audit <candidate.pptx> --role CANDIDATE --producer CHATGPT_LOCAL --pdf <candidate.pdf> --contract <content_contract.json> --archive /local/intake --out /local/candidate.json
    python education/ppt/quality/audit_pptx.py compare /local/reference.json /local/candidate.json education/ppt/design_library/WOLSONG_PROFESSIONAL_V1/LAYOUT_MAP.json --out /local/comparison.json

실제 파일에서 직접 지정 색/글꼴, 글자 크기, 도형 종류, 노트, 상위 객체 경계, 텍스트/표 내용, PDF 추출 텍스트 비교를 수행. 텍스트와 노트 정확 일치 계약은 동일 R1 재생성 기준이다. 외부 전문 AI의 다른 표현·배치에 그대로 강제하면 오류 경고가 발생하므로 동등 의미를 검토할 별도 필수 근거/토큰 계약 및 실제 페이지 매핑을 작성. 자동 PASS는 내용 의미·안전성·저작권·디자인 평가를 대체하지 않는다. 그룹 좌표/회전/SmartArt/차트·이미지 텍스트/상속 스타일은 별도 수동 검토.

## 3. 평가
[QUALITY_RUBRIC.md](QUALITY_RUBRIC.md) 기준으로 작성자 검토 및 독립 검토. 실제 화면을 나란히 확인하고 16장 매핑 결과와 차이를 기록. 동일한 사건, 기준 보고서, 프롬프트, 템플릿, 장수, 목표를 기준으로 서로 비교. 생성 도구의 가격/속도/지원 기능은 실제 실행 기록이 없는 한 미평가. 우수 장표 선정은 내용/디자인/권리 검토와 실제 렌더 후에만. 결과의 기술적 경고가 없는 경우도 REVIEW_REQUIRED 상태 유지.

## 4. 재사용
[REUSE_CATALOG.json](REUSE_CATALOG.json)에는 추출된 레이아웃 패턴 후보만 기록(사진·원본 도형 복제 없음). CANDIDATE_ONLY → DESIGN_REVIEWED → RIGHTS_CLEARED → REUSE_APPROVED → 신규 사건별 CONTENT_REVIEWED → 교육 배포 승인. 각 전이에는 승인자·판본·근거·권리·검수 기록 필요. 새 사건의 데이터로 재구성 후 다시 렌더/검수. 자동 랭킹 및 무조건 장표 복제 금지. 이번 단계에서는 후보 9개 등록, 승격 0개. 자동 장표 복제, 생성기 범용화, 외부 결과 실제 수입 시험은 PPT-E 및 추가 제출 이후.

## 5. 테스트
    cd education/ppt/quality
    python -m unittest -v test_audit.py

로컬 단위 테스트 10/10. 실제 사용자 샘플과 ChatGPT R1에 수입/해시 보존/계약 검사/PDF 대조/16개 매핑 실행. 샘플의 실제 제작 도구 미확인. 실제 Genspark 산출물과 비교한 것으로 간주하지 않음. 참고: 사례별 COMPARISON_PPTD.md와 결과 요약 JSON.
