#!/usr/bin/env python3
"""
script_shorts_v1.py — UK 기업정보 PDF 다운로드 Shorts 영상 스크립트 자동 생성

이 스크립트는:
1. YouTube/Instagram용 Shorts 스크립트 JSON 생성
2. 썸네일 프롬프트 (Midjourney/DALL-E) 생성
3. 해시태그 조합 생성

사용법:
    python script_shorts_v1.py
"""

import json
from datetime import datetime

# === 데이터 정의 ===

COMPANY_DATA = {
    "total_companies": 5_000_000,
    "pdf_percentage": 60,
    "api_rate_limit": "600 requests / 5 minutes",
    "tool_name": "dumpany",
    "tool_stars": 7,
    "tool_url": "https://github.com/pearswick/dumpany",
    "change_date": "2026-04-01",
    "change_description": "iXBRL format mandatory, WebFiling closed"
}

SHORTS_SCRIPT = {
    "title": "UK 기업정보 PDF 대량 다운로드 (dumpany)",
    "duration_seconds": 60,
    "platform": ["Instagram Reels", "YouTube Shorts"],
    "target_audience": ["개발자", "OSINT 연구자", "데이터 분석가"],
    "hook": "영국 기업 500만개 데이터, 60%가 PDF인 이유?",
    "scenes": [
        {
            "time": "0:00-0:05",
            "visual": "Companies House 로고 + '5M companies' 텍스트",
            "narration": "영국에는 500만 개 기업이 등록되어 있습니다.",
            "subtitle": "🇬🇧 UK 기업 500만개"
        },
        {
            "time": "0:05-0:12",
            "visual": "PDF 아이콘 + '60%' 빨간색 강조",
            "narration": "그런데 이 중 60%가 다 PDF예요. 구조화 안 된 데이터죠.",
            "subtitle": "❌ 60%가 PDF?"
        },
        {
            "time": "0:12-0:20",
            "visual": "dumpany GitHub 화면 (7⭐ 표시)",
            "narration": "그래서 개발자가 dumpany라는 도구를 만들었습니다.",
            "subtitle": "🛠️ dumpany (GitHub 7⭐)"
        },
        {
            "time": "0:20-0:35",
            "visual": "터미널 데모: pip install dumpany → 실행",
            "narration": "pip로 설치하고, 회사 번호만 입력하면...",
            "subtitle": "💻 pip install dumpany"
        },
        {
            "time": "0:35-0:45",
            "visual": "다운로드된 PDF 폴더 구조 화면",
            "narration": "Companies House에서 모든 PDF를 한 번에 다운로드합니다.",
            "subtitle": "📥 대량 다운로드 완료"
        },
        {
            "time": "0:45-0:55",
            "visual": "Google NotebookLM 로고 + 'AI 분석' 텍스트",
            "narration": "이 데이터를 NotebookLM에 올리면 AI 분석도 가능하죠.",
            "subtitle": "🤖 AI 분석 연동"
        },
        {
            "time": "0:55-1:00",
            "visual": "CTA 화면: '링크 설명란' + 구독 버튼",
            "narration": "링크는 설명란에 있습니다. 구독하세요!",
            "subtitle": "🔗 설명란 확인 • 구독 👍"
        }
    ],
    "hashtags": [
        "#CompaniesHouse",
        "#UKBusiness",
        "#OSINT",
        "#DataAnalysis",
        "#OpenSource",
        "#GitHub",
        "#Python",
        "#DataScience",
        "#AI",
        "#NotebookLM",
        "#BulkDownload",
        "#PDF",
        "#API",
        "#DeveloperTool"
    ],
    "description": f"""🇬🇧 UK 기업 500만개 데이터, 60%가 PDF인 이유?

dumpany로 Companies House PDF 대량 다운로드하기:
{COMPANY_DATA['tool_url']}

✅ 회사 번호 입력 → 모든 PDF 자동 다운로드
✅ Google NotebookLM 연동 가능
✅ 무료·오픈소스

⏰ Companies House API: 분당 600회 rate limit 주의

#CompaniesHouse #UKBusiness #OSINT #DataAnalysis""",
    "thumbnail_text": {
        "main": "영국 기업 PDF 대량 다운로드",
        "sub": "GitHub 무료 도구"
    }
}

THUMBNAIL_PROMPTS = [
    {
        "style": "데이터 시각화 스타일",
        "prompt": f"Infographic style: UK map with 5 million data points, 60% highlighted in red as PDF icons, clean modern design, blue and white color scheme, professional business look --ar 16:9 --v 6",
        "text_overlay": "왜 60%가 PDF인가?"
    },
    {
        "style": "GitHub 화면 캡처 스타일",
        "prompt": f"Dark mode terminal screen showing GitHub repository page for 'dumpany' with 7 stars, code snippet 'pip install dumpany', clean UI design, tech aesthetic --ar 16:9 --v 6",
        "text_overlay": "무료로 다운로드"
    },
    {
        "style": "타임라인/인포그래픽 스타일",
        "prompt": f"Timeline infographic: 2026.04 → UK company data changes, calendar icon with warning triangle, British flag colors (red, blue, white), clean modern design --ar 16:9 --v 6",
        "text_overlay": "2026년 4월 변경사항"
    }
]

# === 출력 함수 ===

def generate_json_output():
    """Shorts 스크립트 JSON 파일 생성"""
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "author": "질럿 (AI Agent)"
        },
        "script": SHORTS_SCRIPT,
        "company_data": COMPANY_DATA,
        "thumbnail_prompts": THUMBNAIL_PROMPTS
    }
    
    with open('./assets/shorts_script_output.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("✅ shorts_script_output.json 생성 완료")
    return output

def generate_prompt_for_ai():
    """AI 썸네일 생성을 위한 프롬프트 출력"""
    print("\n" + "="*60)
    print("🎨 AI 썸네일 생성 프롬프트 (Midjourney/DALL-E)")
    print("="*60)
    
    for i, prompt in enumerate(THUMBNAIL_PROMPTS, 1):
        print(f"\n--- 썸네일 {i} ---")
        print(f"스타일: {prompt['style']}")
        print(f"프롬프트: {prompt['prompt']}")
        print(f"텍스트 오버레이: {prompt['text_overlay']}")

def generate_hashtag_combos():
    """해시태그 조합 생성"""
    base_tags = SHORTS_SCRIPT['hashtags']
    
    combos = [
        {"name": "개발자 타겟", "tags": ["#Python", "#GitHub", "#OSINT", "#API", "#OpenSource"]},
        {"name": "데이터 분석 타겟", "tags": ["#DataScience", "#DataAnalysis", "#PDF", "#BulkDownload", "#AI"]},
        {"name": "비즈니스 타겟", "tags": ["#UKBusiness", "#CompaniesHouse", "#Startup", "#Consulting", "#BusinessData"]}
    ]
    
    print("\n" + "="*60)
    print("📱 해시태그 조합")
    print("="*60)
    
    for combo in combos:
        print(f"\n{combo['name']}:")
        print(f"  {' '.join(combo['tags'])}")
    
    return combos

# === 메인 실행 ===

if __name__ == "__main__":
    print("🚀 UK 기업정보 PDF 다운로드 Shorts 스크립트 생성 시작")
    print("="*60)
    
    # 1. JSON 출력
    output = generate_json_output()
    
    # 2. 프롬프트 출력
    generate_prompt_for_ai()
    
    # 3. 해시태그 조합
    hashtag_combos = generate_hashtag_combos()
    
    print("\n" + "="*60)
    print("✅ 모든 산출물 생성 완료")
    print("="*60)
