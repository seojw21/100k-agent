# T+72 리다이렉트 페이지 시각화 가이드라인 (Final)

## 1. 핵심 디자인 원칙
- **고대비(High Contrast):** 모든 주요 수치와 경고 문구는 시인성을 극대화하기 위해 고대비 컬러 시스템을 적용한다.
- **손실 회피(Loss Aversion):** 사용자가 놓치고 있는 기회비용(Lost Income)을 시각적으로 강렬하게 인지시켜 결제 유지 및 업셀링을 유도한다.

## 2. 컬러 팔레트 (Color Palette)
- **Primary Background/Text:** `#000000` (Pure Black)
- **Highlight/Action Color:** `#FFD700` (Bright Yellow) - *핵심 수치 및 강조 문구에만 사용*
- **Warning/Alert:** `#FF0000` (Red) - *필요 시에만 제한적으로 사용*

## 3. 'Lost Income' 수치 시각화 사양
- **대상 요소:** 계산된 손실 금액 (예: $150.00)
- **폰트 스타일:** 
  - Weight: Bold (700+)
  - Size: 최소 48px (모바일 대응 시 가변적이나 강조가 필수적임)
  - Color: `#FFD700`
- **레이아웃:** 
  - 'Lost Income' 문구는 `#000000` 배경 위에 배치.
  - 수치(Amount)는 `_` 또는 `$` 기호와 함께 강조 처리.

## 4. 카운트업 애니메이션 (Count-up Animation)
- **시작 시점:** 페이지 로드 직후 또는 해당 섹션 스크롤 진입 시 즉시 실행.
- **애니메이션 효과:** 0부터 최종 계산된 수치까지 빠르게 카운트업.
- **지속 시간(Duration):** 1.5초 ~ 2초 (사용자가 숫자가 올라가는 것을 인지할 수 있는 최소한의 시간 확보).
- **Easing:** `easeOut` 또는 `linear` 적용 (부드럽게 상승하다가 목표치에서 멈춤).

## 5. UI 컴포넌트 구성 (개발 참고용)
<!-- 예시 구조 -->
<div class="lost-income-container" style="background: #000000; padding: 20px;">
  <p class="label" style="color: #ffffff; font-size: 18px;">You are losing</p>
  <h1 class="value" id="lost-income-amount" style="color: #FFD700; font-size: 48px; font-weight: bold;">
    $<span class="count-up">0</span>
  </h1>
  <p class="sub-text" style="color: #ffffff;">every month due to manual processing.</p>
</div>
```

## 6. 체크리스트 (QA 가이드)
- [ ] 수치가 `#FFD700` 색상으로 명확하게 보이는가?
- [ ] 카운트업 애니메이션이 끊김 없이 부드럽게 작동하는가?
- [ ] $100 임계치 초과 시 경고 문구가 강조되는가?
- [ ] 모바일 환경에서도 48px 이상의 수치가 잘리지 않고 표시되는가?