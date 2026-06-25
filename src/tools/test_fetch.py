import requests
import xml.etree.ElementTree as ET
import sys

# Windows 및 GitHub Actions 환경 모두에서 UTF-8 출력 보장
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def fetch_daily_ideas():
    ideas = []
    # User-Agent 설정으로 봇 차단 방지
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Hacker News RSS
        response = requests.get('https://news.ycombinator.com/rss', headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')[:5]
        ideas.append("🔥 [Hacker News Top Trends]")
        for idx, item in enumerate(items, 1):
            title = item.find('title').text
            ideas.append(f"{idx}. {title}")
            
        # TechCrunch RSS
        tc_res = requests.get('https://techcrunch.com/feed/', headers=headers, timeout=10)
        tc_root = ET.fromstring(tc_res.content)
        tc_items = tc_root.findall('.//item')[:5]
        ideas.append("\n🚀 [TechCrunch Latest]")
        for idx, item in enumerate(tc_items, 1):
            title = item.find('title').text
            ideas.append(f"{idx}. {title}")
            
    except Exception as e:
        ideas.append(f"데이터 수집 실패: {str(e)}")
        
    if not ideas or len(ideas) <= 2:
        ideas.append("\n대체 아이디어:\n1. AI-driven SaaS\n2. No-code Automation\n3. B2B Lead Gen tools")
        
    return "\n".join(ideas)

print(fetch_daily_ideas())
