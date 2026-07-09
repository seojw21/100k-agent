# RateParse — 실브로커 진출 플레이북 (2026-07-05)

> 타겟: 미국 1~10인 소규모 freight broker / 3PL. 채널: Reddit, 브로커 커뮤니티, 직접 아웃리치.
> 원칙(강의): 홍보문이 아니라 "결과를 파는" 톤 + build-in-public 신뢰. Reddit은 노골적 광고를 밴한다.

---

## 0. 진출 전 필수 체크 (오늘)

- [ ] PayPal 라이브 전환 — **실결제를 받으려면 필수**. 지금은 샌드박스라 진짜 돈이 안 들어온다.
      (진출과 병행 가능하나, 첫 관심 고객이 결제 시도하기 전엔 끝나야 함)
- [ ] 실브로커 운임표 샘플 3~5장 확보 → 파싱 정확도 실측 (아래 2번이 이걸 겸함)
- [ ] Reddit 계정 준비: 신규 계정은 스팸 취급됨. 최소 2~3주간 일반 댓글로 karma를 쌓은
      계정이 필요. 없으면 지금부터 매일 freight 관련 스레드에 진짜 도움되는 댓글부터.

---

## 1. 채널별 우선순위

| 채널 | 성격 | 접근법 | 우선도 |
|---|---|---|---|
| **r/FreightBrokers** | 소규모 브로커 밀집 | 질문 답변 + 도구 언급(요청 시) | 1 |
| **r/freightbrokering, r/logistics** | 인접 | 보조 | 2 |
| **FreightWaves 커뮤니티 / LinkedIn 그룹** | 업계 전문 | 콘텐츠 공유 | 2 |
| **직접 아웃리치 (콜드 DM/이메일)** | 1:1 | 운임표 파싱 무료 체험 제안 | 3 (전환율 높지만 노동집약) |

---

## 2. 실브로커 운임표 확보 = 정확도 검증 (진출과 동시)

진짜 브로커 운임표 없이 진출하면 첫 사용자의 실파일에서 파싱이 깨질 위험. 확보 방법:

1. **r/FreightBrokers에 "도움 요청" 톤 게시** (홍보 아님):
   > "I built a tool that turns carrier rate sheets (PDF/Excel) into a searchable
   > lane database. I want to make sure it handles real-world messy sheets, not just
   > clean ones. If anyone's willing to share a (redacted / fake-rate) sample sheet,
   > I'll run it and send back the structured output — free, no signup. Trying to
   > find where it breaks."
   → 샘플도 얻고, 관심 있는 첫 사용자도 얻고, 커뮤니티에 "만드는 사람"으로 각인.

2. 공개된 캐리어 운임표 예시(구글 "carrier rate sheet sample filetype:pdf")로 보조 테스트.

3. 확보한 샘플로 파싱 → 실원가 계측(방금 배포) 데이터 첫 수집 → 마진 실측.

---

## 3. Reddit 게시 원칙 (밴 안 당하려면)

- **첫 게시는 절대 "가입하세요/제 사이트" 아님.** 질문에 진짜 답을 하고, 관련될 때만 도구를 "I made X" 형태로.
- 9:1 규칙 — 자기 것 언급 1번당 순수 도움 9번.
- 가격·링크는 물어보면 답하는 형태가 안전. 본문에 링크 도배 금지.
- "build in public" 톤: 실패·한계도 공개(강의 EP.01/03 원칙). "아직 carrier명 추출은 약해요" 같은 정직함이 신뢰를 만든다.

---

## 4. 핵심 메시지 (어디서든 일관)

- 한 줄: **"Upload a carrier rate sheet, get a searchable lane database and instant quotes. $49/mo, no sales call."**
- 차별점: 경쟁사(Vooma/Drumkit/Pallet)는 전부 **데모 요청·엔터프라이즈 영업**. 우리는 카드 긁고 바로 씀.
- 결과 중심(강의): "AI 파싱" 말고 **"흐린 PDF → 견적 몇 초"**. 랜딩의 Before→After가 그 증거.

---

## 5. 첫 2주 실행 리스트

| 일차 | 할 일 |
|---|---|
| 1~3 | Reddit karma 쌓기(진짜 댓글), PayPal 라이브 전환 |
| 4~5 | 운임표 샘플 요청 게시 → 샘플 수집 → 정확도 실측·수정 |
| 6~10 | 답변 페이지 배치 2 배포(SEO/GEO 유입 축적), 주간 GEO 벤치마크 |
| 11~14 | 관심 보인 사람에게 무료 체험 안내, 첫 유료 전환 시도 |

## 6. 측정 (블루프린트 손절 기준과 연결)

- 8주 차 유료 전환 3건 미만 → 피벗 검토([[후보군.md]]의 idea_975 1순위).
- 주간 기록: GEO 인용률, Reddit 게시 반응(업보트/댓글/DM), 가입·유료 전환, 평균 파싱 실원가.
