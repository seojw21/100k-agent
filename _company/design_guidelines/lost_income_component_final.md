# 🎨 [Final] 'Lost Income' 시각화 컴포넌트 디자인 가이드라인

## 1. 기본 컨셉 및 목적
- **목적**: 사용자가 즉각적으로 손실 중인 금액을 시각적으로 인지하게 하여 'Stop the Loss' 심리를 자극하고 결제 전환을 유도함.
- **핵심 원칙**: 고대비(High Contrast), 직설적 수치 강조, 긴박감 조성.

## 2. 비주얼 시스템 (Visual System)
### 🎨 컬러 팔레트
- **배경색 (Background)**: `#000000` (Pure Black)
- **강조색 (Highlight/Primary)**: `#FFD700` (Gold/Yellow) - *모든 핵심 수치 및 경고 문구에 적용*
- **보조 텍스트**: `#FFFFFF` (White) - *설명 문구 등에 제한적 사용*

### 🖋 타이포그래피 (Typography)
- **메인 수치 (Amount)**: `48px`, Bold, `Letter-spacing: -0.02em`
  - 예: "$150" 또는 "Lost: $150"
  - 적용 색상: `#FFD700`
- **경고 문구 (Warning Label)**: `24px`, Semi-bold
  - 예: "STOP THE LOSS NOW"
  - 적용 색력: `#FFD700`

## 3. 인터랙션 및 애니메이션
### 📈 카운트업 (Count-up Animation)
- **동작**: 페이지 로드 시 또는 컴포넌트 노출 시, 수치가 `0`에서 계산된 `Lost Income` 금액까지 빠르게 카운트업됨.
- **속도**: 약 1.5초 내에 완료 (부드러운 가속도 적용).

### ⚠️ 임계치 알림 (Threshold Logic)
- **조건**: 계산된 수치가 `$100` 이상일 경우.
- **시각적 효과**: 
  - 해당 영역에 미세한 펄스(Pulse) 애니메이션 추가.
  - 경고 문구의 강조도가 높아지며 시각적으로 '위험' 상태임을 알림.

## 4. 레이아웃 구조 (Layout Structure)
1. **상단 라벨**: "Your Lost Income" (Small, White/Gray)
2. **중앙 수치**: "$[Amount]" (**Large, #FFD700, 48px**)
3. **하단 액션**: "Stop the Loss" 버튼 또는 강조 문구 (High Contrast)

## 5. 개발 구현 참고사항 (For Developer)
- 모든 수치는 실시간으로 계산된 값을 반영하며, 소수점은 제거하고 정수로 표기함.
- 애니메이션 라이브러리(예: Framer Motion 등) 사용 시 `easeOut` 효과 적용 권장.