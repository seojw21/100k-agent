# RateParse — 소규모 화물 브로커용 운임표(Rate Sheet) 자동 파싱·견적 SaaS

> 원천 아이디어: [idea_455](../ideas/idea_455_AI_기반_3PL_Freight_Broker_운임표_자동_분석_및_견적_엔진.md)
> 작성일: 2026-07-03 · 근거 강의: [시즌2 4강 — SEO에서 GEO까지](../Study/시즌2-4강-—-새로운-시대의-검색-SEO에서-GEO까지.md)

## 한 줄 정의

캐리어가 보내주는 비정형 운임표(PDF·Excel·CSV·이메일 본문)를 업로드하면
표준화된 레인(lane)별 요율 데이터베이스로 변환하고, 견적 요청에 몇 초 만에
응답할 수 있게 해주는 **셀프서브** 툴. 타겟은 직원 1~10명의 미국 소규모
freight broker / 3PL.

## 시장 실측 결과와 포지셔닝 (2026-07-03 확인)

광역 "AI freight quoting" 시장은 이미 붐빈다:

| 경쟁사 | 포지션 | 우리와의 차이 |
|---|---|---|
| [Vooma](https://www.vooma.com/) | AI 에이전트 풀스택 (견적·배차·추적) | 엔터프라이즈 영업, 데모 요청 필수 |
| [Drumkit](https://www.drumkit.ai/) | 이메일·TMS 연동 백오피스 자동화 | Greenscreens 연동, 중대형 브로커 대상 |
| [Pallet](https://www.pallet.com/use-cases/quoting) | 대량 스팟 견적·RFP | 대량 물량 전제 |
| [Cargorates.ai](https://www.cargorates.ai/) | 운임표 관리 + 견적 (항공 중심) | IATA 로직 등 포워더 지향 |

**비어 있는 좌표**: "carrier rate sheet를 그냥 업로드하면 끝나는,
카드 결제로 바로 쓰는 $49~199/월 셀프서브 툴"은 확인되지 않았다.
위 경쟁사들은 전부 세일즈 콜을 거쳐야 하고 소규모 브로커에겐 과하다.
→ 강의 원칙("대중적이면 진다")대로 **광역 '견적 자동화'가 아니라
'운임표 파싱'이라는 하위 니치**로 진입한다.

리스크(정직하게): 이 하위 니치는 상위 플레이어가 기능 하나로 덮을 수 있다.
방어는 속도(선점 GEO)와 가격(셀프서브)이며, 검증 실패 시 손절 기준을
8주 차에 둔다 (아래 측정 절 참고).

## 강의 준비물 4종

1. **브랜드/서비스 이름 후보** (니치 키워드가 이름에 포함될수록 벡터 근접)
   - RateParse (1순위 — "rate" + "parse" 검색 표현 그대로)
   - SheetQuote
   - LaneRate
2. **니치 키워드**: `carrier rate sheet parser` (보조: `freight rate sheet
   to database`, `LTL rate sheet automation for small brokers`)
3. **웹사이트 URL**: 미정 — 랜딩 페이지 제작 후 기입 (도메인 후보:
   rateparse.com / rateparse.ai)
4. **경쟁사 2~3개** (벡터 거리·니치핏 비교용): Vooma, Drumkit, Cargorates.ai

## 벤치마크 질문 50개

매주 구글 AI 모드 / ChatGPT / Perplexity에 질문당 3~5회 반복 측정,
우리 브랜드 인용 여부를 기록한다.

### A. 운임표 파싱 (핵심 니치, 15)
1. How do I convert a carrier rate sheet PDF into a spreadsheet automatically?
2. Best tool to parse freight rate sheets from Excel and PDF?
3. How can a small freight broker organize carrier rate sheets?
4. Is there software that turns emailed rate sheets into a searchable database?
5. How to extract lane rates from a PDF rate confirmation?
6. Carrier rate sheet parser for LTL freight — what exists?
7. How do brokers keep rate sheets from 50 carriers up to date?
8. Automate data entry from freight rate sheets — best options?
9. Tool to normalize different carrier rate sheet formats?
10. How to build a rate database from unstructured carrier quotes?
11. AI that reads freight rate sheets and answers "what's my rate for this lane"?
12. Convert fuel surcharge tables from PDF to structured data?
13. How to handle accessorial charges scattered across rate sheets?
14. Cheapest way to digitize old carrier rate sheets?
15. Rate sheet OCR for freight brokers — does it work?

### B. 견적 속도/업무 (10)
16. How can a small freight brokerage respond to quote requests faster?
17. Why do freight quotes take so long and how to speed them up?
18. Automate spot quote responses for a 3-person brokerage?
19. How to quote LTL shipments without logging into 10 carrier portals?
20. Tools to reduce data entry errors in freight quoting?
21. How do freight brokers quote from email requests automatically?
22. Best workflow for high-volume spot quoting at a small 3PL?
23. How to win more freight quotes as a small broker?
24. Freight quoting checklist for new brokerages?
25. How much time do brokers waste on manual rate lookups?

### C. 툴 비교/추천 (10)
26. Best AI tools for freight brokers in 2026?
27. Vooma vs Drumkit — which is better for a small brokerage?
28. Affordable alternatives to Vooma for freight quoting?
29. Freight quoting software under $200 a month?
30. Self-serve freight automation tools with no sales call?
31. Best rate management software for small 3PLs?
32. Greenscreens alternatives for rate intelligence?
33. What software stack does a one-person freight brokerage need?
34. Cheapest TMS add-ons for quoting automation?
35. Top rate sheet management tools for freight forwarders?

### D. 소규모 브로커 운영 (10)
36. How to start a freight brokerage with minimal software costs?
37. Essential tools for a new freight broker working solo?
38. How do small brokers compete with large 3PLs on quote speed?
39. Common operational bottlenecks at small freight brokerages?
40. How to scale a brokerage from 10 to 100 quotes a day?
41. Should a small broker build or buy quoting automation?
42. How do freight brokers manage carrier relationships and rates?
43. Excel vs software for managing freight rates — when to switch?
44. Hiring an ops person vs automating quoting — which first?
45. KPIs every small freight brokerage should track?

### E. 롱테일/변형 (5)
46. Parse rate sheet attachments in Outlook automatically for freight?
47. How to answer "rate for Chicago to Dallas dry van" instantly from my own contracts?
48. Turn carrier email quotes into a private rate index?
49. Rate sheet version control — how do brokers track rate changes?
50. API to extract structured rates from freight documents?

## 측정·손절 기준

- 매주 위 50문항 측정, 주간 인용률(질문 대비 브랜드 언급 비율) 기록.
- 8주 차 기준: 인용률 추세와 무관하게 **유료 전환 3건 미만이면 피벗 검토**
  (강의의 "정직하게 측정" 원칙 — 1~2주 등락으로 판단하지 않는다).

## 가격 설계 (3강 원가·가격 계산법 적용, 2026-07-03 산출)

### 원가 — 인건비 0, 원가는 API + 결제수수료가 전부

| 항목 | 추정치 | 근거 |
|---|---|---|
| 운임표 1장 파싱 (LLM) | ≈ $0.35 | 평균 입력 ~30K + 출력 ~10K 토큰, Sonnet급 단가, 재생성 ×1.5 포함. 보수적 상한 $0.50 |
| 레인 검색 1건 | ≈ $0 | 구조화 후에는 DB 조회 — LLM 불호출 |
| PayPal 구독 수수료 | 3.49% + $0.49/건 | 2026년 구독 결제 기준. 한국 계정 수취 시 국경 간 수수료(~1.5%)와 환전 수수료가 추가되어 **실효 ~5~6%**로 잡음 |
| 개발비 | 1회성 | 고객 수로 나뉘어 0에 수렴 (3강) |

### 가치 기준점 — 원가가 아니라 가치로 매긴다

- 미국 브로커 운영 인력이 운임표 1장을 수기 입력하는 데 1~2시간,
  시급 ~$25 기준 **장당 $25~50의 가치**. 우리 실효 단가는 장당 $1.5~2.5
  수준이라 고객이 느끼는 가치의 1/10 이하 — 가격 저항이 낮다.
- 경쟁 엔터프라이즈 툴(Vooma·Drumkit)은 공개가가 없고 통상 월 $1,000+로
  추정(신뢰도 낮음 — 공개 자료 없음). 셀프서브 $49~299는 그 아래 빈 구간.

### 플랜 (무제한 금지 — 전 플랜 한도제)

| 플랜 | 월 가격 | 한도 | 월 원가(API+수수료) | 마진 |
|---|---|---|---|---|
| Free 체험 | $0 | 운임표 3장 (1회) | ~$1 | 획득 비용으로 간주 |
| Starter | **$49** | 운임표 20장 · 레인 검색 500건 | ~$10 | ~80% |
| Pro | **$149** | 운임표 100장 · 검색 5,000건 · 이메일 인박스 파싱 | ~$43 | ~71% |
| Growth | **$299** | 운임표 300장 · API 접근 · 3시트 | ~$120 | ~60% |

- 한도 초과: 장당 $1.50 (원가의 ~4배) — "무제한 금지" 원칙의 안전판
- 연간 결제: 2개월 무료 (실질 17% 할인) — PayPal 수수료 횟수도 12→1회로 감소
- 검증 순서: Starter 단일 플랜으로 먼저 출시 → 사용 데이터로 한도 보정 후
  Pro/Growth 오픈 (계산하고 출시, 손해 보는 건 안 만듦)

## MVP 스코프 (다음 단계, 별도 SPEC로 진행)

1. 업로드(PDF/XLSX/CSV) → LLM 파싱 → 레인·요율·유효기간·부대비용 구조화
2. 레인 검색("Chicago → Dallas dry van") → 매칭 요율 + 마진 규칙 적용 견적
3. 결제: **PayPal 구독(Subscriptions)** 셀프서브 — 한국 사업자는 Stripe 직접
   가입이 안 되므로 PayPal로 USD 수취. 실효 수수료 ~5~6%는 위 원가에 반영됨
4. 랜딩 페이지: GEO 설계 적용 — 결론 첫 문장, 수치·출처, 비교 리스티클 동반
