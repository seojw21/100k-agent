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
    if not api_key:
        print("⚠️  YOUTUBE_API_KEY가 비어있어요. youtube_account.json 또는 trend_sniper.json에 입력하세요.")
        print("   발급: https://console.cloud.google.com/ → YouTube Data API v3 사용 설정 → 사용자 인증 정보 → API 키")
        sys.exit(1)
    target_keywords = cfg.get("TARGET_KEYWORDS", [])
    if not target_keywords:
        print("⚠️  TARGET_KEYWORDS가 비어있어요. 분석할 키워드를 1개 이상 추가하세요.")
        sys.exit(1)
    lm_studio_url = (_shared(cfg, acct, "LM_STUDIO_URL") or _shared(cfg, acct, "LLM_URL") or _shared(cfg, acct, "OLLAMA_URL") or "http://127.0.0.1:1234").rstrip("/")
    if "11434" in lm_studio_url:
        lm_studio_url = lm_studio_url.replace("11434", "1234")
    model = _shared(cfg, acct, "MODEL", "") or ""
    pick = min(2, len(target_keywords))
    chosen = random.sample(target_keywords, pick)

    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ google-api-python-client가 설치되지 않았어요.")
        print("   설치: pip install google-api-python-client requests")
        sys.exit(1)
    try:
        import requests
    except ImportError:
        print("❌ requests가 설치되지 않았어요. pip install requests")
        sys.exit(1)

    print(f"\n🎯 [트렌드 스나이퍼] 키워드 {chosen} 스캔 시작...")
    youtube = build('youtube', 'v3', developerKey=api_key)
    last_month = (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(days=30)).isoformat("T") + "Z"
    sniper_data = []
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

    print(f"🧠 [LLM 분석 중... 엔진: LM Studio]")

    report = ""
    # 모델 자동 선택 — LM Studio 전용 (OpenAI 호환 API /v1/models)
    if not model:
        try:
            base = lm_studio_url
            if not base.endswith('/v1'):
                base = base + '/v1'
            r = requests.get(f"{base}/models", timeout=5)
            r.raise_for_status()
            models = [m["id"] for m in r.json().get("data", [])]
            if not models:
                print(f"❌ LM Studio에 활성화된 모델이 없어요. LM Studio에서 모델을 로드하세요.")
                model = None
            else:
                model = models[0]
                print(f"   자동 선택 모델: {model}")
        except Exception as e:
            print(f"❌ LM Studio 연결 실패 ({lm_studio_url}): {e}")
            print(f"   엔진 실행 확인: LM Studio (포트 1234 또는 설정 포트)")
            model = None

    # 추론 호출 — LM Studio 전용
    if model:
        max_retries = 3
        retry_delay = 10
        for attempt in range(max_retries):
            try:
                base = lm_studio_url
                if not base.endswith('/v1'):
                    base = base + '/v1'
                r = requests.post(
                    f"{base}/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "max_tokens": 2048,
                    },
                    timeout=180,
                )
                r.raise_for_status()
                report = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                break
            except Exception as e:
                err_msg = ""
                if 'r' in locals() and hasattr(r, 'text'):
                    err_msg = r.text
                
                # LM Studio가 다른 모델을 언로드하고 새 모델을 메모리에 로드하는 중 발생할 수 있는 오류들 대응
                if "reloaded" in err_msg.lower() or "loading" in err_msg.lower() or "loaded" in err_msg.lower() or (attempt < max_retries - 1 and getattr(e, 'response', None) is not None and e.response.status_code == 400):
                    print(f"⚠️  LM Studio 모델 로딩/교체 감지. {retry_delay}초 대기 후 재시도... (시도 {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                
                print(f"❌ LM Studio 호출 실패: {e}")
                if err_msg:
                    print(f"   서버 응답 상세: {err_msg}")
                report = ""
                break

    # LM Studio 호출이 실패했거나 모델이 없는 경우 폴백 텍스트 설정
    if not report:
        print("⚠️  LM Studio를 통한 요약 보고서 작성을 건너뜁니다. 수집된 로우 데이터를 저장합니다.")
        report = f"""⚠️ LM Studio 연결 실패로 분석 보고서를 완성하지 못했습니다. 수집된 트렌드 원본 데이터를 기록합니다.

### 📡 수집된 유튜브 떡상 영상 목록
{data_text}"""

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
