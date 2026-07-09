# 메인 제품 결정 + 데이터 체크리스트

> 결정일: 2026-07-09  
> 혼란 줄이기용. 에이전트·본인 모두 “무엇을 살릴지” 기준표.

---

## 1) 메인 제품: **RateParse** (추천·확정)

| 비교 | RateParse | WhatReview |
|------|-----------|------------|
| 폴더 | `rateparse/` | `whatsapp-review-saas/` |
| 완성도 | 파싱·결제·GTM·혼자운영 킷 있음 | MVP·B2 콘솔 대기 |
| 가격 | $49/mo | Free + Pro $9/mo |
| 타깃 | US freight broker | IN wedding photo (가설) |
| 손절 | 8주 유료 3건 미만 | 동일, 실패 시 RateParse 복귀 |
| 역할 | **메인 무대** | 백업(주 5h 캡) |

**이유:** 라이브에 가깝고, PayPal·배포·아웃리치 문서가 이미 있으며, WhatReview 계획 문서도 “RateParse 우선 / 실패 시 복귀”로 적혀 있음.  
**분산 금지** 원칙상 지금은 한 제품만 민다.

---

## 2) 데이터 — 살릴 것 / 접을 것

### ✅ 메인으로 읽고 쓰기 (에이전트 컨텍스트 우선)

| 경로 | 용도 |
|------|------|
| `rateparse/` 전체 | 제품·배포·GEO |
| `business/go_to_market_playbook.md` | 진출 플레이북 |
| `business/solo_operation_kit.md` | 영어 답장·혼자 운영 |
| `business/first_targets_ready.md` 등 RateParse 관련 | 타깃 |
| `_shared/goals.md` · `identity.md` | 북극성 |
| `_company/_shared/*` (위와 동기화) | Connect AI가 읽는 쪽 |
| 고객 질문·샘플 파싱 결과 (앞으로 생기는 것) | 전환 자산 |

### 🔵 필요할 때만 검색

| 경로 | 용도 |
|------|------|
| `knowledge/pain_db.json` | freight / logistics / broker 관련·점수 9–10만 |
| `Study/` 중 원가·GEO 강의 요약 | 가격·측정 참고 |
| `whatsapp-review-saas/` | 백업 제품 작업할 때만 |

### ⚪ 당분간 무시 (삭제 안 해도 됨, 작업 입력에 넣지 말 것)

| 경로 | 이유 |
|------|------|
| `_company/sessions` 대량 자동 세션 | 노이즈·반복 많음 |
| `ideas/` 999개 | 신규 아이디어 분산 유발 |
| `knowledge/raw_collected.jsonl`, `selfrag_log` | 엔진 로그 |
| `00_Raw` 강의 샘플 중 RateParse 무관 | 브레인팩 잔여 |
| Writer 쪽 Executive Voice 리드마그넷 목표 | 메인 제품과 무관 → 주간 목표에서 제외 |

### 🟣 나중에 (유료 1건 나온 뒤)

- 잘된 영어 답장·온보딩 문장 → SFT 후보 100개 이내  
- 파인튜닝 재학습  
- pain_db 전면 활용 상품화

---

## 3) 주간 루틴 (데이터 활용 = 이 4스텝)

1. **목표 읽기** — `goals.md` 이번 주 5개  
2. **제품 폴더만 열고** 막힌 것 1개 고르기  
3. **Connect AI에 미션 1개** (아래 복붙)  
4. **결과 중 쓸 만한 것만** `business/` 또는 `rateparse/docs`에 남기기 (sessions 방치 금지)

### 복붙 미션 예시

```
goals.md와 rateparse/, business/go_to_market_playbook.md, business/solo_operation_kit.md만 보고 작업해.
다른 아이디어·유튜브·신규 SaaS 금지.

오늘 산출물:
1) PayPal 라이브 체크리스트 (남은 단계만)
2) r/FreightBrokers용 도움 댓글 영어 3개 (링크 없음)
3) 샘플 rate sheet 요청 게시 초안 1개 (홍보 아닌 도움 요청 톤)
```

---

## 4) 체크: 이번 주 성공 정의

- [ ] 결제 경로가 “진짜 돈” 받을 준비에 한 걸음 가까워짐  
- [ ] 커뮤니티에 사람 말 걸기 5회 이상  
- [ ] 파싱 증거(샘플) 1건  
- [ ] sessions에 쓸모없는 자동 리포트만 늘지 않음  

끝. 개수 500·3000은 신경 끄고, **위 체크 4칸**만 보면 됨.
