"""
build_knowledge.py
==================
레딧 핵심통증.txt (TSV) + reddit add row.txt → 통합 JSON DB + 999개 MD 세컨드 브레인 구축 스크립트

결과물:
    knowledge/pain_db.json          - 전체 정제 및 병합 데이터
    knowledge/index.json            - 카테고리/점수 인덱스
    knowledge/top_ideas.md          - 상위 아이디어 요약
    knowledge/md_brain/             - 999개 Markdown 파일 (Connect AI Lab 시각화용)
"""

import os
import json
import csv
import re
import requests
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# 경로 설정
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
SOURCE_FILE_1 = BASE_DIR / "레딧 핵심통증.txt"
# SOURCE_FILE_2는 윈도우 개발 환경의 절대 경로입니다. 맥 환경에서는 해당 경로가 존재하지 않는 경우 자동으로 무시됩니다.
SOURCE_FILE_2 = Path("D:/AUTOPUS/daangn-lead-discovery/reddit add row.txt")

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Uigez5tb4Cn86lAJeDPmZLy5k-TamrRKtfZCrfRZSrM/export?format=csv"

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
MD_BRAIN_DIR = KNOWLEDGE_DIR / "md_brain"

PAIN_DB_PATH = KNOWLEDGE_DIR / "pain_db.json"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
TOP_IDEAS_PATH = KNOWLEDGE_DIR / "top_ideas.md"

# ─────────────────────────────────────────────
# 카테고리 자동 분류 키워드 맵
# ─────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "AI_자동화": ["AI", "LLM", "GPT", "자동화", "에이전트", "머신러닝", "생성형"],
    "마케팅_영업": ["마케팅", "SEO", "콘텐츠", "리드", "아웃리치", "광고", "콜드 이메일", "GTM"],
    "개발자_도구": ["개발자", "API", "코드", "SaaS", "IDE", "Git", "스크래핑", "웹훅"],
    "이커머스_쇼핑": ["쇼핑", "이커머스", "Shopify", "아마존", "드롭쉬핑", "판매자"],
    "생산성_업무": ["생산성", "회의", "일정", "노트", "문서", "할 일", "업무"],
    "HR_채용": ["채용", "이력서", "구직", "HR", "온보딩", "직원"],
    "재무_결제": ["결제", "재무", "구독", "차지백", "Stripe", "인보이스", "수익"],
    "교육_학습": ["교육", "학습", "학교", "강의", "수업", "공부", "튜터"],
    "헬스_웰니스": ["헬스", "건강", "운동", "수면", "멘탈", "웰니스"],
    "법무_규정": ["법률", "규정", "GDPR", "컴플라이언스", "보안", "개인정보"],
    "B2B_SaaS": ["B2B", "엔터프라이즈", "기업", "스타트업", "CRM", "대시보드"],
    "콘텐츠_창작": ["콘텐츠", "유튜브", "소셜미디어", "크리에이터", "블로그", "영상"],
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
    if not filepath.exists():
        print(f"⚠️ 파일이 존재하지 않습니다: {filepath}")
        return records

    with open(filepath, "r", encoding="utf-8-sig") as f:
        # 헤더 읽기
        header_line = f.readline().strip()
        if "\t" in header_line:
            delimiter = "\t"
        else:
            delimiter = ","
        
        headers = [h.strip() for h in header_line.split(delimiter)]
        
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
    
    for r in records:
        cat = r["category"]
        if cat not in index["by_category"]:
            index["by_category"][cat] = []
        index["by_category"][cat].append(r["id"])
    
    for r in records:
        score_key = str(r["score"])
        if score_key not in index["by_score"]:
            index["by_score"][score_key] = []
        index["by_score"][score_key].append(r["id"])
    
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

def sanitize_filename(name: str) -> str:
    """파일명에서 사용할 수 없는 문자 제거 및 정제"""
    cleaned = re.sub(r'[\/:*?"<>|]', ' ', name)
    cleaned = re.sub(r'\s+', '_', cleaned.strip())
    return cleaned[:60]

def build_md_brain(records: list[dict]):
    """Connect AI Lab 및 Ezerai 시각화용 999개 Markdown 파일 생성"""
    print(f"\n📂 999개 Markdown 파일 생성 중... (경로: {MD_BRAIN_DIR})")
    MD_BRAIN_DIR.mkdir(exist_ok=True, parents=True)
    
    # 기존 파일 삭제 (초기화)
    for f in MD_BRAIN_DIR.glob("*.md"):
        try:
            f.unlink()
        except Exception:
            pass
            
    # 점수 높은 상위 999개 선별
    sorted_records = sorted(records, key=lambda x: x["score"], reverse=True)
    top_999 = sorted_records[:999]
    
    for i, r in enumerate(top_999, 1):
        safe_name = sanitize_filename(r["idea_name"])
        filename = f"idea_{i:03d}_{safe_name}.md"
        filepath = MD_BRAIN_DIR / filename
        
        # MD 내용 작성
        content = f"""# {r['idea_name']}
**카테고리:** {r['category']}
**점수:** {r['score']}
**태그:** #{r['category']} #{r['score']}점

## 😟 핵심 통증 (Pain Point)
{r.get('pain_point', '정보 없음')}

## 💡 해결 방안 (Solution)
{r.get('solution', '정보 없음')}

## 💰 수익화 근거 (Monetization)
{r.get('monetization', '정보 없음')}

---
- **출처 URL:** {r.get('url', 'N/A')}
- **수집일:** {r.get('collected_at', 'N/A')}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"✅ MD 브레인 생성 완료: {len(top_999)}개 마크다운 파일")

def build_chroma_db(records: list[dict]):
    """ChromaDB 벡터 데이터베이스 구축"""
    CHROMA_DIR = KNOWLEDGE_DIR / "chroma_db"
    print(f"\n📂 ChromaDB 벡터 데이터베이스 생성 중... (경로: {CHROMA_DIR})")
    
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    except ImportError:
        print("⚠️ chromadb 또는 sentence-transformers 패키지가 설치되어 있지 않아 ChromaDB 구축을 스킵합니다.")
        print("설치를 위해 'pip install chromadb sentence-transformers'를 실행하세요.")
        return
    
    CHROMA_DIR.mkdir(exist_ok=True, parents=True)
    
    # ChromaDB Persistent Client 생성
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # knowledge_search.py 와 동일한 임베딩 모델 사용
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # 기존 컬렉션 초기화
    try:
        client.delete_collection("pain_points")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="pain_points",
        embedding_function=embedding_fn
    )
    
    ids = []
    documents = []
    metadatas = []
    
    for r in records:
        # RAG 검색 최적화용 텍스트 합성
        doc_text = f"아이디어명: {r.get('idea_name', '')}\n카테고리: {r.get('category', '')}\n핵심통증: {r.get('pain_point', '')}\n해결방안: {r.get('solution', '')}\n수익화근거: {r.get('monetization', '')}"
        
        # 메타데이터 매핑
        meta = {
            "id": r.get("id", ""),
            "idea_name": r.get("idea_name", ""),
            "category": r.get("category", ""),
            "score": int(r.get("score", 0)),
            "url": r.get("url", ""),
            "collected_at": r.get("collected_at", "")
        }
        
        ids.append(r.get("id", ""))
        documents.append(doc_text)
        metadatas.append(meta)
        
    # 200개씩 배치 인서트 실행 (ChromaDB의 배치 크기 권장 제한 준수)
    batch_size = 200
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        print(f"  -> {end_idx}/{len(ids)} 개 레코드 임베딩 완료...")
        
    print(f"✅ ChromaDB 구축 완료! 총 {collection.count()}개 벡터 인덱싱됨.")

def download_google_sheet_csv():
    """구글 스프레드시트에서 최신 데이터를 다운로드하여 로컬 캐시(레딧 핵심통증.txt) 업데이트"""
    print(f"\n🌐 구글 스프레드시트 최신 데이터 다운로드 시도 중...")
    print(f"🔗 URL: {GOOGLE_SHEET_CSV_URL}")
    try:
        response = requests.get(GOOGLE_SHEET_CSV_URL, timeout=15)
        response.raise_for_status()
        
        # UTF-8 BOM 및 한글 깨짐 방지를 위해 명시적으로 디코딩
        content = response.content.decode('utf-8-sig')
        
        # 다운로드받은 CSV 데이터 검증 (헤더 확인)
        if "작성일" in content and "아이디어명" in content and "핵심통증" in content:
            with open(SOURCE_FILE_1, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 구글 스프레드시트 다운로드 및 로컬 캐시({SOURCE_FILE_1.name}) 갱신 완료!")
        else:
            print("⚠️ 다운로드받은 데이터의 헤더 구조가 올바르지 않습니다. 기존 로컬 데이터를 사용합니다.")
    except Exception as e:
        print(f"⚠️ 구글 스프레드시트 다운로드 실패: {e}")
        print(f"ℹ️ 오프라인 모드: 기존 로컬 캐시({SOURCE_FILE_1.name}) 데이터를 활용하여 빌드를 진행합니다.")

def main():
    print("=" * 60)
    print("🚀 레딧 핵심통증 지식 베이스 및 세컨드 브레인 구축 시작")
    print("=" * 60)
    
    # 0. 구글 스프레드시트에서 최신 데이터 동기화 시도
    download_google_sheet_csv()
    
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    MD_BRAIN_DIR.mkdir(exist_ok=True)
    
    # 1. 파일들 읽기 및 병합
    records = []
    seen_ideas = set()
    
    for source in [SOURCE_FILE_1, SOURCE_FILE_2]:
        if source.exists():
            print(f"\n📂 파일 파싱 중: {source}")
            parsed = parse_tsv(source)
            for r in parsed:
                if r["idea_name"] not in seen_ideas:
                    seen_ideas.add(r["idea_name"])
                    records.append(r)
                    
    print(f"\n✅ 파싱 및 중복 제거 완료: {len(records)}개 고유 레코드")
    
    # 고유 ID 부여
    for i, r in enumerate(records, start=1):
        r["id"] = f"idea_{i:04d}"
        
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
    
    # 4. Top Ideas 마크다운 요약 생성
    print(f"\n📝 Top 30 아이디어 요약 생성 중...")
    top_md = build_top_ideas_md(records)
    with open(TOP_IDEAS_PATH, "w", encoding="utf-8") as f:
        f.write(top_md)
    print(f"✅ Top Ideas 저장 완료: {TOP_IDEAS_PATH}")
    
    # 5. Connect AI Lab 시각화용 MD 브레인 생성
    build_md_brain(records)
    
    # 6. ChromaDB 벡터 DB 구축
    build_chroma_db(records)
    
    print("\n" + "=" * 60)
    print("🎉 모든 지식 베이스 및 MD 세컨드 브레인 구축 완료!")
    print("=" * 60)
    print(f"\n생성된 파일 및 폴더:")
    print(f"  📄 {PAIN_DB_PATH}")
    print(f"  📄 {INDEX_PATH}")
    print(f"  📄 {TOP_IDEAS_PATH}")
    print(f"  📁 {MD_BRAIN_DIR}/ (999개 파일)")
    print(f"  📁 {KNOWLEDGE_DIR / 'chroma_db'}/ (ChromaDB 벡터 인덱스)")

if __name__ == "__main__":
    main()
