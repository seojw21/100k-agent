# 100k-agent — 리퍼코퍼레이션 두뇌 백업

**Connect AI / Antigravity용 회사 지식·에이전트 메모리 저장소**  
(멘토 공유 도구 소스 `connect-ai` 와 별개)

| | |
|--|--|
| 로컬 작업 폴더 | `GEMMA 4` (Antigravity `localBrainPath`) |
| 이 깃허브 | 클라우드 백업·동기화 (`secondBrainRepo`) |
| 메인 제품 | **RateParse** → 코드는 `seojw21/rateparse` |
| 최적화일 | 2026-07-09 |

## 구조 (정리 후)

```
00_Raw/ 10_Wiki/ 20_Meta/     # P-Reinforce 지식
_agents/ _company/ _shared/   # 에이전트·회사 OS
business/                     # RateParse GTM·운영 (코드 아님)
knowledge/pain_db.json        # 시장 통증 DB (고점수 우선)
src/                          # 로컬 유틸 (RAG 등)
```

## 쓰지 않는 것 (의도적으로 제거됨)

- `ideas/` 대량 덤프
- `knowledge/chroma_db` (로컬 재생성)
- raw/selfrag 로그
- 얇은 자율사이클 세션 (<500B)
- `connect-ai/` 복사본
- 사이드 프로토타입 폴더들

## 에이전트 규칙

1. `_shared/goals.md` · `identity.md` 가 북극성
2. RateParse 전환과 무관한 신규 SaaS/유튜브 양산 금지
3. 좋은 산출물은 `sessions`에 방치하지 말고 `business/` 로 승격

## 관련 레포

- 도구: https://github.com/seojw21/connect-ai
- 제품: https://github.com/seojw21/rateparse
- 두뇌: https://github.com/seojw21/100k-agent  (여기)


## 히스토리 최적화 (2026-07-09)

- `git filter-repo` 로 chroma / ideas / connect-ai 복사본 / venv / vsix / pdf 등 **과거 대용량 경로 제거**
- pack 크기 약 **~19MB** (pain_db 유지)
- force-push 완료 — 다른 PC 클론은 `git clone` 새로 받는 것 권장

## GEMMA 4 ↔ 동기화

로컬 작업 폴더(`GEMMA 4`)가 본진입니다. 백업은 이 레포.

```bash
# 상태
python3 "/Users/seojeong-won/GEMMA 4/scripts/sync_100k_agent.py" status

# GEMMA → 100k-agent 반영 후 푸시
python3 "/Users/seojeong-won/GEMMA 4/scripts/sync_100k_agent.py" push --commit --push

# 100k → GEMMA (목표/문서만, 제품 코드 제외)
python3 "/Users/seojeong-won/GEMMA 4/scripts/sync_100k_agent.py" pull
```

동기화 화이트리스트: `_shared/`, `_company/_shared/`, `business/`, `knowledge/pain_db*`, `00_Raw/`, `10_Wiki/`, `20_Meta/` 등  
**제외:** `rateparse/`, `whatsapp-review-saas/`, chroma, raw 로그, `.env`
