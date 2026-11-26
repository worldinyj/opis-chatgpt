# Phase 3-D 전문가 검토 준비 완료

기준 40072c2b91d56ed8d38957aa6acda1d8635a42a7. 37건 패키지, D/I 242개 우선 판정 대상, H/P 43개 별도 확인. 추가 및 미선정은 전체 코드로 유지. 기존 metadata 배열 148개 비교: {"MATCH":148}. 패키지 생성 구조검사 37/37, 기존 blob 1362개 불변. 원본 재판독 및 전문가 승인 미실시.

## 검토 순서

| 순위 | 사건 | D/I | H/P | 패키지 |
|---|---|---:|---:|---|
| P1_EVIDENCE_BOUNDARY | 031229Y5 | 0 | 8 | [열기](../cases/2003/031229Y5/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_EVIDENCE_BOUNDARY | 020405U4 | 0 | 6 | [열기](../cases/2002/020405U4/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_EVIDENCE_BOUNDARY | 941020-1301 | 0 | 5 | [열기](../cases/1994/941020-1301/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_LINK_REVIEW | 240319W3 | 10 | 0 | [열기](../cases/2024/240319W3/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_LINK_REVIEW | 230405W2 | 8 | 0 | [열기](../cases/2023/230405W2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_LINK_REVIEW | 200719HU6 | 9 | 0 | [열기](../cases/2020/200719HU6/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_LINK_REVIEW | 190510HB1 | 17 | 1 | [열기](../cases/2019/190510HB1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_LINK_REVIEW | 061011U2 | 9 | 0 | [열기](../cases/2006/061011U2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P1_LINK_REVIEW | 060507U1 | 8 | 2 | [열기](../cases/2006/060507U1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 250314SH2 | 7 | 1 | [열기](../cases/2025/250314SH2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 190121W3 | 4 | 1 | [열기](../cases/2019/190121W3/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 130414KR4 | 6 | 1 | [열기](../cases/2013/130414KR4/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 130117U1 | 5 | 1 | [열기](../cases/2013/130117U1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 051106W1 | 2 | 8 | [열기](../cases/2005/051106W1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 001117K1 | 2 | 5 | [열기](../cases/2000/001117K1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 990323Y2 | 5 | 2 | [열기](../cases/1999/990323Y2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P2_ROLE_BOUNDARY | 970117-1502 | 6 | 2 | [열기](../cases/1997/970117-1502/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 250112W2 | 10 | 0 | [열기](../cases/2025/250112W2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 240908HB6 | 7 | 0 | [열기](../cases/2024/240908HB6/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 240513W4 | 10 | 0 | [열기](../cases/2024/240513W4/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 221222K3 | 7 | 0 | [열기](../cases/2022/221222K3/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 220908SW2 | 8 | 0 | [열기](../cases/2022/220908SW2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 210712K3 | 6 | 0 | [열기](../cases/2021/210712K3/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 180611W3 | 8 | 0 | [열기](../cases/2018/180611W3/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 170327K4 | 5 | 0 | [열기](../cases/2017/170327K4/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 161220HU5 | 3 | 0 | [열기](../cases/2016/161220HU5/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 160227HB1 | 7 | 0 | [열기](../cases/2016/160227HB1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 150903K4 | 4 | 0 | [열기](../cases/2015/150903K4/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 141017Y3 | 6 | 0 | [열기](../cases/2014/141017Y3/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 141001Y12 | 7 | 0 | [열기](../cases/2014/141001Y12/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 140617W4 | 5 | 0 | [열기](../cases/2014/140617W4/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 140228Y2 | 5 | 0 | [열기](../cases/2014/140228Y2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 121126U6 | 8 | 0 | [열기](../cases/2012/121126U6/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 110621K2 | 7 | 0 | [열기](../cases/2011/110621K2/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 110419K34 | 10 | 0 | [열기](../cases/2011/110419K34/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 100917SK1 | 11 | 0 | [열기](../cases/2010/100917SK1/review_package/EXPERT_REVIEW_PACKET_V1.json) |
| P3_STANDARD_REVIEW | 090903W2 | 10 | 0 | [열기](../cases/2009/090903W2/review_package/EXPERT_REVIEW_PACKET_V1.json) |

P1_LINK_REVIEW 6건: 원장 근거 연결 검토. P1_EVIDENCE_BOUNDARY 3건: 직접·간접 후보 0, 교육/긍정 범위 및 누락 검토. P2는 교육 가설 경계, P3는 표준 검토. 순서는 업무 편의이며 사고 중요도 순위가 아니다.

[판정 입력용 CSV](phase3d_expert_decisions_20261126.csv)에는 242개 후보별 근거 ID와 설명, 패키지 blob, 빈 판단란을 제공한다. 전체 40속성 및 H/P는 사건 패키지 참조. 새 판정 수집, 검증, 변경 승인 및 후속 콘텐츠 반영은 다음 단계이며 자동 승인 없음. 6개 경고는 작성자 의견 등록, 전문가 검토 전 종결하지 않는다. can_ship=false.
