# Connect AI — 지금 바로 실행

로컬 LLM + 경로 정합성 맞춤 (두뇌=reaper-brain / 코드=GEMMA 4).

## 0. 구조 (고정)

| 역할 | 경로 |
|------|------|
| Connect 두뇌 | `/Users/seojeong-won/reaper-brain` |
| knowledge | `/Users/seojeong-won/reaper-brain/knowledge` |
| 코딩 워크스페이스 | `/Users/seojeong-won/GEMMA 4` |
| secondBrainRepo | 비움 |
| autoCycleEnabled | **OFF** |

## 1. 열기

1. Antigravity → Open Folder → **GEMMA 4** → **Reload Window** (설정 반영)
2. Connect AI에서 두뇌/`localBrainPath`가 **reaper-brain** 인지 확인
3. Ollama 연결 · 모델: gemma 계열
4. 자율 사이클 토글이 있으면 **끄기** 유지

## 2. 커밋 (VS Code OK)

일반 메시지 커밋 가능. auto-sync 스타일 메시지만 훅이 막음.

```bash
# 예: 정상
git commit -m "feat: rateparse copy tweak"

# 예: 차단됨
# git commit -m "🧠 Auto knowledge update: ..."
```

## 3. 첫 메시지 (복붙)

```
_shared/goals.md, _shared/principles.md, _shared/OPERATING_RUNBOOK.md,
business/go_to_market_playbook.md, business/solo_operation_kit.md, rateparse/README.md 만 사용.
WhatReview·유튜브·신규 아이디어 금지.

산출물 3개, business/ 에 md 저장:
1) PayPal 라이브 남은 단계 체크리스트
2) Freight Reddit 도움 댓글 영어 5 (링크 없음)
3) 샘플 rate sheet 요청 게시 초안 1
```

> 참고: Connect가 reaper-brain 기준으로 쓰면 산출은 `~/reaper-brain/business/` 또는
> `~/reaper-brain/_company/sessions/...` 쪽에 쌓일 수 있음. GEMMA 4 코드 변경은 워크스페이스에서.

## 4. 읽을 파일

| 파일 | 용도 |
|------|------|
| `_shared/goals.md` | 이번 주 할 일 |
| `_shared/principles.md` | Study 경영 원칙 |
| `_shared/OPERATING_RUNBOOK.md` | 일상 운영 |
| `_shared/main_product.md` | 폴더·가격 맵 |
| `BRAIN_DETACHED.md` | 두뇌/커밋 게이트 정책 |

## 5. 백업

3일마다 100k-agent 자동. 수동:

```bash
python3 "/Users/seojeong-won/GEMMA 4/scripts/sync_100k_agent.py" push --commit --push
```
