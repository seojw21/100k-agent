# [UI Specification] T+72 리다이렉트 페이지: 'Lost Income' 시각화 가이드라인

## 1. 디자인 원칙 (Design Principles)
- **고대비(High Contrast):** 배경과 핵심 수치 간의 극명한 대비를 통해 사용자의 시선을 즉각적으로 고정.
- **가독성 우선:** 복잡한 장식 배제, 숫자와 단위의 명확한 전달.
- **심리적 자극:** '잃어버린 수익(Lost Income)'을 시각적으로 강조하여 행동 변화 유도.

## 2. 컬러 시스템 (Color System)
| 요소 | 색상 코드 | 적용 규칙 |
| :--- | :--- | :--- |
| **Primary Background** | `#000000` | 섹션 배경 및 카드 컨테이너에 적용 |
| **Highlight Color** | `#FFD700` | 'Lost Income' 수치, 화살표, 핵심 강조 문구에 적용 |
| **Secondary Text** | `#FFFFFF` (80% Opacity) | 레이블(Label), 보조 설명문구에 적용 |
| **Warning/Alert** | `#FF0000` | (선택사항) 현재 상태가 부정적일 때만 포인트로 사용 |

## 3. 타이포그래피 및 컴포넌트 사양 (Typography & Components)

### A. 'Lost Income' 메인 수치 카드
- **컨테이너:** 배경 `#000000`, 테두리 `1px solid #FFD700` (또는 강조 효과를 위한 미세한 글로우 효과).
- **레이블 (Label):** "Estimated Lost Income" 또는 "Potential Annual Loss"
  - Font: Bold, Size: 16px, Color: `#FFFFFF`, Margin-bottom: 8px.
- **수치 (Value):** "$XX,XXX" (실시간 계산된 금액)
  - Font: Extra Bold, Size: 48px~60px, Color: `#FFD700`.
  - **효과:** 수치 뒤에 `+` 또는 화살표 아이콘을 배치하여 '회수 가능한 금액'임을 암시.

### B. 비교 테이블 (Comparison Table)
| 항목 | 현재 상태 (Current) | 개선 후 (With Solution) |
| :--- | :--- | :--- |
| **Time Spent** | 40h / month | 5h / month |
| **Lost Income** | **$2,000** (Gray/Small) | **$18,000** (Gold/Large) |

- **시각적 강조:** '결과' 열(Column)의 수치에 `#FFD700`를 적용하고 폰트 크기를 1.5배 키워 시각적 위계 형성.

## 4. 레이아웃 및 인터랙션 (Layout & Interaction)
- **비율:** 화면 중앙 또는 핵심 전환 지점에 배치.
- **애니메이션:** 페이지 로드 시 'Lost Income' 수치가 카운트업(Count-up)되며 `#FFD700` 색상으로 변하는 효과 적용 (선택 사항이나 권장).
- **공백(Spacing):** 수치 주변에 충분한 여백을 확보하여 다른 요소와 섞이지 않도록 분리.

## 5. 디자인 레퍼런스 가이드
- 배경: 완전한 블랙 (#000000)
- 강조: 금색/노란색 (#FFD700) - 시인성 극대화
- 대비: [검정 배경] + [금색 텍스트] 조합을 모든 핵심 수치에 강제 적용.