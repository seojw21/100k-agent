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

## 자동 커밋 루프 (중요 — 2026-07-10 차단)

**본질 원인 (3겹):**
1. GitHub Actions `Knowledge Auto Collector` / `Daily Scan` — 매일 원격에서 `git commit`+`push`
2. Connect AI **24h 자율 사이클** — 자리 비우면 에이전트가 파일 생성 → git 커밋 메시지(`feat: …`) 양산
3. 두뇌 폴더(GEMMA 4) origin = **rateparse** — 위 커밋이 제품 저장소 히스토리에 섞임

**조치 (적용됨):**
- Actions 스케줄 **비활성** (수동 `workflow_dispatch`만)
- `connectAiLab.autoCycleEnabled` = **false**
- 백업은 3일 간격 **100k-agent** 스크립트만 (`chore(auto): brain backup…`)

다시 키지 마세요. 필요 시 Actions → 해당 workflow → Enable 후 **Run workflow** 한 번만.

## 자율 사이클

- **기본 OFF.** 켜면 커밋·세션 노이즈가 다시 늘어남.
- 켤 경우 goals “이번 주 밖 금지”만으로는 **git 커밋 자체는 막히지 않음.**

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
