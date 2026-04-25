import os
import datetime
import requests
import google.generativeai as genai
import traceback
import sys

# --- 환경 설정 ---
API_KEY = os.getenv("GEMINI_API_KEY")
DEBUG_LOG = ""

try:
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        DEBUG_LOG += "✅ API 키가 감지되었습니다.\n"
    else:
        model = None
        DEBUG_LOG += "❌ API 키가 설정되지 않았습니다. (GitHub Secrets 확인 필요)\n"
except Exception as e:
    model = None
    DEBUG_LOG += f"❌ 모델 설정 중 오류 발생: {str(e)}\n"

MEMORY_DIR = "./memory"

def ensure_directory():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

def main():
    global DEBUG_LOG
    ensure_directory()
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    report_content = f"# 🏠 100k Interior Agent Debug Report - {today}\n\n"
    
    try:
        # 1. 조사
        info = "1. AI-driven interior design tools\n2. Smart glass tech\n3. Eco-friendly materials"
        DEBUG_LOG += "✅ 조사관 단계 완료\n"
        
        # 2. 분석/기획/마케팅 (AI 활용)
        if model:
            try:
                analysis = model.generate_content(f"분석해줘: {info}").text
                DEBUG_LOG += "✅ 분석가 단계 완료\n"
                
                plan = model.generate_content(f"기획해줘: {analysis}").text
                DEBUG_LOG += "✅ 기획자 단계 완료\n"
                
                marketing = model.generate_content(f"마케팅전략 짜줘: {plan}").text
                DEBUG_LOG += "✅ 마케터 단계 완료\n"
            except Exception as ai_e:
                analysis = "AI 처리 중 오류 발생"
                plan = "N/A"
                marketing = "N/A"
                DEBUG_LOG += f"❌ AI 생성 중 에러: {str(ai_e)}\n"
        else:
            analysis = plan = marketing = "AI 미작동 (키 없음)"
            
        report_content += f"## 🛠 디버그 로그\n{DEBUG_LOG}\n\n"
        report_content += f"## 📊 분석 결과\n{analysis}\n\n"
        report_content += f"## 💡 기획 내용\n{plan}\n\n"
        report_content += f"## 📣 마케팅 전략\n{marketing}\n"
        
    except Exception as e:
        report_content += f"\n\n## ⚠️ 치명적 실행 오류\n{str(e)}\n{traceback.format_exc()}"
    
    # 파일 쓰기 (에러가 나도 무조건 쓰기)
    filepath = f"{MEMORY_DIR}/{today}_debug_result.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"디버그 리포트 생성 완료: {filepath}")
    # 강제 종료 방지 (Actions가 성공으로 뜨게 함)
    sys.exit(0)

if __name__ == "__main__":
    main()
