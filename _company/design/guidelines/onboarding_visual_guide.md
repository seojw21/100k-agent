# [Visual & UI Guidelines] - Post-Purchase Success Sequence

## 0. Core Design System (Global Standard)
*   **Color Palette:**
    *   **Background:** `#000000` (Pure Black) - 시각적 집중도 극대화.
    *   **Primary Accent (Action):** `#FFD700` (High-Contrast Yellow) - 버튼, 핵심 강조 문구, 성공 아이콘.
    *   **Secondary Accent (Alert/Urgency):** `#FF0000` (Red) - 주의 사항 또는 즉각적인 행동 유도 시 사용.
    *   **Typography:** `#FFFFFF` (White) - 기본 본문 및 설명.
*   **Typography:** 
    *   **Heading:** Bold Sans-serif (예: Inter, Montserrat). 가독성 최우선.
    *   **Body:** Medium weight. 충분한 자간과 행간 확보.
*   **Visual Principle:** "Problem-Solution-Result" 구조를 시각적 계층(Hierarchy)으로 변환. 중요한 정보는 크고 밝게, 부차적인 정보는 작고 차분하게 배치.

---

## 1. Step 1: T+1 Minute (Immediate Confirmation)
**목표:** "잘 선택했다"는 안도감과 즉각적인 성취감 제공.

*   **Visual Concept:** **[The Victory Moment]**
    *   **Hero Element:** 화면 중앙에 대형 체크마크(✔) 또는 'Success' 배지 배치 (Color: `#FFD700`).
    *   **Headline:** "Welcome Aboard!" 또는 "Access Activated"를 가장 큰 폰트로 강조.
    *   **Button UI:** 
        *   배경: `#FFD700` / 글자: `#000000` (고대비)
        *   효과: 클릭 시 즉각적인 반응(Scale 변화 등).
    *   **Layout:** 중앙 집중형. 불필요한 메뉴를 숨기고 'Get Started' 버튼으로 시선을 유도하는 단일 경로 설계.

## 2. Step 2: T+24 Hours (Value Realization)
**목표:** "이것은 실제로 작동한다"는 확신 부여.

*   **Visual Concept:** **[The Roadmap/Progress]**
    *   **Infographic Element:** 현재 단계와 다음 단계를 시각화한 프로그레스 바(Progress Bar). (Active: `#FFD700`, Inactive: Gray)
    *   **Highlighting:** 핵심 혜택(Specific Benefit) 부분에 노란색 하이라이트 박스 적용.
    *   **Content Layout:** 리스트 형태를 활용하되, 'Quick Win' 항목은 강조 아이콘을 배치하여 시각적 분리.
    *   **Contrast Rule:** 배경 `#000000` 위에서 텍스트가 뭉치지 않도록 충분한 여백(Padding) 확보.

## 3. Step 3: T+72 Hours (Long-term Loyalty)
**목표:** 지속적인 가치 제안 및 커뮤니티 연결.

*   **Visual Concept:** **[The Growth Path]**
    *   **Social Proof Card:** 실제 성공 사례나 후기를 카드 UI로 제작. 테두리(Border)를 `#FFD700`으로 처리하여 시선 고정.
    *   **Call-to-Action:** "Next Steps" 섹션을 구분선으로 분리하고, 다음 행동을 유도하는 버튼을 하단에 배치.
    *   **Color Strategy:** 장기적 관계를 위해 신뢰감을 주는 톤 유지하되, 핵심 전환 포인트에서만 `#FFD700` 사용.

---

## UI Component Summary Table
| Element | Style | Color Code | Purpose |
| :--- | :--- | :--- | :--- |
| **Primary Button** | Solid Fill | `#FFD700` (BG) / `#000000` (Text) | Main Action (Get Started, Claim) |
| **Success Icon** | Outline/Solid | `#FFD700` | Confirmation & Achievement |
| **Highlight Box** | Border/Background | `#FFD700` | Key Value Proposition |
| **Warning/Alert** | Text/Icon | `#FF0000` | Critical Info / Urgency |
| **Body Text** | High Contrast | `#FFFFFF` | Readability on Black Background |