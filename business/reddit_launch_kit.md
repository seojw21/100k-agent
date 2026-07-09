# RateParse — Reddit 진출 키트 (r/FreightBrokers)

> 목표: 실제 운임표 샘플 확보 + 첫 사용자 + "만드는 사람" 신뢰. 밴 회피가 최우선.
> 원칙(강의 EP.01/03): build in public, 결과를 판다, 실패·한계도 공개.

---

## ⚠️ 0. 게시 전 필수 (안 하면 밴/삭제)

1. **계정 karma·나이**: 신규/저karma 계정은 자동 삭제됨. 최소 2~3주 된 계정 + 다른 서브레딧
   에서 쌓은 댓글 karma 필요. 없으면 → 아래 "1주 워밍업" 먼저.
2. **서브레딧 규칙 확인**: r/FreightBrokers 사이드바의 self-promotion 규칙 정독.
   자기 홍보 금지면 → 링크 없이 "도움 요청/피드백"으로만, 링크는 DM/댓글 요청 시.
3. **게시 시간**: 미국 동부 기준 평일 오전 8~10시(브로커 업무 시작). 한국 시간 밤 9~11시.

## 1주 워밍업 (karma 없을 때)

- 매일 r/FreightBrokers, r/logistics의 질문 글에 **진짜 도움되는 댓글** 2~3개.
- 운임·배차·TMS 관련 질문에 경험/지식으로 답. 이 단계에선 RateParse 언급 절대 금지.
- 목표: 게시 자격 + "이 사람 업계 좀 아네" 인상.

---

## 2. 메인 게시글 (복사해서 사용, 링크 없는 버전)

**제목:**
```
I built a tool that turns messy carrier rate sheets into a searchable lane database — looking for real sheets to test against (not selling anything)
```

**본문:**
```
Small broker shop here. One thing that always ate my time was carrier rate
sheets — every carrier sends a different format (PDF, Excel, some just paste
rates in an email), and finding "what's my rate for Chicago to Dallas dry van"
meant digging through files.

So I built something that takes those sheets and turns them into one searchable
lane database, then spits out a quote with your margin applied. Upload, search,
done.

Here's my problem: it works great on clean sheets, but real carrier sheets are
messy — weird abbreviations, fuel surcharges baked in, accessorials in
footnotes, dates in every format. I want to find where it breaks BEFORE I tell
anyone it's ready.

If anyone's willing to share a rate sheet (redact the carrier name / fudge the
actual rates if you want — I just need the messy *structure*), I'll run it and
send you back the clean structured output. Free, no signup, no pitch. I mostly
want to see what formats break it.

Also genuinely curious how you all handle this today — spreadsheets? memory?
a TMS? Trying to understand if this is even a real pain for shops my size or
just mine.
```

**왜 이렇게 썼나 (근거):**
- 제목에 "(not selling anything)" — Reddit의 광고 알레르기를 선제 차단.
- "Small broker shop here" — 같은 처지임을 먼저. 외부 벤더가 아니라 동료.
- "where it breaks BEFORE I tell anyone it's ready" — 강의의 정직한 build-in-public. 완성품 홍보 아님.
- 마지막 질문("how do you handle this today?") — 순수 대화 유도 = Reddit이 좋아하는 형식 + 시장 검증 데이터.
- 링크 0개 — 규칙 위반 위험 제거. 관심 있으면 알아서 물어봄.

---

## 3. 댓글 대응 스크립트

**"링크 어디?" / "어디서 써봐요?" (호의적):**
```
Sent you a DM — didn't want to drop a link in the post and come off as an ad.
Happy to just run your sheet and send back the output too if you'd rather try
it that way first.
```
→ DM으로 https://rateparse.xyz 전달. 또는 샘플 받아 직접 파싱해 결과만 회신(가입 마찰 0).

**"이거 [Vooma/Drumkit]랑 뭐가 달라요?":**
```
Those are great but they're full-stack, enterprise, sales-call-first. This is
way narrower — just the rate sheet → searchable database piece, self-serve,
$49/mo, card and go. Built for 1–10 person shops that don't want a demo call.
```

**"AI 믿을 만함? 요율 틀리면 큰일인데":**
```
Fair — that's exactly why I'm asking for real sheets to break it. It flags rows
it can't parse instead of guessing, and you see every extracted rate before you
quote off it. Not trying to replace your judgment, just the data entry.
```
→ 강의 "품질=마진" + 정직함. 과장 금지.

**부정적/공격적 댓글:**
- 방어·논쟁 금지. "Totally fair, appreciate the honesty — what would make it
  actually useful for you?" 로 피드백 전환. Reddit은 방어적 창업자를 싫어함.

---

## 4. 샘플 받은 후 (전환 루프)

1. 받은 시트 파싱 → 결과(레인 테이블 + 견적) 스크린샷/텍스트로 회신.
2. **실원가 계측 데이터 첫 수집** (방금 배포한 것) → 마진 실측.
3. 파싱 실패한 포맷 → 개선 백로그 (carrier명 추출·dedupe 등 알려진 이슈와 함께).
4. 만족한 사람에게: "free tier로 3장까지 그냥 써봐요, 가입만 하면 돼요" → 첫 활성 사용자.

---

## 5. 측정·손절 연결

- 기록: 게시 반응(업보트/댓글/DM 수), 샘플 확보 수, 파싱 성공률, free 가입, 유료 전환.
- 8주 차 유료 3건 미만 → 피벗 검토([[후보군.md]] idea_975).
- 한 서브레딧에 반복 도배 금지 — 반응 보고 r/logistics 등으로 확장.
