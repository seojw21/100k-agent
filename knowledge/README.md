# Knowledge

## pain_db.json
- 레코드: 3501
- 점수 분포: {10: 1152, 9: 1363, 8: 754, 7: 157, 6: 35, 3: 1, 0: 39}
- **유지 이유:** 시장 통증 검색·카피 재료 (점수 8+ 우선 사용)
- 재인덱싱: 로컬에서 chroma 재생성 (이 레포에는 chroma 커밋 안 함)

## 사용 규칙
1. 에이전트 기본 컨텍스트: goals + identity + business/* + pain 고점수
2. sessions 전체 덤프 금지 — 쓸 만한 산출만 business/ 로 승격
3. raw 로그·chroma·ideas 덤프는 이 레포에 다시 넣지 말 것
