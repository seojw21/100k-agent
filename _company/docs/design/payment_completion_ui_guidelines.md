# [Design Guideline] 결제 완료 페이지: Saved Income 시각화

## 1. 디자인 원칙 (Core Principles)
- **고대비(High Contrast):** 배경 #000000, 핵심 강조색 #FFD700 적용.
- **가독성 극대화:** 수치(Number)와 핵심 키워드에 볼드체 및 크기 대비 적용.
- **심리적 보상:** 결제 직후 사용자가 "올바른 선택을 했다"는 확신을 시각적으로 즉각 전달.

## 2. UI 레이아웃 설계 (Layout Structure)
결제 완료 메시지 바로 아래에 배치되는 'Value Confirmation Box'를 구성합니다.

### [Component: Value_Confirmation_Card]
- **Container:** 
  - Background: `#000000` (Pure Black)
  - Border: `2px solid #FFD700` (Gold/Yellow)
  - Padding: `32px`
  - Radius: `12px`

### [Content Layout]
1. **Header (Success Message):** 
   - Text: "결제가 성공적으로 완료되었습니다!" 또는 "Payment Successful!"
   - Style: White (#FFFFFF), Font-size: 18px, Weight: Bold
2. **Divider:** 
   - Line: `1px solid #333333` (Subtle separator)
3. **Main Highlight (Saved Income):**
   - Label: "당신이 확보한 가치" / "Your Saved Value"
   - Style: `#FFD700`, Font-size: 14px, Weight: Medium
   - **Value:** `$[수치]` (예: $2,500)
   - **Style:** `#FFD700`, Font-size: 48px, Weight: Extra Bold, Letter-spacing: -1px
4. **Sub-copy (Reasoning):**
   - Text: "당신은 이제 매월 [X시간]의 시간을 절약하고, 약 $[금액]의 잠재적 손실을 방어하게 됩니다."
   - Style: `#FFFFFF`, Font-size: 16px, Line-height: 1.5

## 3. 스타일 가이드 (Style Guide)
| 요소 | 색상 코드 | 타이포그래피 | 비고 |
| :--- | :--- | :--- | :--- |
| 배경색 | `#000000` | - | 카드 전체 배경 |
| 강조 수치 | `#FFD700` | 48px / Bold | 'Saved Income' 금액 |
| 안내 문구 | `#FFFFFF` | 16px / Medium | 일반 설명 텍스트 |
| 포인트 라벨 | `#FFD700` | 14px / Semi-bold | 수치 상단 레이블 |

## 4. 개발 구현 가이드 (For Developer)
- **수치 애니메이션:** 결제 완료 시 `[수치]`가 0부터 해당 금액까지 카운트업(Count-up)되는 효과를 적용하여 시각적 임팩트 부여.
- **하이라이트 강조:** `#FFD700` 색상은 단순 노란색이 아닌, 고대비 환경에서 가장 눈에 띄는 채도를 유지할 것.