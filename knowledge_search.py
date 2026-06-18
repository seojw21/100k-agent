"""
knowledge_search.py
===================
레딧 핵심통증 지식 베이스 검색 유틸리티

사용 예시:
    from knowledge_search import KnowledgeSearch
    ks = KnowledgeSearch()

    # 자연어 의미 검색
    results = ks.search("AI 마케팅 자동화 관련 통증")

    # 카테고리 필터 검색
    results = ks.search("결제 자동화", category="재무/결제", top_k=5)

    # 고점수 아이디어만
    top = ks.get_top_ideas(n=10, min_score=9)

    # agent.py 용 컨텍스트 문자열 생성
    context = ks.build_context_for_agent("마케팅 자동화")
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# GitHub Actions(Linux) / Windows 환경 모두에서 UTF-8 출력 보장
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = KNOWLEDGE_DIR / "chroma_db"
PAIN_DB_PATH = KNOWLEDGE_DIR / "pain_db.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"

class KnowledgeSearch:
    def __init__(self):
        self._db: list[dict] = []
        self._index: dict = {}
        self._chroma_collection = None
        self._load_json_db()
        self._load_chromadb()

    # ─────────────────────────────────────────────
    # 초기화
    # ─────────────────────────────────────────────
    def _load_json_db(self):
        """JSON DB 로드"""
        if PAIN_DB_PATH.exists():
            with open(PAIN_DB_PATH, "r", encoding="utf-8") as f:
                self._db = json.load(f)
            if INDEX_PATH.exists():
                with open(INDEX_PATH, "r", encoding="utf-8") as f:
                    self._index = json.load(f)
            print(f"[OK] JSON DB 로드 완료: {len(self._db)}개 레코드")
        else:
            print("[WARN] knowledge/pain_db.json 없음 - build_knowledge.py 먼저 실행하세요")

    def _load_chromadb(self):
        """ChromaDB 컬렉션 로드"""
        if not CHROMA_DIR.exists():
            print("[WARN] ChromaDB 인덱스 없음 - build_knowledge.py 먼저 실행하세요")
            return
        try:
            import chromadb
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            embedding_fn = SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            self._chroma_collection = client.get_collection(
                name="pain_points",
                embedding_function=embedding_fn,
            )
            print(f"[OK] ChromaDB 로드 완료: {self._chroma_collection.count()}개 벡터")
        except Exception as e:
            print(f"[WARN] ChromaDB 로드 실패 (JSON 폴백 사용): {e}")
            self._chroma_collection = None

    @property
    def is_ready(self) -> bool:
        return len(self._db) > 0

    @property
    def has_vector_search(self) -> bool:
        return self._chroma_collection is not None

    # ─────────────────────────────────────────────
    # 핵심 검색 메서드
    # ─────────────────────────────────────────────
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: int = 0,
        category: Optional[str] = None,
    ) -> list[dict]:
        """
        자연어 의미 검색 (ChromaDB) → JSON 키워드 검색 폴백

        Args:
            query: 검색 쿼리 (자연어)
            top_k: 반환할 결과 수
            min_score: 최소 점수 필터 (0~10)
            category: 카테고리 필터 (예: "AI/자동화")

        Returns:
            결과 레코드 리스트
        """
        if self._chroma_collection:
            return self._vector_search(query, top_k, min_score, category)
        else:
            return self._keyword_search(query, top_k, min_score, category)

    def _vector_search(self, query: str, top_k: int, min_score: int, category: Optional[str]) -> list[dict]:
        """ChromaDB 벡터 검색"""
        where_filter = {}
        if min_score > 0:
            where_filter["score"] = {"$gte": min_score}
        if category:
            where_filter["category"] = {"$eq": category}
        
        kwargs = {
            "query_texts": [query],
            "n_results": min(top_k * 2, self._chroma_collection.count()),  # 여유있게 가져와서 필터
        }
        if where_filter:
            kwargs["where"] = where_filter
        
        try:
            result = self._chroma_collection.query(**kwargs)
        except Exception as e:
            print(f"벡터 검색 에러: {e}, 키워드 검색으로 폴백")
            return self._keyword_search(query, top_k, min_score, category)
        
        # 메타데이터를 풍부한 레코드로 변환
        records = []
        if result["metadatas"] and result["metadatas"][0]:
            for meta, dist in zip(result["metadatas"][0], result["distances"][0]):
                record = dict(meta)
                record["_similarity"] = round(1 - dist, 3)  # cosine distance → similarity
                records.append(record)
        
        return records[:top_k]

    def _keyword_search(self, query: str, top_k: int, min_score: int, category: Optional[str]) -> list[dict]:
        """JSON DB 키워드 검색 (폴백)"""
        query_lower = query.lower()
        results = []
        
        for r in self._db:
            if r.get("score", 0) < min_score:
                continue
            if category and r.get("category") != category:
                continue
            
            combined = " ".join([
                r.get("idea_name", ""),
                r.get("pain_point", ""),
                r.get("solution", ""),
            ]).lower()
            
            # 간단한 TF 점수
            words = query_lower.split()
            hit_count = sum(1 for w in words if w in combined)
            if hit_count > 0:
                record = dict(r)
                record["_similarity"] = round(hit_count / len(words), 3)
                results.append(record)
        
        results.sort(key=lambda x: (-x["_similarity"], -x.get("score", 0)))
        return results[:top_k]

    # ─────────────────────────────────────────────
    # 편의 메서드
    # ─────────────────────────────────────────────
    def get_top_ideas(self, n: int = 10, min_score: int = 9) -> list[dict]:
        """고점수 아이디어 반환"""
        filtered = [r for r in self._db if r.get("score", 0) >= min_score]
        filtered.sort(key=lambda x: -x.get("score", 0))
        return filtered[:n]

    def get_by_category(self, category: str, top_k: int = 10) -> list[dict]:
        """카테고리별 아이디어 반환"""
        filtered = [r for r in self._db if r.get("category") == category]
        filtered.sort(key=lambda x: -x.get("score", 0))
        return filtered[:top_k]

    def get_categories(self) -> dict:
        """카테고리 목록 및 개수 반환"""
        cats = {}
        for r in self._db:
            cat = r.get("category", "기타")
            cats[cat] = cats.get(cat, 0) + 1
        return dict(sorted(cats.items(), key=lambda x: -x[1]))

    def get_stats(self) -> dict:
        """지식 베이스 통계"""
        return {
            "total": len(self._db),
            "has_vector_search": self.has_vector_search,
            "categories": self.get_categories(),
            "score_distribution": self._index.get("by_score", {}),
            "top_10": self._index.get("top_10", []),
            "built_at": self._index.get("built_at", "unknown"),
        }

    def build_context_for_agent(self, topic: str, top_k: int = 5) -> str:
        """
        agent.py 프롬프트에 주입할 컨텍스트 블록 생성

        Args:
            topic: 오늘의 뉴스 트렌드 키워드 또는 주제
            top_k: 참조할 아이디어 수

        Returns:
            마크다운 형태의 컨텍스트 문자열
        """
        if not self.is_ready:
            return ""
        
        related = self.search(topic, top_k=top_k, min_score=8)
        
        if not related:
            # 폴백: 고점수 아이디어 반환
            related = self.get_top_ideas(n=top_k, min_score=9)
        
        lines = [
            "## 📚 레딧 검증 핵심통증 (유사 사례 참조)",
            f"> 주제 '{topic}' 관련 실제 사용자 통증 {len(related)}건:",
            "",
        ]
        
        for i, r in enumerate(related, 1):
            sim = r.get("_similarity", "")
            sim_str = f" (유사도: {sim})" if sim else ""
            lines.append(f"### {i}. {r.get('idea_name', 'N/A')}{sim_str}")
            lines.append(f"- **통증**: {r.get('pain_point', 'N/A')[:200]}")
            lines.append(f"- **해결**: {r.get('solution', 'N/A')[:200]}")
            lines.append(f"- **수익화**: {r.get('monetization', 'N/A')[:150]}")
            lines.append("")
        
        return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI 테스트
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    print("🔍 KnowledgeSearch 테스트")
    ks = KnowledgeSearch()
    
    if not ks.is_ready:
        print("❌ 지식 베이스가 없습니다. 먼저 build_knowledge.py를 실행하세요.")
        sys.exit(1)
    
    stats = ks.get_stats()
    print(f"\n📊 통계:")
    print(f"  총 레코드: {stats['total']}개")
    print(f"  벡터 검색: {'✅' if stats['has_vector_search'] else '❌ (키워드 폴백)'}")
    print(f"  카테고리: {list(stats['categories'].keys())}")
    
    # 검색 테스트
    queries = [
        "AI 마케팅 자동화",
        "결제 실패 자동 복구",
        "코드 보안 취약점 스캔",
    ]
    
    for query in queries:
        print(f"\n🔎 검색: '{query}'")
        results = ks.search(query, top_k=3)
        for r in results:
            sim = r.get("_similarity", "")
            print(f"  [{r.get('score', 0)}점] {r.get('idea_name', 'N/A')} (유사도: {sim})")
    
    # 컨텍스트 생성 테스트
    print(f"\n📝 에이전트 컨텍스트 생성 테스트:")
    ctx = ks.build_context_for_agent("AI SaaS 자동화 트렌드")
    print(ctx[:500] + "...")
