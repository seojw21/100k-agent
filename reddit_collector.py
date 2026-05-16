"""
reddit_collector.py
===================
Reddit RSS 기반 통증 포인트 자동 수집기
- API 키 불필요 (RSS 활용)
- 타겟 서브레딧: SaaS, startups, SideProject, Entrepreneur, indiehackers

실행 방법:
    python reddit_collector.py

결과물:
    knowledge/raw_collected.jsonl   - 수집된 원본 게시물 (JSONL 형식, 누적)
"""

import json
import time
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
RAW_COLLECTED_PATH = KNOWLEDGE_DIR / "raw_collected.jsonl"
COLLECTED_IDS_PATH = KNOWLEDGE_DIR / "collected_ids.json"

# ─────────────────────────────────────────────
# 수집 대상 서브레딧 (통증 포인트 밀도 높은 곳)
# ─────────────────────────────────────────────
TARGET_SUBREDDITS = [
    "SaaS",
    "startups",
    "SideProject",
    "Entrepreneur",
    "indiehackers",
    "smallbusiness",
    "freelance",
    "digitalnomad",
]

# 통증 신호 키워드 (이 단어가 있는 게시물 우선 수집)
PAIN_SIGNAL_KEYWORDS = [
    # 영어
    "frustrated", "annoyed", "pain", "struggle", "wish there was",
    "anyone else", "hate when", "problem with", "so hard to",
    "is there a tool", "alternative to", "how do i", "best way to",
    "wasting time", "manual process", "keep forgetting", "impossible to",
    # 한국어
    "불편", "힘들어", "짜증", "문제", "도구가 없", "방법이 없",
]

def get_url_id(url: str) -> str:
    """URL에서 고유 ID 추출"""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def load_collected_ids() -> set:
    """이미 수집된 ID 목록 로드 (중복 방지)"""
    if COLLECTED_IDS_PATH.exists():
        with open(COLLECTED_IDS_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_collected_ids(ids: set):
    """수집된 ID 목록 저장"""
    with open(COLLECTED_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(ids), f)

def has_pain_signal(text: str) -> bool:
    """텍스트에 통증 신호 키워드가 있는지 확인"""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in PAIN_SIGNAL_KEYWORDS)

def fetch_subreddit_rss(subreddit: str, limit: int = 25) -> list[dict]:
    """서브레딧 RSS 피드 수집"""
    url = f"https://www.reddit.com/r/{subreddit}/hot.rss?limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 KnowledgeBot/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"  ⚠️ r/{subreddit}: HTTP {response.status_code}")
            return []
        
        root = ET.fromstring(response.content)
        
        # RSS 네임스페이스 처리
        ns = {
            "": "http://www.w3.org/2005/Atom",
            "media": "http://search.yahoo.com/mrss/",
        }
        
        items = []
        
        # Atom 형식 파싱
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for entry in entries:
            title_el = entry.find("{http://www.w3.org/2005/Atom}title")
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            content_el = entry.find("{http://www.w3.org/2005/Atom}content")
            updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
            author_el = entry.find(".//{http://www.w3.org/2005/Atom}name")
            
            title = title_el.text if title_el is not None else ""
            url_val = link_el.get("href", "") if link_el is not None else ""
            content = content_el.text if content_el is not None else ""
            updated = updated_el.text if updated_el is not None else ""
            author = author_el.text if author_el is not None else ""
            
            # HTML 태그 간단 제거
            import re
            content_clean = re.sub(r"<[^>]+>", " ", content or "").strip()
            content_clean = re.sub(r"\s+", " ", content_clean)[:1000]
            
            if not title or not url_val:
                continue
            
            item = {
                "id": get_url_id(url_val),
                "subreddit": subreddit,
                "title": title,
                "url": url_val,
                "content": content_clean,
                "author": author,
                "published_at": updated,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "has_pain_signal": has_pain_signal(title + " " + content_clean),
            }
            items.append(item)
        
        # 일반 RSS 형식도 시도 (fallback)
        if not items:
            rss_items = root.findall(".//item")
            for rss_item in rss_items:
                title_el = rss_item.find("title")
                link_el = rss_item.find("link")
                desc_el = rss_item.find("description")
                date_el = rss_item.find("pubDate")
                
                title = title_el.text if title_el is not None else ""
                url_val = link_el.text if link_el is not None else ""
                content = desc_el.text if desc_el is not None else ""
                published = date_el.text if date_el is not None else ""
                
                import re
                content_clean = re.sub(r"<[^>]+>", " ", content or "").strip()[:1000]
                
                if not title or not url_val:
                    continue
                
                item = {
                    "id": get_url_id(url_val),
                    "subreddit": subreddit,
                    "title": title,
                    "url": url_val,
                    "content": content_clean,
                    "author": "",
                    "published_at": published,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "has_pain_signal": has_pain_signal(title + " " + content_clean),
                }
                items.append(item)
        
        return items
        
    except ET.ParseError as e:
        print(f"  ❌ r/{subreddit} XML 파싱 에러: {e}")
        return []
    except Exception as e:
        print(f"  ❌ r/{subreddit} 수집 에러: {e}")
        return []

def collect_all(only_pain_signals: bool = False) -> tuple[list[dict], int]:
    """모든 서브레딧에서 신규 게시물 수집"""
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    
    collected_ids = load_collected_ids()
    new_items = []
    duplicate_count = 0
    
    for subreddit in TARGET_SUBREDDITS:
        print(f"  📡 r/{subreddit} 수집 중...")
        items = fetch_subreddit_rss(subreddit)
        
        for item in items:
            if item["id"] in collected_ids:
                duplicate_count += 1
                continue
            
            # 통증 신호 필터 (선택적)
            if only_pain_signals and not item["has_pain_signal"]:
                continue
            
            new_items.append(item)
            collected_ids.add(item["id"])
        
        print(f"    → {len(items)}개 수집, {len([i for i in items if i['id'] not in collected_ids - {i['id']}])}개 신규")
        time.sleep(1)  # Rate limiting
    
    # 신규 항목 JSONL에 추가
    if new_items:
        with open(RAW_COLLECTED_PATH, "a", encoding="utf-8") as f:
            for item in new_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        save_collected_ids(collected_ids)
    
    return new_items, duplicate_count

def main():
    print("=" * 60)
    print(f"🤖 Reddit 자동 수집 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    new_items, dupes = collect_all(only_pain_signals=False)
    
    pain_count = sum(1 for i in new_items if i["has_pain_signal"])
    
    print(f"\n📊 수집 결과:")
    print(f"  신규 게시물: {len(new_items)}개")
    print(f"  통증 신호 포함: {pain_count}개")
    print(f"  중복 스킵: {dupes}개")
    print(f"  저장 위치: {RAW_COLLECTED_PATH}")
    
    return new_items

if __name__ == "__main__":
    main()
