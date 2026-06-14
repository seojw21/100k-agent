# [Design Guide] T+72 Redirect Page: Lost Income Component

## 1. 핵심 디자인 원칙 (Core Principles)
- **High Contrast:** 시각적 긴박감과 가독성을 위해 고대비 컬러 시스템 적용.
- **Directness:** 3040 해외 타겟을 고려하여 군더더기 없는 직설적인 레이아웃.
- **Urgency:** 'Stop the Loss' 컨셉을 시각적으로 극대화.

## 2. 컬러 팔레트 (Color Palette)
| 요소 | 색상 코드 | 용도 |
| :--- | :--- | :--- |
| **Primary Background** | `#000000` | 페이지 배경 및 주요 컨테이너 |
| **Highlight / Action** | `#FFD700` | 'Lost Income' 수치, 'Stop the Loss' 버튼/텍스트 |
| **Warning / Alert** | `#FF0000` | $100 임계치 도달 시 경고 표시 (선택적 강조) |

## 3. 타이포그래피 및 스타일 (Typography & Style)
- **Main Metric (Lost Income Amount):**
  - **Size:** `48px` (모바일/데스크톱 공통 강조)
  - **Weight:** Bold
  - **Color:** `#FFD700`
  - **Effect:** 수치가 업데이트될 때 시각적 임팩트를 위해 약간의 애니메이션(Scale 또는 Pulse) 적용.
- **Headline ("Stop the Loss"):**
  - **Size:** `32px`
  - **Weight:** Bold
  - **Color:** `#FFD700` (또는 배경이 검정일 때 가장 대비가 강한 색상)
- **Sub-headline ("Recover Your Lost Income"):**
  - **Size:** `18px`
  - **Weight:** Medium
  - **Color:** `#FFFFFF` (흰색으로 가독성 확보)

## 4. 컴포넌트 레이아웃 및 시각적 요소
### [Lost Income Visualization Block]
1. **Header:** "Stop the Loss" (상단 중앙 또는 좌측 정렬, 강조형)
2. **Sub-text:** "Recover Your Lost Income" (헤드라인 바로 아래 배치)
3. **Main Value:** `$[Calculated Amount]` (48px, #FFD700 적용)
4. **Threshold Alert:** 
   - 수치가 $100에 근접하거나 초과할 경우, 해당 영역에 **Pulse 효과**를 부여하여 시각적 경고 전달.
5. **CTA Button:** "Secure Your Income Now" (또는 관련 전환 버튼)
   - 배경: `#FFD700` / 텍스트: `#000000`

## 5. 애니메이션 사양 (Animation Specs)
- **Count-up Animation:** 페이지 로드 시 'Lost Income' 수치가 0에서 최종 금액까지 빠르게 카운트업되며 표시됨.
- **Pulse Effect:** $100 임계치 도달 시 수치 부분에 1초 간격의 부드러운 Pulse 애니메이션 적용.

## 6. 개발 구현 참고 (Dev Notes)
- 모든 수치는 실시간 데이터와 연동되어야 하며, 계산 오류 시 기본값(Default Value)을 표시하는 예외 처리 포함.
- 고대비 컬러(#000000, #FFD700)는 웹 접근성 가이드라인을 준수하며 명확하게 구분되어야 함.