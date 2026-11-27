# C07 / C08 — Excel 복사본 연계 및 대시보드 합성 프로토타입
2026-11-27. 실제 AI 제출물 적재 및 승인 금지.
## C07
기준 main 8775c5ae6249cf0f8bcd70d513e3296cbb46343e의 docs/THREE_AI_INDEPENDENT_REVIEW_V1.md 직접 조회: 기존 OPIS_38건_3AI_교차검토_전문가판정_V1.xlsx 통합검토, 3행 헤더, 4~1523행 데이터, A/B/C/H 키, O ChatGPT 보호, P/Q/R Gemini, S/T/U Claude, V/W/X/AC 수식 및 Y:AB 전문가 입력 보호. Git tree 2463개 항목 확인(잘림 없음), 해당 xlsx 없음. Drive에서 정확한 파일명 및 OPIS 3AI 검색 결과 없음; 원본 양식 미확보.
excel/c07_excel.py blob 8b36c646618f7019e935cd68b4f2c6f693dc121b, test_c07.py blob ccce989dcc137d1aa284e602fb4aa03accccbc1d. artifact_tool을 이용한 합성 workbook 복사본 생성. 키/관리번호/사건/코드 일치, 전체 40행 및 사건별 동일 적격 참조, role/result 일치, 비적격 및 중복/위험 텍스트 차단, 기존 대상 셀 덮어쓰기 금지, 원본 SHA256 보존, A1:AC 범위의 값과 수식 비교(계산 캐시 제외), 임시 저장 후 재개방 확인 및 os.link로 새 파일만 공개. 실제 ROOT 키 차단. 수식 주입 텍스트는 이번 합성 버전에서 텍스트로 정규화하지 않고 거부하는 보수적 결정.
실행: python integration_platform/excel/test_c07.py (artifact_tool 설치 환경). 7/7 PASS, 4.914초: copy, duplicate, formula, grid, hold, partial, real_key. 전체 1520행은 plan 시험, 실제 파일 왕복은 역순 40행 Gemini 120셀 및 V4/AC4 수식·O/Y 기존 값 포함 합성 시험. GitHub 재조회 blob과 로컬 실행 파일 일치.
제한: 실제 양식 및 헤더 이름 미확인, 실제 전체 workbook의 다른 시트·서식·유효성 검사·매크로·도형·정의명 등 보존 미검증, 1520행 실파일 왕복/Claude 경로/양 모델 순차 기록/실제 권한과 DB 적격 증거 연결 미검증. 함수 입력 적격 참조는 fixture 주장으로만 검사. 전문가 값은 보존만 하고 신규 기록 미구현. 임시 파일 동시성 및 실제 파일 포맷 별도 검증 필요. C07-R1에서 실제 원본 읽기 전용 확보 후 구조 및 복사본 수용시험. 운영 적용 금지.
## C08
dashboard/c08_dashboard.py blob 90ebc352165c13df209fbf08bdac2911366dec95, test_c08.py blob b37255646a738651890d66e8ec7cd3fdeffa3dab. C04/C05-R1을 재사용하여 독립 실행형 HTML 생성. 38 가상 사건/1520 키/4560 슬롯, 내부 합의 후보 520, 전문가 검토 필요 520, 입력 대기 480, 완전 1040. 데이터 충족률, 두/세 범주 통계, pairwise/common 분모, 10원칙/40속성/가상 발전소/가상 연도/사건 표와 섹션 이동. 전문가 진행 정보는 미연결·미산정 표시. 입력 문자열 HTML escape 및 외부 스크립트/URL 없음.
실행: PYTHONPATH=integration_platform/consensus:integration_platform/analytics python integration_platform/dashboard/test_c08.py. 7/7 PASS, 0.226초: counts, escape, groups, labels, missing, no_remote, real. HTML 생성 실행 완료. 로컬 산출물은 Git에 커밋하지 않고 코드로 재현 가능. 생성 명령: PYTHONPATH=integration_platform/consensus:integration_platform/analytics python integration_platform/dashboard/c08_dashboard.py OPIS_C08_SYNTHETIC_DASHBOARD.html. GitHub blob과 로컬 실행 파일 일치.
제한: HTML 구조/텍스트 시험이며 브라우저 렌더링·접근성·Django·DB 통합·실시간 필터·전문가 이력 연동은 미실행. 실제 통계 아님.
## 종합 및 잔여 게이트
이번 신규 실행 14개 통과. C03-R1/C04-R1 전체 C02-R2 연결시험, C05-R2 DB 연결, C06-R1 Django runtime은 이전 상태 유지; 로컬 django 미설치 확인, 이번 신규 설치 시도 없음. C07-R1 원본 확보와 C08-R1 웹 연동, C09 통합 검증 우선. Track B 승인 대기 상태 변경 없음. 실제 적재는 C10 명시 승인 이후.
approved=false / can_ship=false / main_merge=false / actual_data_import=false.
