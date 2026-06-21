
# [Technical Specification] B2B 사내 지식 베이스 챗봇

## 1. Core Technology Stack
- **LLM Engine:** OpenAI GPT-4o (높은 추론 능력 및 한국어 성능 최적화)
- **Orchestration Framework:** LangChain (RAG 파이프라인 구축 및 에이전트 기능 구현)
- **Vector Database:** Pinecone 또는 ChromaDB (초기 단계에서는 관리 효율을 위해 Pinecone 권장)
- **Embedding Model:** text-embedding-3-small (비용 효율적이며 높은 성능의 임베딩 제공)
- **Data Ingestion:** Unstructured.io (PDF, Word, Notion 등 다양한 포맷 파싱)

## 2. System Architecture (RAG Pipeline)
1.  **Ingestion Layer:**
    *   Source Connectors: Notion API, Google Drive API 연동.
    *   Preprocessing: 텍스트 추출 -> 청크(Chunking) 분할 → 임베딩 생성.
2.  **Retrieval Layer:**
    *   Hybrid Search: 벡터 검색(Semantic) + 키워드 검색(BM25) 결합으로 정확도 극대화.
    *   Re-ranking: 검색된 상위 결과 중 가장 관련성 높은 정보를 재정렬하여 LLM에 전달.
3.  **Generation Layer:**
    *   Prompt Engineering: "제공된 컨텍스트 내에서만 답변할 것", "모르면 모른다고 할 것" 등의 제약 조건 부여.
    *   Source Citation: 답변 시 참조한 문서의 제목과 링크를 반드시 포함하도록 설계.

## 3. Infrastructure & Scalability
- **Backend:** FastAPI (빠른 성능 및 비동기 처리 지원)
- **Frontend/Interface:** Slack Bolt SDK (슬랙 연동), Streamlit (관리자용 대시보드 및 테스트용 웹 UI)
- **Deployment:** Docker 컨테이너 기반 배포로 확장성 확보.

## 4. Key Technical Challenges & Solutions
- **Hallucination 방지:** Retrieval 결과가 부족할 경우 "정보를 찾을 수 없습니다"라고 답변하도록 시스템 프롬프트 고도화.
- **Context Window 관리:** 긴 문서를 처리할 때 핵심 정보만 추출하여 컨텍스트에 포함하는 전략 채택.
