# Grok I2V 프롬프트

원본은 `templates/project/production.json`입니다. common.video + continuity + 해당 참조 외형 + 0/3/6초 상태 + 3구간 motion이 매 클립에 합성됩니다. `production.py build` 결과의 I2V_PROMPTS.md를 복사하세요. 기본 single_start는 시작 이미지 1장만 첨부합니다. 다중 키프레임은 실제 UI 지원을 확인한 경우에만 선택합니다. 제작 목표는 480p / 9:16 / 6초이며 UI에서 따로 설정합니다.
