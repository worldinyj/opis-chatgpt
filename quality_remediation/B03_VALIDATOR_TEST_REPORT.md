# B03 — 읽기 전용 품질 검증기 및 회귀시험
2026-11-27. B02 다음 단계. Python + jsonschema 4.26.0.
실행 파일 tools/b03_validator.py, tools/test_b03.py. 로컬 시험 파일과 GitHub 재조회 blob 각각 12318b584b1d9cbc80b75ed280a28c5bbc803a64, c039224be9669fb56f0732fb52e2c74a441345a1 일치.
실행: cd quality_remediation/tools && python -m unittest -v
17/17 PASS: 정상(쉼표/인용부호/개행), JSON 중복 키, 비정상 CSV, 부분 입력, 중복 CSV 키, 역할, 근거 누락, 미등록 사실, ledger gap, 물리쪽 범위, 보고된 원본 identity, 수식 접두어, 역할 접두어 보완, 사유 변경, schema date format, 빈 근거 문구, Git blob/SHA256/경로 탈출. 합성 fixture 및 임시 Git 저장소만 사용.
실제 검증 실행: python quality_remediation/tools/b03_validator.py /path/to/full-clone ROOT-014 (그 외 6개 지정 가능). B01 manifest 고정 commit/blob에서 읽고 원본 Git 객체 및 기록 SHA256 검증, 실제 schema/standard 적용. 실행 결과는 stdout JSON; 원본 및 파생 파일 쓰기 없음.
제한: 실제 저장소 full clone과 원본 바이트를 이 실행 환경에 확보하지 않아 7건 실데이터에 대한 실행 미수행. 회귀시험은 축약 합성 schema로 schema 엔진 및 교차검사 시험; 고정 실제 schema 전체 분기 검증은 B03-R1에서 수행. PDF 원문 재해시/의미 검증 및 독립성 확인 미수행. source serialization은 B04에서 생성 후 별도 검증; 현 단계 SERIALIZE_SOURCE는 모든 근거 행에 대한 작업 후보이지 결함 건수 아님. 절 문자열 의미/일치와 report.md/validation.md 내용 교차검증은 추가 필요. 후보 true도 HOLD 해제나 적격 승인 아님.
다음 B03-R1: 원본 clone 확보 및 7건 실제 검증, schema fixture 보강, 절/보고서 교차검증과 파생 출력 수식 위험 검사. 이후 B04 형식 보완 후보 생성. 모든 7건 HOLD 유지, approved=false, can_ship=false, main_merge=false.
