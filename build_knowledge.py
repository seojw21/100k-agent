"""
build_knowledge.py
==================
레딧 핵심통증.txt (TSV) → JSON DB + ChromaDB 벡터 인덱스 구축 스크립트

실행 방법:
    python build_knowledge.py

결과물:
    knowledge/pain_db.json          - 전체 정제 데이터
    knowledge/index.json            - 카테고리/점수 인덱스
    knowledge/top_ideas.md          - 상위 아이디어 요약
    knowledge/chroma_db/            - ChromaDB 벡터 인덱스
"""

import os
import json
import csv
import re
import traceback
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# 경로 설정
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
SOURCE_FILE = BASE_DIR / "레딧 핵심통증.txt"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = KNOWLEDGE_DIR / "chroma_db"

PAIN_DB_PATH = KNOWLEDGE_DIR / "pain_db.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
TOP_IDEAS_PATH = KNOWLEDGE_DIR / "top_ideas.md"

# ─────────────────────────────────────────────
# 카테고리 자동 분류 키워드 맵
# ─────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "AI/자동화": ["AI", "LLM", "GPT", "자동화", "에이전트", "머신러닝", "생성형"],
    "마케팅/영업": ["마케팅", "SEO", "콘텐츠", "리드", "아웃리치", "광고", "콜드 이메일", "GTM"],
    "개발자 도구": ["개발자", "API", "코드", "SaaS", "IDE", "Git", "스크래핑", "웹훅"],
    "이커머스/쇼핑": ["쇼핑", "이커머스", "Shopify", "아마존", "드롭쉬핑", "판매자"],
    "생산성/업무": ["생산성", "회의", "일정", "노트", "문서", "할 일", "업무"],
    "HR/채용": ["채용", "이력서", "구직", "HR", "온보딩", "직원"],
    "재무/결제": ["결제", "재무", "구독", "차지백", "Stripe", "인보이스", "수익"],
    "교육/학습": ["교육", "학습", "학교", "강의", "수업", "공부", "튜터"],
    "헬스/웰니스": ["헬스", "건강", "운동", "수면", "멘탈", "웰니스"],
    "법무/규정": ["법률", "규정", "GDPR", "컴플라이언스", "보안", "개인정보"],
    "B2B SaaS": ["B2B", "엔터프라이즈", "기업", "스타트업", "CRM", "대시보드"],
    "콘텐츠 창작": ["콘텐츠", "유튜브", "소셜미디어", "크리에이터", "블로그", "영상"],
}

def classify_category(text: str) -> str:
    """텍스트에서 카테고리를 자동 분류"""
    text_lower = text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw.lower() in text_lower)
        if count > 0:
            scores[cat] = count
    if not scores:
        return "기타"
    return max(scores, key=scores.get)

def parse_tsv(filepath: Path) -> list[dict]:
    """TSV 파일을 파싱하여 레코드 리스트 반환"""
    records = []
    
    with open(filepath, "r", encoding="utf-8-sig") as f:
        # 헤더 읽기
        header_line = f.readline().strip()
        # 탭 또는 혼합 구분자 처리
        if "\t" in header_line:
            delimiter = "\t"
        else:
            delimiter = ","
        
        headers = [h.strip() for h in header_line.split(delimiter)]
        print(f"📋 헤더 감지: {headers}")
        
        # 한국어 헤더 → 영어 키 매핑
        key_map = {
            "작성일": "created_at",
            "URL": "url",
            "점수": "score",
            "아이디어명": "idea_name",
            "핵심통증": "pain_point",
            "해결방안": "solution",
            "수익화근거": "monetization",
            "수집일": "collected_at",
        }
        
        reader = csv.reader(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        for line_num, row in enumerate(reader, start=2):
            if not row or not any(cell.strip() for cell in row):
                continue
            
            # 행이 헤더 수보다 짧으면 패딩
            while len(row) < len(headers):
                row.append("")
            
            record = {}
            for i, header in enumerate(headers):
                key = key_map.get(header.strip(), header.strip())
                value = row[i].strip() if i < len(row) else ""
                record[key] = value
            
            # 점수 정수화
            try:
                record["score"] = int(record.get("score", 0))
            except (ValueError, TypeError):
                record["score"] = 0
            
            # 아이디어명이 없으면 건너뜀
            if not record.get("idea_name"):
                continue
            
            # 카테고리 자동 분류
            combined = " ".join([
                record.get("idea_name", ""),
                record.get("pain_point", ""),
                record.get("solution", ""),
            ])
            record["category"] = classify_category(combined)
            
            # 고유 ID 부여
            record["id"] = f"idea_{line_num:04d}"
            
            records.append(record)
    
    return records

def build_index(records: list[dict]) -> dict:
    """카테고리/점수 기반 인덱스 구성"""
    index = {
        "total": len(records),
        "built_at": datetime.now().isoformat(),
        "by_category": {},
        "by_score": {},
        "top_10": [],
    }
    
    # 카테고리별
    for r in records:
        cat = r["category"]
        if cat not in index["by_category"]:
            index["by_category"][cat] = []
        index["by_category"][cat].append(r["id"])
    
    # 점수별
    for r in records:
        score_key = str(r["score"])
        if score_key not in index["by_score"]:
            index["by_score"][score_key] = []
        index["by_score"][score_key].append(r["id"])
    
    # 상위 10개 (점수 기준)
    sorted_records = sorted(records, key=lambda x: x["score"], reverse=True)
    index["top_10"] = [
        {
            "id": r["id"],
            "idea_name": r["idea_name"],
            "score": r["score"],
            "category": r["category"],
        }
        for r in sorted_records[:10]
    ]
    
    return index

def build_top_ideas_md(records: list[dict]) -> str:
    """상위 아이디어 마크다운 요약 생성"""
    sorted_records = sorted(records, key=lambda x: x["score"], reverse=True)
    top_30 = sorted_records[:30]
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🏆 레딧 핵심통증 Top 30 아이디어",
        f"> 생성일: {now} | 전체 {len(records)}개 중 상위 30개",
        "",
    ]
    
    # 카테고리별 그룹핑
    by_cat = {}
    for r in top_30:
        cat = r["category"]
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(r)
    
    for cat, items in by_cat.items():
        lines.append(f"## {cat}")
        for r in items:
            lines.append(f"### [{r['score']}점] {r['idea_name']}")
            lines.append(f"**핵심통증:** {r.get('pain_point', 'N/A')[:200]}...")
            lines.append(f"**해결방안:** {r.get('solution', 'N/A')[:200]}...")
            lines.append(f"**수익화:** {r.get('monetization', 'N/A')[:150]}...")
            lines.append("")
    
    return "\n".join(lines)

def build_chromadb(records: list[dict]):
    """ChromaDB 벡터 인덱스 구축"""
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError:
        print("❌ chromadb 패키지가 없습니다. pip install chromadb 실행 후 재시도하세요.")
        return False
    
    print("🧠 ChromaDB 벡터 인덱스 구축 중...")
    
    # 다국어 임베딩 함수 (한국어 지원)
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        print("  ✅ 다국어 임베딩 모델 로드 완료")
    except Exception as e:
        print(f"  ⚠️ SentenceTransformer 로드 실패: {e}")
        print("  🔄 기본 임베딩 함수로 폴백...")
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # ChromaDB 클라이언트 초기화
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # 기존 컬렉션 삭제 후 재생성
    try:
        client.delete_collection("pain_points")
        print("  🗑️ 기존 컬렉션 삭제")
    except Exception:
        pass
    
    collection = client.create_collection(
        name="pain_points",
        embedding_function=embedding_fn,
        metadata={"description": "레딧 핵심통증 벡터 DB", "hnsw:space": "cosine"},
    )
    
    # 배치 단위로 삽입 (ChromaDB 권장 배치 크기: 100~500)
    BATCH_SIZE = 200
    total = len(records)
    
    for batch_start in range(0, total, BATCH_SIZE):
        batch = records[batch_start : batch_start + BATCH_SIZE]
        
        ids = [r["id"] for r in batch]
        
        # 검색에 사용될 텍스트 (아이디어명 + 통증 + 해결방안 결합)
        documents = [
            f"{r.get('idea_name', '')} | {r.get('pain_point', '')} | {r.get('solution', '')}"
            for r in batch
        ]
        
        # 메타데이터 (필터링에 활용)
        metadatas = [
            {
                "idea_name": r.get("idea_name", "")[:100],
                "category": r.get("category", "기타"),
                "score": r.get("score", 0),
                "url": r.get("url", "")[:200],
                "pain_point": r.get("pain_point", "")[:300],
                "solution": r.get("solution", "")[:300],
                "monetization": r.get("monetization", "")[:200],
            }
            for r in batch
        ]
        
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"  📥 {min(batch_start + BATCH_SIZE, total)}/{total} 삽입 완료")
    
    print(f"✅ ChromaDB 벡터 인덱스 완성: {total}개 레코드")
    return True

def main():
    print("=" * 60)
    print("🚀 레딧 핵심통증 지식 베이스 구축 시작")
    print("=" * 60)
    
    # 디렉토리 생성
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    CHROMA_DIR.mkdir(exist_ok=True)
    
    # 1. TSV 파싱
    print(f"\n📂 파일 읽는 중: {SOURCE_FILE}")
    if not SOURCE_FILE.exists():
        print(f"❌ 파일이 없습니다: {SOURCE_FILE}")
        return
    
    records = parse_tsv(SOURCE_FILE)
    print(f"✅ 파싱 완료: {len(records)}개 레코드")
    
    # 카테고리 분포 출력
    cat_counts = {}
    for r in records:
        cat = r["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    print("\n📊 카테고리 분포:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:20s}: {cnt}개")
    
    # 2. JSON DB 저장
    print(f"\n💾 JSON DB 저장 중...")
    with open(PAIN_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"✅ 저장 완료: {PAIN_DB_PATH}")
    
    # 3. 인덱스 생성
    print(f"\n🗂️ 인덱스 생성 중...")
    index = build_index(records)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"✅ 인덱스 저장 완료: {INDEX_PATH}")
    
    # 4. Top Ideas 마크다운
    print(f"\n📝 Top 30 아이디어 요약 생성 중...")
    top_md = build_top_ideas_md(records)
    with open(TOP_IDEAS_PATH, "w", encoding="utf-8") as f:
        f.write(top_md)
    print(f"✅ Top Ideas 저장 완료: {TOP_IDEAS_PATH}")
    
    # 5. ChromaDB 벡터 인덱스
    print(f"\n🔍 벡터 인덱스 구축 중...")
    success = build_chromadb(records)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 모든 지식 베이스 구축 완료!")
    else:
        print("⚠️ JSON/인덱스는 완료, ChromaDB는 패키지 설치 후 재실행 필요")
    print("=" * 60)
    print(f"\n생성된 파일:")
    print(f"  📄 {PAIN_DB_PATH}")
    print(f"  📄 {INDEX_PATH}")
    print(f"  📄 {TOP_IDEAS_PATH}")
    if success:
        print(f"  🗄️ {CHROMA_DIR}/")

if __name__ == "__main__":
    main()
