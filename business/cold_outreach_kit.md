# RateParse — 콜드 아웃리치 키트 (영어 대행)

> 전제: 사용자는 영어 실시간 대화가 어렵다. 그래서 **비동기·문서형**으로만 간다.
> 이메일 초안·답장은 전부 Claude가 작성/번역. 사용자는 복사→붙여넣기→전송만.
> 원칙: 소량·타겟·정직. 대량 스팸 금지(역효과 + CAN-SPAM 위반 위험).

---

## 0. 스팸 안 되는 규칙 (반드시 지킬 것)

1. **하루 5~10통 이내**, 손으로 고른 타겟만. 대량 발송 금지 — 도메인 평판 죽고 스팸 폴더행.
2. 첫 메일에 **무료 가치 먼저** (샘플 파싱 제안), 판매 강요 금지.
3. **opt-out 한 줄 필수**: "If this isn't relevant, just reply 'no' and I won't follow up." (CAN-SPAM 준수 + 예의)
4. support@rateparse.xyz 또는 본인 Gmail에서 발송. 처음엔 소량이라 Gmail로 충분.
5. 같은 사람에게 팔로업은 **최대 1회**, 그 후 중단.

---

## 1. 타겟 찾는 법 (직원 1~10명 미국 브로커)

| 소스 | 방법 | 링크 |
|---|---|---|
| **FMCSA SAFER** | 회사명/MC번호로 브로커 authority·소재지 확인 | https://safer.fmcsa.dot.gov/keywordx.asp?searchstring=*BROKER* |
| **FF Dispatch 디렉토리** | 25,000+ 브로커 검색, MC번호·상태 | https://www.dispatchff.com/brokers |
| **LinkedIn** | "freight broker" + "founder/owner", 소규모 회사 필터. 프로필에서 규모 짐작 | linkedin.com |
| **Google** | "freight brokerage" + 도시명 → 소규모 지역 브로커 웹사이트(연락처 이메일 있음) | — |

**타겟 판별**: 웹사이트가 소박하고, "family-owned" / "boutique" / 직원 수 적음 / 데모·엔터프라이즈 언어 없음 = 우리 핏. 대형(수백명)·이미 TMS 완비 = 스킵.

**연락처 확보**: 회사 웹사이트 Contact 페이지의 일반 이메일(info@, ops@) 또는 LinkedIn 담당자. 개인정보 무단수집·구매 리스트 금지.

---

## 2. 첫 이메일 (복사해서 사용) — A안: 샘플 파싱 제안

**제목:**
```
Quick question about your carrier rate sheets
```

**본문:**
```
Hi [Name],

I'll keep this short. I built a small tool for freight brokers that turns
carrier rate sheets (PDF, Excel, even pasted email rates) into one searchable
lane database, so you can pull up "what's my rate for Chicago to Dallas dry van"
in a couple seconds instead of digging through files.

I'm not asking you to buy anything — I'm looking for real rate sheets to make
sure it handles messy formats well. If you send me one sheet (redact the carrier
name or fudge the rates if you want, I just need the structure), I'll run it and
send back the clean, searchable output. Free, no signup.

If it's useful, there's a free tier you can keep using (3 sheets), and paid
plans start at $49/mo — but honestly I mostly want to know if this solves a real
headache for a shop your size.

If this isn't relevant, just reply "no" and I won't follow up.

Thanks,
[Your name]
rateparse.xyz
```

**왜 이렇게**: 판매가 아니라 "샘플 요청" 프레임(Reddit 전략과 동일) → 방어벽 낮음. 무료 가치 먼저. opt-out 명시. 짧음.

---

## 3. 첫 이메일 — B안: 더 직접적(시간 절약 각도)

**제목:**
```
Turning carrier rate sheets into instant quotes — worth a look?
```

**본문:**
```
Hi [Name],

If your team still looks up carrier rates by opening PDFs and spreadsheets,
this might save you time.

RateParse takes your carrier rate sheets and turns them into a searchable lane
database with instant, margin-applied quotes. Upload, search, done. Built
specifically for small brokerages — self-serve, no sales call, no demo. Free to
try with 3 sheets; $49/mo after that.

Two-minute look: rateparse.xyz

Happy to run one of your real sheets through it for free so you can see the
output on your own data first — just reply and I'll send details.

If this isn't relevant, reply "no" and I'll leave you alone.

Best,
[Your name]
```

---

## 4. 답장 대응 (오면 Claude에게 원문 붙여넣기 → 번역·답장 초안 받기)

사용자 워크플로: **받은 영어 답장을 Claude에게 그대로 붙여넣기** → Claude가 (1) 한국어 요약 (2) 영어 답장 초안 제공 → 복붙 전송.

자주 나올 답장 유형별 준비된 답장:

**"Sure, here's a sheet" (샘플 보냄):**
```
Awesome, thank you! Give me a bit and I'll send back the structured output.
```
→ 사용자가 시트를 rateparse.xyz/app에 업로드(또는 나에게 전달) → 결과 스크린샷 회신. accuracy 하네스로 검증도 가능.

**"How is this different from Vooma/Drumkit?":**
```
Good question. Those are great but they're full platforms — enterprise pricing,
sales calls, built for bigger operations. RateParse is deliberately narrow: just
the rate-sheet-to-searchable-database piece, self-serve, $49/mo, no demo call.
Built for 1–10 person shops that don't need the whole suite.
```

**"Is the AI accurate? Wrong rates are dangerous":**
```
Totally fair — that's the #1 thing. It flags any row it can't parse cleanly
instead of guessing, and you see every extracted rate before quoting off it. I've
tested it against a range of messy real-world formats. Send me one of your sheets
and judge the output yourself before trusting it — no signup needed.
```

**"Not interested" / "no":**
```
No problem at all — thanks for reading, and best of luck out there.
```
→ 즉시 중단. 재접촉 금지.

---

## 5. 추적 (간단히)

스프레드시트 한 장 (회사 / 연락처 / 발송일 / 답장 / 상태 / 메모):
- 상태: sent → replied → sample received → trial → paid / declined
- 주간 집계: 발송 수, 답장률, 샘플 확보, 무료 가입, 유료 전환.
- 8주 손절 기준(유료 3건)과 연결.

---

## 6. 이번 주 실행 (영어 부담 0)

| 일차 | 할 일 | 영어? |
|---|---|---|
| 1 | FMCSA/LinkedIn에서 타겟 브로커 10곳 손으로 수집(회사명·이메일) | 읽기만 |
| 1 | 위 A안 이메일에 [Name] 채워 5통 발송 | 복붙만 (내가 작성) |
| 2~5 | 답장 오면 Claude에 붙여넣기 → 번역·답장 → 전송 | 0 (내가 대행) |
| 매일 | 샘플 오면 파싱해 결과 회신 | 0 |

핵심: **실시간 영어 대화 없음. 전부 비동기 + Claude 번역.** 영어 못해도 진출 가능.
