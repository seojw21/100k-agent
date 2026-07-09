# Connect AI 실행 런북 — 맘 놓고 돌리기

> 로컬 LLM only. 두 프로젝트: RateParse(메인) + WhatReview(캡).

## 시작 전 30초 체크

1. Antigravity에서 폴더 **`GEMMA 4`** 연 상태  
2. Connect AI 사이드바 열림  
3. Ollama 동작 (`ollama list` 또는 연결 진단)  
4. 모델: `gemma4:12b` 또는 설치한 gemma4 계열  
5. 지식/두뇌 경로: **`/Users/seojeong-won/GEMMA 4`** (md_brain 단독 말고 루트 권장)

## 매일 (5분, 사람)

- [ ] 비서/CEO에게: `goals.md 이번 주 기준으로 오늘 할 일 1개만`  
- [ ] 나온 산출물 중 쓸 만한 것만 `business/` 또는 제품 폴더에 남기기  
- [ ] PayPal/배포 막히면 본인이 콘솔 1스텝 (에이전트는 체크리스트만)

## 자율 사이클 켤 때

- **켜도 됨** — 단 goals에 “이번 주 밖 금지”가 박혀 있음  
- 같은 리포트 반복하면: 사이클 끄거나 CEO에  
  `반복 산출 금지. RateParse KPI 중 빈 칸 하나만.`  
- YouTube/Instagram 구독자 목표는 **무시** (freight Reddit·GEO가 채널)

## 추천 첫 미션 (복붙)

```
_shared/goals.md, principles.md, business/go_to_market_playbook.md, business/solo_operation_kit.md, rateparse/README.md 만 참고.
WhatReview·신규 아이디어·유튜브 금지.

오늘 산출물 3개만:
1) PayPal 라이브 남은 단계 체크리스트 (영어+한국어 짧게)
2) r/FreightBrokers용 도움 댓글 영어 5개 (제품 링크 없음)
3) 샘플 rate sheet 요청 게시 초안 1개 (홍보 아닌 도움 요청 톤)
business/ 아래에 md로 저장.
```

## WhatReview 미션 (여유 시만)

```
whatsapp-review-saas/PLAN.md, B2-SETUP.md, EXECUTION.md 만.
신규 기능 금지. 배포/환경 막힌 1스텝 체크리스트만 작성.
```

## 백업

- 3일마다 `100k-agent` 자동 (launchd)
- 수동: `python3 scripts/sync_100k_agent.py push --commit --push`

## 막히면

| 증상 | 조치 |
|------|------|
| 모델 무응답 | Ollama 재시작, 작은 모델로 |
| 이상한 새 사업 제안 | goals 다시 읽히게 미션에 경로 명시 |
| git pull 충돌 | rateparse 제품 이슈 — 두뇌 백업과 별개 |
| 세션만 쌓임 | 사이클 끄고 위 미션 1개만 수동 |
