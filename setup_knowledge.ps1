# 레딧 핵심통증 지식 베이스 구축 실행 스크립트 (Windows PowerShell)
# 터미널에서 아래 명령어를 순서대로 실행하세요

# Step 1: 패키지 설치
pip install chromadb sentence-transformers

# Step 2: 지식 베이스 구축 (TSV → JSON + 벡터 인덱스)
python build_knowledge.py

# Step 3: 검색 테스트
python knowledge_search.py

# Step 4: 에이전트 실행 (선택)
# python agent.py
