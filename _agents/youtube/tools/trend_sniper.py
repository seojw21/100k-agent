#!/usr/bin/env python3
"""Trend Sniper — pulls top YouTube videos for target keywords, asks a local
LLM (Ollama/LM Studio) to extract the algorithmic patterns, and writes a
planning report next to this script.

Shared keys (API key, OLLAMA_URL, MODEL) come from youtube_account.json so
you only set them once. Per-tool keys (TARGET_KEYWORDS) come from
trend_sniper.json. If a key exists in both, trend_sniper.json wins.

Requires:  pip install google-api-python-client requests
"""
import os, json, time, random, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "trend_sniper.json")
ACCOUNT_PATH = os.path.join(HERE, "youtube_account.json")
REPORT_PATH = os.path.join(HERE, "trend_sniper_report.md")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 설정 파일을 읽을 수 없어요: {CONFIG_PATH}\n{e}")
        sys.exit(1)

def load_account():
    try:
        if os.path.exists(ACCOUNT_PATH):
            with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _shared(cfg, acct, key, default=""):
    """Per-tool config wins; falls back to shared account; finally default."""
    v = cfg.get(key)
    if v not in (None, "", []):
        return v
    v = acct.get(key)
    if v not in (None, "", []):
        return v
    return default

def main():
    cfg = load_config()
    acct = load_account()
    api_key = (_shared(cfg, acct, "YOUTUBE_API_KEY") or "").strip()
    target_keywords = cfg.get("TARGET_KEYWORDS", [])
    if not target_keywords:
        print("⚠️  TARGET_KEYWORDS가 비어있어요. 분석할 키워드를 1개 이상 추가하세요.")
        sys.exit(1)
    ollama_url = (_shared(cfg, acct, "OLLAMA_URL", "http://127.0.0.1:11434") or "http://127.0.0.1:11434").rstrip("/")
    model = _shared(cfg, acct, "MODEL", "") or ""
    pick = min(2, len(target_keywords))
    chosen = random.sample(target_keywords, pick)

    try:
        import requests
    except ImportError:
        print("❌ requests가 설치되지 않았어요. pip install requests")
        sys.exit(1)

    is_mock = False
    if not api_key:
        print("⚠️  YOUTUBE_API_KEY가 비어있어 모킹(Mock) 모드로 동작합니다.")
        print("   실제 데이터 수집을 원하시면 youtube_account.json 또는 trend_sniper.json에 API 키를 입력하세요.")
        is_mock = True

    sniper_data = []
    print(f"\n🎯 [트렌드 스나이퍼] 키워드 {chosen} 스캔 시작...")

    if is_mock:
        mock_templates = [
            "초보자도 10분 만에 따라하는 실전 가이드",
            "이걸 모르면 평생 후회합니다 (업계 비밀 대공개)",
            "2026년 가장 핫한 트렌드 분석 및 전망",
            "1인 창업자가 반드시 써야 할 필수 도구 TOP 5",
            "조회수 폭발하는 비법과 실제 적용 사례 공유",
            "기초부터 고급까지 단숨에 마스터하기",
            "하루 30분 투자해서 생산성 200% 올리는 노하우"
        ]
        for q in chosen:
            print(f"📡 [{q}] 모의 데이터(Mock) 생성 중...")
            time.sleep(0.5)
            selected_templates = random.sample(mock_templates, min(5, len(mock_templates)))
            for idx, tpl in enumerate(selected_templates):
                title = f"{q} - {tpl}"
                channel = f"크리에이터_{random.randint(10, 99)}"
                sniper_data.append(f"[{q}] 채널: {channel} | 제목: {title}")
    else:
        try:
            from googleapiclient.discovery import build
        except ImportError:
            print("❌ google-api-python-client가 설치되지 않았어요.")
            print("   설치: pip install google-api-python-client requests")
            sys.exit(1)

        youtube = build('youtube', 'v3', developerKey=api_key)
        last_month = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat("T") + "Z"
        for q in chosen:
            print(f"📡 [{q}] 검색 중...")
            try:
                req = youtube.search().list(
                    part="snippet", q=q, maxResults=5, order="viewCount",
                    publishedAfter=last_month, type="video"
                )
                res = req.execute()
                for item in res.get('items', []):
                    title = item['snippet']['title']
                    channel = item['snippet']['channelTitle']
                    sniper_data.append(f"[{q}] 채널: {channel} | 제목: {title}")
            except Exception as e:
                print(f"❌ 검색 오류 ({q}): {e}")

    if not sniper_data:
        print("❌ 수집된 데이터 없음. API 키 한도/네트워크 확인.")
        sys.exit(1)

    data_text = "\n".join(sniper_data)
    prompt = f"""당신은 유튜브 알고리즘 마스터마인드입니다. 아래는 최근 30일 떡상 영상입니다.

[키워드] {', '.join(chosen)}
[데이터]
{data_text}

분석해서 마크다운 보고서를 작성하세요. 반드시 3섹션:
1. 🌍 트렌드 해킹 분석 — 어떤 패턴이 조회수를 끌고 있는지
2. 🎯 빈집 털기 전략 — 차별화 가능한 틈새 주제
3. 🎬 파괴적 영상 기획안 — 썸네일 카피, 제목 3개, 후킹 오프닝(첫 5초)
"""

    print("🧠 [LLM 분석 중...]")
    if not model:
        # Try first available model
        try:
            r = requests.get(f"{ollama_url}/api/tags", timeout=5)
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            if not models:
                print("❌ 로컬 LLM에 설치된 모델이 없어요. Ollama/LM Studio에서 모델을 풀(pull)하세요.")
                sys.exit(1)
            model = models[0]
        except Exception as e:
            print(f"❌ 로컬 LLM 연결 실패 ({ollama_url}): {e}")
            sys.exit(1)

    try:
        r = requests.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=180,
        )
        r.raise_for_status()
        report = r.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ LLM 호출 실패: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print(report)
    print("="*60)

    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n\n# 🎯 트렌드 스나이핑 보고서 — {now}\n")
        f.write(f"## 📡 키워드: {', '.join(chosen)}\n\n")
        f.write(report)
        f.write("\n\n---\n")
    print(f"\n✅ 보고서 저장: {REPORT_PATH}")

if __name__ == "__main__":
    main()
