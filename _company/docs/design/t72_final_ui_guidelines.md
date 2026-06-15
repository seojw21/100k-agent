# [Final UI Guideline] T+72 Redirect Page: Lost Income Visualization

## 1. 디자인 원칙 (Design Principles)
- **고대비(High Contrast):** 모든 핵심 수치와 경고 문구는 배경색 `#000000`(Black)과 강조색 `#FFD700`(Yellow)의 조합을 사용하여 시각적 충격을 극대화함.
- **손실 회피(Loss Aversion):** 사용자가 '아무것도 하지 않음으로써 잃고 있는 돈'을 직관적으로 인식하게 함.
- **수식 기반 시각화:** "Time Saved = Money Earned" 공식을 UI 요소에 녹여내어 가치 제안을 명확히 함.

## 2. 컬러 팔레트 (Color Palette)
| 용도 | 색상 코드 | 적용 대상 |
| :--- | :--- | :--- |
| **Primary Background** | `#000000` | 페이지 전체 배경 및 주요 섹션 배경 |
| **Highlight/Alert** | `#FFD700` | Lost Income 수치, $100 경고 문구, 강조 버튼 |
| **Secondary Text** | `#FFFFFF` | 일반 설명 문구 (가독성 확보) |

## 3. 핵심 컴포넌트 사양 (Component Specifications)

### A. Lost Income Counter (핵심 시각화 영역)
- **기본 상태 (Value < $100):**
  - 수치 표시: `[Lost Income: $XX]` (크고 굵은 폰트, 색상 `#FFD700`)
  - 하단 설명: "Your estimated monthly loss due to manual tasks."
- **경고 상태 (Value ≥ $100):**
  - **Trigger:** 계산된 Lost Income이 $100 이상일 경우.
  - **Visual Change:** 수치 주변에 `#FFD700` 색상의 굵은 테두리(Border) 추가 및 깜빡임(Pulse) 효과 또는 강조 아이콘 삽입.
  - **Copy Update:** "⚠️ WARNING: You are losing over $100/mo in wasted time." (강조색 적용)

### B. 'Time Saved' Conversion Logic
- 수식: `[Minutes Saved] $\rightarrow$ [Equivalent Value]`
- UI 표현: "You save [X] hours monthly, which equals **$[Y]** in potential income."
- 강조 포인트: $[Y] 부분에 `#FFD700` 적용.

## 4. 개발 구현 가이드 (For Developer)
- **Logic:** `if (lostIncome >= 100)` 조건문이 충족될 시, 해당 컴포넌트의 CSS 클래스를 `.alert-mode`로 전환.
- **Animation:** 경고 상태 진입 시 수치가 부드럽게 커지거나 강조색이 강조되는 트랜지션 적용.
- **Contrast Check:** 모든 텍스트는 배경 대비 7:1 이상의 명도 대비를 유지할 것.

## 5. 최종 검증 체크리스트
- [ ] $100 임계치 도달 시 색상 및 문구가 즉각적으로 변하는가?
- [ ] #000000과 #FFD700의 조합이 모바일 환경에서도 가독성이 높은가?
- [ ] 'Time Saved = Money Earned' 수식이 직관적으로 연결되는가?