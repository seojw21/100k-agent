# Lost Income Component Design Specification

## 1. Color System
- Primary: `#000000` (Background)
- Accent: `#FFD700` (Highlight, Numbers, Buttons)
- Text: `#FFFFFF` (Primary), `#CCCCCC` (Secondary)

## 2. Typography & Sizing
- **Main Value:** `48px`, Bold, Color: `#FFD700`
- **Headline:** `24px`, Bold, Color: `#FFFFFF`
- **Label/Body:** `18px`, Regular, Color: `#FFFFFF`

## 3. Component Layout (T+72 Redirect Page)
- **Container:** Padding: 40px, Background: #000000, Border: 1px solid #FFD700 (Optional for emphasis)
- **Animation:** Count-up effect on the "Lost Income" value.
- **Logic:** If `calculated_loss > 100`, apply a subtle red glow or warning icon to emphasize urgency.

## 4. Assets & Icons
- Use high-contrast icons (Solid style).
- No gradients; use flat colors for maximum clarity on mobile/desktop.