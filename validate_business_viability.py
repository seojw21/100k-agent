"""
validate_business_viability.py
==============================
레딧 핵심통증 10점짜리 아이디어들의 사업성(BVI)을 5대 평가 기준으로 심층 검증하는 AI 에이전트 스크립트.

평가 기준 (5대 차원, 각 10점 만점):
  1. 시장 규모 및 확장성 (Market Scale & Growth)
  2. 지불 의사 및 고통의 크기 (Willingness to Pay)
  3. 1인 개발/운영 용이성 (Solopreneur Feasibility)
  4. 진입 장벽 및 모방 난이도 (Defensibility & Moat)
  5. 신속한 출시 가능성 (Time to Market)
"""

import os
import json
import sys
import requests
from pathlib import Path

# 출력 인코딩 설정
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent
PAIN_DB_PATH = BASE_DIR / "knowledge" / "pain_db.json"
CONFIG_PATH = Path("/Users/seojeong-won/Library/Application Support/connect-ai-desktop/connect-ai-config.json")

def get_gemini_api_key() -> str:
    """설정 파일 또는 환경변수에서 Gemini API 키 추출"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                key = cfg.get("apiKeys", {}).get("gemini")
                if key and not key.startswith("YOUR_"):
                    return key
        except Exception as e:
            print(f"⚠️ 설정 파일 읽기 실패: {e}")
            
    # 환경변수 폴백
    key = os.getenv("GEMINI_API_KEY")
    if key and not key.startswith("YOUR_"):
        return key
        
    return ""  # 기본 키 비워둠 (환경변수/설정 필수)

def call_gemini(prompt: str, api_key: str) -> str:
    """Gemini API 호출"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ API 에러 (Status {response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ API 호출 예외 발생: {e}")
    return ""

def clean_json_response(text: str) -> dict:
    """Gemini가 반환한 마크다운 코드 블록 제거 및 JSON 파싱"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)

def evaluate_idea(idea: dict, api_key: str) -> dict:
    """단일 아이디어 사업성 검증"""
    prompt = f"""You are an elite venture capitalist and serial solopreneur. 
Analyze the following business idea from a startup perspective and score it rigorously.

[Idea Details]
- Name: {idea.get('idea_name')}
- Category: {idea.get('category')}
- Pain Point: {idea.get('pain_point')}
- Solution: {idea.get('solution')}
- Monetization Evidence: {idea.get('monetization')}

Evaluate the business viability based on 5 dimensions (Score 1 to 10 for each, 10 being the best):
1. Market Scale (market_scale): Is the target market large enough, and does it have clear expansion/scaling potential?
2. Willingness to Pay (willingness_to_pay): Is the customer's pain intense enough that they will readily pay for a solution?
3. Solopreneur Feasibility (solopreneur_feasibility): Can a single developer build, launch, and operate this within 2-3 months?
4. Defensibility/Moat (defensibility): How hard is it for copycats to steal the market? Does it allow building a network effect or data moat?
5. Time to Market (time_to_market): Can a minimal viable product (MVP) be launched rapidly to get immediate feedback?

Please output your response as a valid JSON object strictly containing the following keys (DO NOT output any introductory or concluding text, only the JSON block):
{{
  "market_scale": 8,
  "willingness_to_pay": 9,
  "solopreneur_feasibility": 7,
  "defensibility": 5,
  "time_to_market": 9,
  "total_score": 38,
  "evaluation_summary": "1. Market: ...\\n2. Monetization: ...\\n3. Feasibility: ...\\n4. Defensibility: ...\\n5. Launch: ..."
}}
"""
    response_text = call_gemini(prompt, api_key)
    if not response_text:
        return {}
    
    try:
        result = clean_json_response(response_text)
        # 가중치 계산 (100점 만점 환산)
        # total_score = (sum of 5 dimensions) * 2
        raw_sum = (
            result.get("market_scale", 5) +
            result.get("willingness_to_pay", 5) +
            result.get("solopreneur_feasibility", 5) +
            result.get("defensibility", 5) +
            result.get("time_to_market", 5)
        )
        result["bvi_index"] = raw_sum * 2  # 100점 만점 지수
        return result
    except Exception as e:
        print(f"❌ JSON 파싱 에러: {e}")
        return {}

def main():
    print("=" * 60)
    print("🚀 레딧 10점 아이디어 사업성 심층 검증 시스템 시작")
    print("=" * 60)
    
    api_key = get_gemini_api_key()
    if not api_key:
        print("❌ Gemini API 키를 찾을 수 없습니다. 환경변수 또는 설정 파일을 확인하세요.")
        sys.exit(1)
        
    if not PAIN_DB_PATH.exists():
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {PAIN_DB_PATH}")
        sys.exit(1)
        
    with open(PAIN_DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    # 점수 10점짜리 고유 아이디어 필터링
    ideas_10 = [r for r in db if int(r.get("score", 0)) == 10]
    print(f"✅ 총 {len(db)}개 아이디어 중 10점 만점 아이디어: {len(ideas_10)}개 감지됨")
    
    # 카테고리 출력 및 사용자에게 카테고리 입력 유도 (기본값은 AI_자동화)
    categories = {}
    for r in ideas_10:
        cat = r.get("category", "기타")
        categories[cat] = categories.get(cat, 0) + 1
        
    print("\n📊 10점 아이디어 카테고리 분포:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {count}개")
        
    # 스크립트 실행 시 인자를 받거나, 기본적으로 카테고리를 설정하여 실행
    target_category = "AI_자동화"
    if len(sys.argv) > 1:
        target_category = sys.argv[1]
        
    print(f"\n🎯 대상 카테고리: [{target_category}]")
    filtered_ideas = [r for r in ideas_10 if r.get("category") == target_category]
    
    if not filtered_ideas:
        print(f"⚠️ 해당 카테고리에 맞는 10점 아이디어가 없습니다. 다른 카테고리를 지정하세요.")
        sys.exit(0)
        
    eval_count = min(5, len(filtered_ideas))
    print(f"🔎 상위 {eval_count}개 아이디어의 심층 사업성 평가를 시작합니다...")
    
    evaluated_results = []
    for idx, idea in enumerate(filtered_ideas[:eval_count], 1):
        print(f"\n[{idx}/{eval_count}] Evaluating: {idea.get('idea_name')}")
        eval_result = evaluate_idea(idea, api_key)
        if eval_result:
            eval_result["idea_name"] = idea.get("idea_name")
            eval_result["pain_point"] = idea.get("pain_point")
            eval_result["solution"] = idea.get("solution")
            eval_result["monetization"] = idea.get("monetization")
            eval_result["url"] = idea.get("url")
            evaluated_results.append(eval_result)
            
    # BVI 지수 순으로 정렬
    evaluated_results.sort(key=lambda x: -x.get("bvi_index", 0))
    
    # 보고서 경로 동적 생성
    report_path = BASE_DIR / f"business_evaluation_report_{target_category}.md"
    
    # 보고서 작성
    print(f"\n💾 사업성 검증 보고서 작성 중... ({report_path.name})")
    
    markdown_lines = [
        f"# 📈 [{target_category}] 분야 사업성 심층 검증 보고서 (BVI)",
        f"> 본 보고서는 Reddit의 10점 만점 통증 아이디어를 바탕으로 시장성, 지불의사, 개발 용이성 등을 다차원 분석한 결과입니다.",
        "",
        "## 📊 사업성 평가 요약 비교표",
        "| 순위 | 아이디어명 | BVI 지수 | 시장 규모 | 지불 의사 | 개발 용이성 | 모방 장벽 | 출시 속도 |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]
    
    for rank, res in enumerate(evaluated_results, 1):
        markdown_lines.append(
            f"| {rank} | {res['idea_name']} | **{res['bvi_index']} / 100** | {res['market_scale']}/10 | {res['willingness_to_pay']}/10 | {res['solopreneur_feasibility']}/10 | {res['defensibility']}/10 | {res['time_to_market']}/10 |"
        )
        
    markdown_lines.extend([
        "",
        "---",
        "",
        "## 🔍 아이디어별 세부 분석 보고서",
        ""
    ])
    
    for rank, res in enumerate(evaluated_results, 1):
        markdown_lines.extend([
            f"### #{rank}. {res['idea_name']}",
            f"- **BVI 사업성 지수:** {res['bvi_index']} / 100",
            f"- **원문 링크:** [{res['url']}]({res['url']})",
            "",
            "#### 😟 문제와 해결책 요약",
            f"* **핵심 통증:** {res['pain_point']}",
            f"* **제안 솔루션:** {res['solution']}",
            f"* **수익화 근거:** {res['monetization']}",
            "",
            "#### 🧠 AI 심층 평가 코멘트",
            f"```text",
            f"{res['evaluation_summary']}",
            f"```",
            ""
        ])
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))
        
    print(f"🎉 검증 보고서 생성 완료! {report_path}")

if __name__ == "__main__":
    main()
