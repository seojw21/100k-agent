import os
import datetime
import requests
import google.generativeai as genai
import traceback

# --- 환경 설정 ---
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"AI 모델 설정 오류: {e}")
        model = None
else:
    print("경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    model = None

MEMORY_DIR = "./memory"

def ensure_directory():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

# --- 에이전트 1: 조사관 (Researcher) - 인테리어 특화 ---
def agent_researcher():
    print("조사관: 인테리어 및 홈테크 트렌드 탐색 중...")
    # 인테리어 관련 키워드로 데이터 수집 (예시 데이터)
    raw_data = """
    1. AI-driven interior design consultation tools for DIYers.
    2. Smart film/glass technology for privacy and energy saving.
    3. Eco-friendly, sustainable building materials for home renovation.
    4. Modular interior systems for 1-person households in Korea.
    5. VR/AR home styling platforms (Virtual staging).
    6. 1인 가구 특화 인테리어 패키지 및 구독 서비스.
    7. 노후 주택 단열 및 창호 교체 관련 정부 지원금 연계 비즈니스.
    """
    return raw_data

# --- 에이전트 2: 분석가 (Analyst) ---
def agent_analyst(raw_data):
    print("분석가: 인테리어 시장 분석 중...")
    if not model: return "AI API 키가 없어 분석을 건너뜁니다."
    
    prompt = f"""
    당신은 인테리어 산업 전문 비즈니스 분석가입니다. 다음 자료에서 한국의 1인 기업가가 
    소자본으로 시작하기 가장 좋은 아이템 3개를 선정하세요.
    수익성, 실행 용이성, 그리고 최근 한국의 인테리어 트렌드(단기 시공, 부분 인테리어 등)를 고려하세요.
    
    자료: {raw_data}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"분석 중 오류 발생: {e}"

# --- 에이전트 3: 기획자 (Planner) ---
def agent_planner(analysis):
    print("기획자: 인테리어 비즈니스 모델 설계 중...")
    if not model: return "AI API 키가 없어 기획을 건너뜁니다."
    
    prompt = f"""
    당신은 인테리어 스타트업 기획자입니다. 분석 내용 중 1위를 선정하여 
    구체적인 서비스 흐름, 수익 구조, 그리고 '첫 고객'을 모으는 방법을 설계하세요.
    
    분석 내용: {analysis}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"기획 중 오류 발생: {e}"

# --- 에이전트 4: 마케터 (Marketer) ---
def agent_marketer(plan):
    print("마케터: 인테리어 마케팅 전략 수립 중...")
    if not model: return "AI API 키가 없어 마케팅 전략을 건너뜁니다."
    
    prompt = f"""
    당신은 인테리어 전문 마케터입니다. 위 사업 계획에 대해 
    '오늘 바로 인스타그램/당근마켓에 올릴 수 있는 홍보 문구'와 '비주얼 전략'을 제안하세요.
    
    사업 계획: {plan}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"마케팅 전략 수립 중 오류 발생: {e}"

# --- 메인 실행 로직 ---
def run_100k_team():
    try:
        ensure_directory()
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        raw_info = agent_researcher()
        analysis_result = agent_analyst(raw_info)
        planning_result = agent_planner(analysis_result)
        marketing_strategy = agent_marketer(planning_result)
        
        report = f"""# 🏠 100k Interior Agent Report - {today}

## 🔍 [조사관] 인테리어 트렌드 원시 데이터
{raw_info}

## 📊 [분석가] 인테리어 시장 분석 및 TOP 3
{analysis_result}

## 💡 [기획자] 추천 비즈니스 MVP 설계
{planning_result}

## 📣 [마케터] 인테리어 홍보 전략 및 문구
{marketing_strategy}

---
*본 리포트는 100k 인테리어 에이전트 팀에 의해 생성되었습니다.*
"""
        
        filename = f"{MEMORY_DIR}/{today}_interior_report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"인테리어 팀 리포트 생성 완료: {filename}")
        
    except Exception as e:
        print("최종 실행 중 오류 발생:")
        traceback.print_exc()
        exit(1) # 에러 발생 시 종료 코드 1 반환

if __name__ == "__main__":
    run_100k_team()
