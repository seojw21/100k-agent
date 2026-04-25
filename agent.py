import os
import datetime
import requests
import google.generativeai as genai

# --- 환경 설정 ---
# GitHub Secrets에 GEMINI_API_KEY를 등록해야 작동합니다.
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

MEMORY_DIR = "./memory"

def ensure_directory():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

# --- 에이전트 1: 조사관 (Researcher) ---
def agent_researcher():
    print("조사관: 트렌드 탐색 중...")
    # 실제로는 스크래핑 로직이 들어가는 부분 (현재는 고도화된 검색 결과 예시)
    raw_data = """
    1. AI-native vertical SaaS for Legal professionals.
    2. Local SEO tools using hyper-local news.
    3. Senior-care smart home automation.
    4. Micro-SaaS for content repurposing (Short-form).
    5. Emotional consumption (Feelconomy) related F&B.
    """
    return raw_data

# --- 에이전트 2: 분석가 (Analyst) ---
def agent_analyst(raw_data):
    print("분석가: 아이템 평가 및 선정 중...")
    if not model: return "AI API 키가 설정되지 않아 분석을 건너뜁니다."
    
    prompt = f"""
    당신은 전문 비즈니스 분석가입니다. 다음 자료에서 가장 수익성 있고 한국 시장에 적합한 아이템 3개를 골라주세요.
    각 아이템별로 [수익성, 실현가능성, 시장규모]를 10점 만점으로 평가하세요.
    
    자료: {raw_data}
    """
    response = model.generate_content(prompt)
    return response.text

# --- 에이전트 3: 기획자 (Planner) ---
def agent_planner(analysis):
    print("기획자: 사업 모델 설계 중...")
    if not model: return "AI API 키가 설정되지 않아 기획을 건너뜁니다."
    
    prompt = f"""
    당신은 스타트업 기획자입니다. 분석가가 선정한 아이템 중 가장 유망한 하나를 골라 
    MVP(최소기능제품) 기획과 수익 모델을 설계해 주세요.
    
    분석 내용: {analysis}
    """
    response = model.generate_content(prompt)
    return response.text

# --- 에이전트 4: 마케터 (Marketer) ---
def agent_marketer(plan):
    print("마케터: 마케팅 전략 수립 중...")
    if not model: return "AI API 키가 설정되지 않아 마케팅 전략을 건너뜁니다."
    
    prompt = f"""
    당신은 천재 마케터입니다. 다음 사업 계획에 대해 타겟 고객을 정의하고, 
    고객의 마음을 사로잡을 한 줄 카피와 추천 홍보 채널을 제안하세요.
    
    사업 계획: {plan}
    """
    response = model.generate_content(prompt)
    return response.text

# --- 메인 실행 로직 (협업 워크플로우) ---
def run_100k_team():
    ensure_directory()
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # 1. 조사
    raw_info = agent_researcher()
    
    # 2. 분석
    analysis_result = agent_analyst(raw_info)
    
    # 3. 기획
    planning_result = agent_planner(analysis_result)
    
    # 4. 마케팅
    marketing_strategy = agent_marketer(planning_result)
    
    # 리포트 작성
    report = f"""# 🚀 100k Agent Team Report - {today}

## 🔍 [조사관] 오늘 발견한 원시 데이터
{raw_info}

## 📊 [분석가] 시장성 및 수익성 평가
{analysis_result}

## 💡 [기획자] 추천 아이템 및 MVP 설계
{planning_result}

## 📣 [마케터] 타겟팅 및 홍보 전략
{marketing_strategy}

---
*본 리포트는 100k 에이전트 팀에 의해 자동 생성되었습니다.*
"""
    
    filename = f"{MEMORY_DIR}/{today}_team_report.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"팀 리포트 생성 완료: {filename}")

if __name__ == "__main__":
    run_100k_team()
