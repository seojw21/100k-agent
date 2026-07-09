# Connect AI — 지금 바로 실행

로컬 LLM + 두 프로젝트 세팅 완료 (RateParse 메인 / WhatReview 캡).

## 1. 열기
1. Antigravity → Open Folder → **GEMMA 4**
2. Connect AI 아이콘 → Ollama 연결 확인
3. 모델: gemma 계열

## 2. 첫 메시지 (복붙)

```
_shared/goals.md, _shared/principles.md, _shared/OPERATING_RUNBOOK.md,
business/go_to_market_playbook.md, business/solo_operation_kit.md, rateparse/README.md 만 사용.
WhatReview·유튜브·신규 아이디어 금지.

산출물 3개, business/ 에 md 저장:
1) PayPal 라이브 남은 단계 체크리스트
2) Freight Reddit 도움 댓글 영어 5 (링크 없음)
3) 샘플 rate sheet 요청 게시 초안 1
```

## 3. 읽을 파일
| 파일 | 용도 |
|------|------|
| `_shared/goals.md` | 이번 주 할 일 |
| `_shared/principles.md` | Study 경영 원칙 |
| `_shared/OPERATING_RUNBOOK.md` | 일상 운영 |
| `_shared/main_product.md` | 폴더·가격 맵 |

## 4. 백업
3일마다 100k-agent 자동. 수동: `python3 scripts/sync_100k_agent.py push --commit --push`
