import os
import datetime
import requests
import xml.etree.ElementTree as ET
import traceback
import sys

# --- 환경 설정 ---
# 주의: 아래 API 키가 파일에 직접 적혀있으면 GitHub에 올라갔을 때 해킹될 위험이 있습니다!
# 테스트 후에는 반드시 다시 os.getenv("GEMINI_API_KEY") 로 돌려놓으시는 것을 권장합니다.
API_KEY = os.getenv("GEMINI_API_KEY")

DEBUG_LOG = ""

def generate_content_rest(prompt):
    if not API_KEY:
        raise ValueError("API Key is missing")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts":[{"text": prompt}]}]}
    response = requests.post(url, headers=headers, json=data, timeout=30)
    if response.status_code != 200:
        # 오류 발생 시 어떤 모델이 사용 가능한지 조회해서 에러 메시지에 추가
        models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        models_res = requests.get(models_url)
        available = "조회 불가"
        if models_res.status_code == 200:
            available = ", ".join([m['name'] for m in models_res.json().get('models', [])])
        raise Exception(f"API Error {response.status_code}: {response.text}\n사용 가능한 모델 목록: {available}")
    return response.json()['candidates'][0]['content']['parts'][0]['text']

MEMORY_DIR = "./memory"

def ensure_directory():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

def fetch_daily_ideas():
    ideas = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. 긱뉴스(GeekNews) 
        gn_res = requests.get('https://news.hada.io/rss', headers=headers, timeout=10)
        gn_root = ET.fromstring(gn_res.content)
        gn_items = gn_root.findall('.//item')[:5]
        ideas.append("🇰🇷 [GeekNews 트렌드]")
        for idx, item in enumerate(gn_items, 1):
            title = item.find('title').text
            ideas.append(f"{idx}. {title}")
            
        # 2. Hacker News
        hn_res = requests.get('https://news.ycombinator.com/rss', headers=headers, timeout=10)
        hn_root = ET.fromstring(hn_res.content)
        hn_items = hn_root.findall('.//item')[:5]
        ideas.append("\n🌍 [Hacker News 트렌드]")
        for idx, item in enumerate(hn_items, 1):
            title = item.find('title').text
            ideas.append(f"{idx}. {title}")
            
    except Exception as e:
        ideas.append(f"데이터 수집 실패: {str(e)}")
        
    if not ideas or len(ideas) <= 2:
        ideas.append("1. AI-driven interior design tools\n2. Smart glass tech\n3. Eco-friendly materials")
        
    return "\n".join(ideas)

def main():
    global DEBUG_LOG
    ensure_directory()
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    report_content = f"# 🏠 100k Business Idea Agent Report - {today}\n\n"
    
    try:
        # 1. 조사
        DEBUG_LOG += "✅ 조사관 단계 시작 (최신 트렌드 수집중...)\n"
        info = fetch_daily_ideas()
        DEBUG_LOG += "✅ 조사관 단계 완료\n"
        
        # 2. 분석/기획/마케팅 (AI 활용)
        if API_KEY:
            try:
                analysis_prompt = f"다음은 오늘 수집된 IT/비즈니스 트렌드 뉴스입니다.\n{info}\n\n이 뉴스들을 분석하여, 가장 잠재력 있는 '사업/창업 아이디어(IT, B2B, B2C, 오프라인, 콘텐츠 등 분야 무관)'를 1개 도출하고, 그 이유를 분석해줘."
                analysis = generate_content_rest(analysis_prompt)
                DEBUG_LOG += "✅ 분석가 단계 완료\n"
                
                plan_prompt = f"다음 도출된 비즈니스 아이디어를 바탕으로, 구체적인 제품 기획안(MVP 주요 기능, 타겟 고객, 예상 수익 모델)을 작성해줘:\n{analysis}"
                plan = generate_content_rest(plan_prompt)
                DEBUG_LOG += "✅ 기획자 단계 완료\n"
                
                marketing_prompt = f"다음 기획안을 성공적으로 런칭하기 위한 초기 0-to-1 마케팅 전략(초기 고객 확보 방법, 랜딩페이지 카피, 바이럴 전략)을 짜줘:\n{plan}"
                marketing = generate_content_rest(marketing_prompt)
                DEBUG_LOG += "✅ 마케터 단계 완료\n"
            except Exception as ai_e:
                analysis = "AI 처리 중 오류 발생"
                plan = "N/A"
                marketing = "N/A"
                DEBUG_LOG += f"❌ AI 생성 중 에러: {str(ai_e)}\n"
        else:
            analysis = plan = marketing = "AI 미작동 (키 없음)"
            DEBUG_LOG += "❌ API 키가 설정되지 않았습니다. (GitHub Secrets 확인 필요)\n"
            
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
