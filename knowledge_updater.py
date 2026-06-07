"""
knowledge_updater.py
====================
Self-RAG 4단계 검증 기반 지식 베이스 증분 업데이트

Self-RAG 검증 (AI빌더 4-2강 기반):
  1. Is Retrieval Needed?  → 이 게시물이 새로운 지식인가?
  2. Is Relevant?          → 비즈니스 통증 포인트와 관련 있나?
  3. Is Supported?         → 실제 경험/사실 기반인가? (할루시네이션 아님)
  4. Is Useful?            → 1인 기업에 실제로 유용한 인사이트인가?

4개 모두 통과 → DB 저장
1~2개 실패   → 스킵 (쓰레기 지식 방지)
"""

import os
import json
import re
import time
import requests
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = KNOWLEDGE_DIR / "chroma_db"
RAW_COLLECTED_PATH = KNOWLEDGE_DIR / "raw_collected.jsonl"
PAIN_DB_PATH = KNOWLEDGE_DIR / "pain_db.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
PROCESSED_IDS_PATH = KNOWLEDGE_DIR / "processed_ids.json"
SELFRAG_LOG_PATH = KNOWLEDGE_DIR / "selfrag_log.jsonl"

API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# ─────────────────────────────────────────────
# Gemini 공통 호출
# ─────────────────────────────────────────────
def call_gemini(prompt: str, retries: int = 3) -> str | None:
    if not API_KEY:
        return None
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    url = f"{GEMINI_URL}?key={API_KEY}"

    for attempt in range(retries):
        try:
            r = requests.post(url, headers=headers, json=data, timeout=25)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif r.status_code == 429:
                print("    ⏳ Rate limit 60초 대기...")
                time.sleep(60)
            elif r.status_code == 503:
                time.sleep(2 ** attempt)
            else:
                print(f"    ❌ Gemini {r.status_code}: {r.text}")
                return None
        except Exception as e:
            print(f"    ⚠️ 네트워크 에러: {e}")
            time.sleep(2)
    return None


# ─────────────────────────────────────────────
# STEP 1: Self-RAG 4단계 검증 (혼잣말 단계)
# ─────────────────────────────────────────────
def selfrag_verify(title: str, content: str) -> dict:
    """
    Self-RAG 4단계 검증
    Returns:
        {
          "is_retrieval_needed": bool,  # 새로운 지식인가?
          "is_relevant": bool,           # 비즈니스 통증과 관련?
          "is_supported": bool,          # 실제 경험 기반?
          "is_useful": bool,             # 1인 기업에 유용?
          "passed": bool,                # 최종 통과 여부 (3/4 이상)
          "score": int,                  # 통과 기준 수 (0~4)
          "reason": str                  # 검증 이유 요약
        }
    """
    prompt = f"""당신은 비즈니스 지식 품질 검증 AI입니다. 
Reddit 게시물이 1인 창업가의 지식 DB에 저장할 가치가 있는지 Self-RAG 방식으로 판단하세요.

[게시물]
제목: {title}
내용: {content[:600]}

[Self-RAG 4단계 검증] - 각 항목에 대해 스스로 논리적으로 판단하세요:

1. Is Retrieval Needed? (새로운 지식인가?)
   → 이 게시물이 일반 상식이 아닌, 실제로 저장할 가치 있는 새 인사이트를 포함하는가?

2. Is Relevant? (관련성 있나?)  
   → SaaS, 스타트업, 1인 창업, 비즈니스 통증/문제점과 직접 관련 있는가?

3. Is Supported? (사실 기반인가?)
   → 실제 사용자의 경험이나 구체적 문제를 다루는가? (막연한 이론/광고 아닌가?)

4. Is Useful? (유용한가?)
   → 이 정보가 마이크로 SaaS 아이디어 발굴이나 시장 검증에 실제로 도움 되는가?

응답 형식 (JSON만 출력):
{{
  "is_retrieval_needed": true/false,
  "is_relevant": true/false,
  "is_supported": true/false,
  "is_useful": true/false,
  "reason": "판단 이유 1~2줄 요약"
}}"""

    text = call_gemini(prompt)
    if not text:
        return {"passed": False, "score": 0, "reason": "API 호출 실패"}

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"passed": False, "score": 0, "reason": "JSON 파싱 실패"}
        result = json.loads(match.group())

        checks = [
            result.get("is_retrieval_needed", False),
            result.get("is_relevant", False),
            result.get("is_supported", False),
            result.get("is_useful", False),
        ]
        passed_count = sum(checks)
        result["score"] = passed_count
        result["passed"] = passed_count >= 3  # 4개 중 3개 이상 통과해야 저장
        return result

    except Exception:
        return {"passed": False, "score": 0, "reason": "파싱 에러"}


# ─────────────────────────────────────────────
# STEP 2: 지식 추출 (검증 통과 시에만)
# ─────────────────────────────────────────────
def extract_knowledge(title: str, content: str, verify_result: dict) -> dict | None:
    """Self-RAG 통과한 게시물에서 구조화된 지식 추출"""
    prompt = f"""다음 Reddit 게시물에서 비즈니스 지식을 추출하세요.

제목: {title}
내용: {content[:800]}

검증 결과: {verify_result.get('reason', '')}

JSON 형식으로만 응답 (설명 없이):
{{
  "idea_name": "아이디어 이름 (한국어, 20자 이내)",
  "pain_point": "핵심 통증/문제 (한국어, 150자 이내)",
  "solution": "해결 방향 (한국어, 150자 이내)",
  "monetization": "수익화 방법 (한국어, 100자 이내)",
  "quality_score": 1~10 (시장 가능성과 통증 강도),
  "category": "AI/자동화|마케팅/영업|개발자 도구|이커머스/쇼핑|생산성/업무|HR/채용|재무/결제|교육/학습|헬스/웰니스|법무/규정|B2B SaaS|콘텐츠 창작|기타 중 하나",
  "tags": ["태그1", "태그2", "태그3"]
}}"""

    text = call_gemini(prompt)
    if not text:
        return None

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────
# ChromaDB
# ─────────────────────────────────────────────
def get_chroma_collection():
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        fn = SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        try:
            return client.get_collection("pain_points", embedding_function=fn)
        except Exception:
            return client.create_collection("pain_points", embedding_function=fn,
                                            metadata={"hnsw:space": "cosine"})
    except Exception as e:
        print(f"⚠️ ChromaDB 로드 실패: {e}")
        return None


def add_to_chromadb(collection, record: dict) -> bool:
    try:
        doc = f"{record.get('idea_name','')} | {record.get('pain_point','')} | {record.get('solution','')}"
        meta = {
            "idea_name":    str(record.get("idea_name", ""))[:100],
            "category":     str(record.get("category", "기타")),
            "score":        int(record.get("score", 0)),
            "url":          str(record.get("url", ""))[:200],
            "pain_point":   str(record.get("pain_point", ""))[:300],
            "solution":     str(record.get("solution", ""))[:300],
            "monetization": str(record.get("monetization", ""))[:200],
            "selfrag_score":int(record.get("selfrag_score", 0)),
        }
        collection.add(ids=[record["id"]], documents=[doc], metadatas=[meta])
        return True
    except Exception as e:
        if "already exists" not in str(e).lower():
            print(f"    ⚠️ ChromaDB 추가 실패: {e}")
        return False


# ─────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────
def load_json_set(path: Path) -> set:
    return set(json.load(open(path, encoding="utf-8"))) if path.exists() else set()

def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_pain_db() -> list:
    return json.load(open(PAIN_DB_PATH, encoding="utf-8")) if PAIN_DB_PATH.exists() else []

def rebuild_index(records: list):
    index = {"total": len(records), "built_at": datetime.now().isoformat(),
             "by_category": {}, "by_score": {}, "top_10": []}
    for r in records:
        index["by_category"].setdefault(r.get("category","기타"), []).append(r.get("id",""))
        index["by_score"].setdefault(str(r.get("score",0)), []).append(r.get("id",""))
    top = sorted(records, key=lambda x: x.get("score", 0), reverse=True)[:10]
    index["top_10"] = [{"id":r["id"],"idea_name":r.get("idea_name",""),
                        "score":r.get("score",0),"category":r.get("category","")} for r in top]
    save_json(INDEX_PATH, index)

def log_selfrag(item_id: str, title: str, verify: dict, extracted: dict | None):
    """Self-RAG 검증 결과 로그 저장"""
    entry = {
        "id": item_id,
        "title": title[:80],
        "timestamp": datetime.now().isoformat(),
        "selfrag": {
            "is_retrieval_needed": verify.get("is_retrieval_needed"),
            "is_relevant": verify.get("is_relevant"),
            "is_supported": verify.get("is_supported"),
            "is_useful": verify.get("is_useful"),
            "score": verify.get("score", 0),
            "passed": verify.get("passed", False),
            "reason": verify.get("reason", ""),
        },
        "extracted": bool(extracted),
    }
    with open(SELFRAG_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────
def run_update(max_process: int = 50):
    print("=" * 60)
    print(f"🧠 Self-RAG 지식 업데이터 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    if not RAW_COLLECTED_PATH.exists():
        print("⚠️ raw_collected.jsonl 없음 - reddit_collector.py 먼저 실행하세요")
        return 0

    processed_ids = load_json_set(PROCESSED_IDS_PATH)
    KNOWLEDGE_DIR.mkdir(exist_ok=True)

    # 미처리 항목 로드 (통증 신호 있는 것 우선)
    pending = []
    with open(RAW_COLLECTED_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if item["id"] not in processed_ids:
                pending.append(item)

    pending.sort(key=lambda x: (not x.get("has_pain_signal", False),))
    pending = pending[:max_process]

    print(f"📋 처리 대상: {len(pending)}개\n")
    if not pending:
        print("✅ 처리할 항목 없음")
        return 0

    pain_db = load_pain_db()
    existing_ids = {r["id"] for r in pain_db}
    collection = get_chroma_collection()

    stats = {"added": 0, "failed_verify": 0, "failed_extract": 0, "error": 0}

    for i, item in enumerate(pending, 1):
        title = item.get("title", "")
        content = item.get("content", "")
        subreddit = item.get("subreddit", "")

        print(f"[{i}/{len(pending)}] r/{subreddit}: {title[:55]}...")

        # ── STEP 1: Self-RAG 검증 (혼잣말) ──
        if API_KEY:
            verify = selfrag_verify(title, content)
        else:
            # API 없을 때 통증 신호로 대체
            has_signal = item.get("has_pain_signal", False)
            verify = {"passed": has_signal, "score": 3 if has_signal else 1,
                      "reason": "API 없음 - 신호 기반 판단",
                      "is_retrieval_needed": has_signal, "is_relevant": has_signal,
                      "is_supported": has_signal, "is_useful": has_signal}

        checks = [
            "✅" if verify.get("is_retrieval_needed") else "❌",
            "✅" if verify.get("is_relevant") else "❌",
            "✅" if verify.get("is_supported") else "❌",
            "✅" if verify.get("is_useful") else "❌",
        ]
        print(f"  Self-RAG [{verify.get('score',0)}/4] "
              f"필요:{checks[0]} 관련:{checks[1]} 사실:{checks[2]} 유용:{checks[3]}")
        print(f"  → {verify.get('reason','')[:80]}")

        if not verify.get("passed"):
            print(f"  ⛔ 검증 실패 - 저장 안 함\n")
            stats["failed_verify"] += 1
            processed_ids.add(item["id"])
            log_selfrag(item["id"], title, verify, None)
            time.sleep(0.5)
            continue

        # ── STEP 2: 지식 추출 ──
        if API_KEY:
            extracted = extract_knowledge(title, content, verify)
        else:
            extracted = {
                "idea_name": title[:40],
                "pain_point": content[:150],
                "solution": "분석 필요",
                "monetization": "분석 필요",
                "quality_score": 5,
                "category": "기타",
                "tags": [],
            }

        log_selfrag(item["id"], title, verify, extracted)

        if not extracted:
            print(f"  ⚠️ 지식 추출 실패\n")
            stats["failed_extract"] += 1
            processed_ids.add(item["id"])
            continue

        q_score = extracted.get("quality_score", 0)
        print(f"  💡 [{q_score}점] {extracted.get('idea_name','N/A')} "
              f"/ {extracted.get('category','기타')}")
        print(f"  태그: {extracted.get('tags', [])}\n")

        # ── STEP 3: DB 저장 ──
        record = {
            "id":            item["id"],
            "created_at":    item.get("published_at", ""),
            "url":           item.get("url", ""),
            "score":         q_score,
            "selfrag_score": verify.get("score", 0),  # Self-RAG 통과 수 (0~4)
            "idea_name":     extracted.get("idea_name", ""),
            "pain_point":    extracted.get("pain_point", ""),
            "solution":      extracted.get("solution", ""),
            "monetization":  extracted.get("monetization", ""),
            "category":      extracted.get("category", "기타"),
            "tags":          extracted.get("tags", []),
            "subreddit":     subreddit,
            "collected_at":  item.get("collected_at", ""),
            "auto_collected": True,
        }

        if item["id"] not in existing_ids:
            pain_db.append(record)
            existing_ids.add(item["id"])

        if collection:
            add_to_chromadb(collection, record)

        processed_ids.add(item["id"])
        stats["added"] += 1
        time.sleep(1.5)  # Rate limit 방지

    # 저장
    if stats["added"] > 0:
        save_json(PAIN_DB_PATH, pain_db)
        rebuild_index(pain_db)
        print(f"💾 DB 저장 완료: 총 {len(pain_db)}개")

    save_json(PROCESSED_IDS_PATH, list(processed_ids))

    print("\n" + "=" * 60)
    print(f"📊 최종 결과:")
    print(f"  ✅ 저장됨:         {stats['added']}개")
    print(f"  ⛔ 검증 실패:      {stats['failed_verify']}개")
    print(f"  ⚠️  추출 실패:     {stats['failed_extract']}개")
    print(f"  📚 전체 DB:        {len(pain_db)}개")
    print(f"  📝 Self-RAG 로그:  {SELFRAG_LOG_PATH}")
    print("=" * 60)
    return stats["added"]


def main():
    run_update(max_process=50)

if __name__ == "__main__":
    main()
