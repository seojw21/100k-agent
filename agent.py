import os
import datetime
import requests
import google.generativeai as genai
import traceback
import sys

# --- 환경 설정 ---
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        # 최신 모델인 gemini-1.5-flash를 사용합니다.
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("AI 모델 설정 완료 (gemini-1.5-flash)")
    except Exception as e:
        print(f"AI 모델 설정 중 치명적 오류: {e}")
        model = None
else:
    print("경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    model = None

MEMORY_DIR = "./memory"

def ensure_directory():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

# --- 에이전트 1: 조사관 (Researcher) ---
def agent_researcher():
    print("조사관: 인테리어 비즈니스 트렌드 탐색 중...")
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
    if not model: return "AI 분석 불가: 모델이 설정되지 않았습니다."
    print("분석가: 시장성 분석 중...")
    prompt = f"인테리어 비즈니스 전문가로서 다음 데이터를 분석해 한국 1인 기업에게 적합한 TOP 3를 선정하세요: {raw_data}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"분석 에러: {str(e)}"

# --- 에이전트 3: 기획자 (Planner) ---
def agent_planner(analysis):
    if not model: return "AI 기획 불가: 모델이 설정되지 않았습니다."
    print("기획자: MVP 설계 중...")
    prompt = f"위 분석 결과 중 1위를 골라 구체적인 1인 기업용 사업 모델을 기획하세요: {analysis}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"기획 에러: {str(e)}"

# --- 에이전트 4: 마케터 (Marketer) ---
def agent_marketer(plan):
    if not model: return "AI 마케팅 불가: 모델이 설정되지 않았습니다."
    print("마케터: 홍보 전략 수립 중...")
    prompt = f"위 사업 계획에 대한 인스타그램/당근마켓 타겟 홍보 문구를 작성하세요: {plan}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"마케팅 에러: {str(e)}"

# --- 실행부 ---
def main():
    try:
        ensure_directory()
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        info = agent_researcher()
        analysis = agent_analyst(info)
        plan = agent_planner(analysis)
        marketing = agent_marketer(plan)
        
        report = f"# 🏠 100k Interior Agent Team Report - {today}\n\n"
        report += f"## 🔍 [조사관] 데이터\n{info}\n\n"
        report += f"## 📊 [분석가] 분석\n{analysis}\n\n"
        report += f"## 💡 [기획자] 기획\n{plan}\n\n"
        report += f"## 📣 [마케터] 마케팅\n{marketing}\n"
        
        filepath = f"{MEMORY_DIR}/{today}_interior_report.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"성공: {filepath}")
        
    except Exception as e:
        print(f"실행 중 치명적 오류 발생: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
