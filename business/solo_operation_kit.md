# RateParse — 혼자 운영 킷 (AI 도우미 없이 8주 검증)

> 목적: 7/7 이후 비싼 AI 없이도 RateParse를 혼자 운영하며 8주 검증을 완료한다.
> 추가 지출 0. 영어는 아래 완성 답장 + 무료 번역으로 커버.

---

## 0. 마음가짐 (먼저 읽기)

- 이미 쓴 돈은 매몰비용. 지금부터는 **추가 지출 0**으로 답을 얻는 게임.
- 8주 안에 유료 3건이면 계속, 아니면 [[후보군]]의 다음 아이디어로. **둘 다 정상 결과.**
- 안 되도 남는 것: 라이브 제품 1개 + 창업 경험 + 검증된 다음 아이디어 2개 + 재사용 템플릿.
- 이건 "반드시 성공"이 아니라 "싸게 확인"하는 실험이다. 결과가 뭐든 손해가 아니다.

---

## 1. 운영 비용 실측 (안심용)

| 항목 | 월 비용 | 비고 |
|---|---|---|
| Firebase Hosting/Functions/Firestore | ~$0 | 무료 티어 안. 트래픽 적으면 청구 거의 없음 |
| 도메인 rateparse.xyz | 연 ~$1~10 (이미 결제) | 1년치 냄 |
| ImprovMX 이메일 | $0 | 무료 플랜 |
| 파싱 API (Anthropic) | 장당 ~$0.35 | **고객이 결제할 때만 발생 = 매출이 냄** |
| **고정 지출 합계** | **거의 $0** | 고객 없으면 API도 0 |

→ 고객이 안 와도 돈이 새지 않는다. 와도 API비는 그들이 낸 $49에서 나온다.

---

## 2. 영어 답장 — 무료로 처리하는 법

**원칙: 예상 가능한 답장은 아래 완성본 복붙. 예상 밖은 무료 번역기.**

### 무료 번역 도구 (우선순위)

**1순위 — 로컬 올라마(Ollama)** ⭐ 완전 무료 + 비공개 + AI 도우미 없이도 됨
- 이미 설치·작동 확인됨(모델 gemma4:12b, ornith:35b). 내 컴퓨터에서 돌아 API 비용 0, 데이터 외부 안 나감.
- **켜는 법**: 터미널에서 `ollama serve`(이미 켜져 있으면 생략). 포트 11434.
- **Connect AI 익스텐션 연결**: ⚙️ 설정 → AI 엔진 변경 → Base URL `http://127.0.0.1:11434/v1`, 모델 `gemma4:12b`.
- **터미널로 바로 번역**(익스텐션 없이도):
  ```sh
  # 받은 영어 답장 뜻 파악 (영어 → 한국어)
  ollama run gemma4:12b "다음 영어 이메일을 한국어로 번역: <영어 원문 붙여넣기>"

  # 보낼 답장 만들기 (한국어 → 영어, 비즈니스 톤)
  ollama run gemma4:12b "Translate to natural business English: <한국어 붙여넣기>"
  ```
- 품질: 콜드 이메일 답장으로 충분(검증됨). 복잡한 협상은 아래 완성본 우선.

**2순위 — DeepL** (deepl.com) — 무료, 브라우저에서 바로. 올라마 안 켜졌을 때.

**사용 흐름**: 받은 영어 답장 → 올라마/DeepL로 뜻 파악 → 아래 완성 답장 중 맞는 것 복붙 → 없으면 한국어로 쓰고 올라마/DeepL로 영어 변환 → Gmail 전송.

### 완성 영어 답장 모음 (복붙용)

**A. 샘플 시트를 보내줬을 때:**
```
Awesome, thank you! Give me a bit and I'll send back the structured output.
```
→ 그 시트를 rateparse.xyz/app에 업로드 → 결과 스크린샷 회신.
회신 문구:
```
Here's the output from your sheet — every lane in one searchable table, and you
can pull a quote with your margin in a couple seconds. Anything look off? Happy
to tweak. If you want to keep using it, the free tier covers 3 sheets, no card.
```

**B. "Vooma/Drumkit랑 뭐가 달라?":**
```
Good question. Those are great but they're full platforms — enterprise pricing,
sales calls, built for bigger operations. RateParse is deliberately narrow: just
the rate-sheet-to-searchable-database piece, self-serve, $49/mo, no demo call.
Built for small shops that don't need the whole suite.
```

**C. "AI 정확해? 요율 틀리면 큰일인데":**
```
Totally fair — that's the #1 thing. It flags any row it can't parse cleanly
instead of guessing, and you see every extracted rate before you quote off it.
Try it with your own sheet and judge the output yourself before trusting it —
no signup needed, there's a live demo right on the site.
```

**D. "가격이 어떻게 돼?":**
```
Free tier is 3 sheets (no card). Paid starts at $49/mo for 20 sheets and 500
lane searches — Pro is $149 (100 sheets), Growth $299 (300 sheets). No unlimited
plan, so there are no surprise overage bills.
```

**E. "관심 없음 / no":**
```
No problem at all — thanks for reading, and best of luck out there.
```
→ 즉시 중단. 재접촉 금지.

**F. "어떻게 시작해?":**
```
Just go to rateparse.xyz, click "Start free," sign in with Google, and upload a
sheet — 3 are free, no card. There's also a demo on the homepage you can try
first without signing in. Let me know if anything's unclear.
```

---

## 3. 주간 운영 체크리스트 (혼자, 30분/주)

매주 같은 요일에:

- [ ] **이메일 확인**: Gmail(support@rateparse.xyz 포워딩) — 답장 오면 2번 완성본으로 대응.
- [ ] **신규 가입/결제 확인**: Firebase Console → Firestore → users 컬렉션 수 확인. 또는 PayPal 대시보드에서 구독 확인.
- [ ] **GEO 벤치마크 실행** (선택, API 소액): `ANTHROPIC_API_KEY=... python3 rateparse/scripts/geo_benchmark.py` → citation_rate 기록. 비용 아끼려면 격주로.
- [ ] **Search Console 확인**: search.google.com/search-console → 노출/클릭 수 추세.
- [ ] **간단 기록**: 이번 주 발송/답장/가입/유료 몇 건인지 메모.

---

## 4. 8주 판단 기준 (블루프린트)

- **유료 전환 3건 이상** → 된다. 재투자 판단(더 개발·마케팅).
- **3건 미만** → 피벗. [[후보군]]의 idea_975(루핑, 지불의사 실측됨) 1순위 검토.
- 단일 주 등락은 무시. **8주 누적**으로만 판단.

---

## 5. 문제 생겼을 때 (셀프 해결)

| 증상 | 확인 |
|---|---|
| 사이트 안 열림 | Firebase Console → Hosting 상태. 보통 자동 복구 |
| 결제 안 됨 | PayPal 대시보드 → 라이브 구독 상태. webhook 로그 |
| 파싱 실패 | 시트 포맷 문제일 수 있음 — 정상, 사용자에게 다른 포맷 요청 |
| API 잔액 부족 | console.anthropic.com → 크레딧 확인 (고객 결제분으로 충당) |

→ 막히면 다음 AI 사용 가능 시점에 몰아서 물어보기. 급하지 않은 건 쌓아뒀다가.

---

## 6. 다음 AI 접근 때 (7/7 이후 재접근 시) 우선순위

돈 여유 생겨 다시 쓸 때만:
1. 답장 데이터 보고 이메일 문구 개선
2. GEO 답변 페이지 배치 3~5 (인용률 안 오르면)
3. 제품 개선(dedupe, carrier명) — 고객이 요청한 것만
4. 8주 결과가 좋으면 확장, 나쁘면 idea_975로 피벗

**핵심: 재접근은 "필요할 때만". 매주 쓸 필요 없다.**
