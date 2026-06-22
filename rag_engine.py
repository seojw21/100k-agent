import os
import json
import time
import requests
from pathlib import Path
from knowledge_search import KnowledgeSearch

# LM Studio 포트 설정 (1234)
LM_STUDIO_URL = "http://localhost:1234/v1"

# Hallucination 방지 및 전문 톤 유지를 위한 프롬프트 가이드라인
SYSTEM_PROMPT = """당신은 기업의 내부 지식 베이스를 관리하는 전문 AI 비서입니다.
아래 제공된 [Context] 내용만을 바탕으로 사용자의 질문에 답변하십시오.

[지침]
1. 반드시 제공된 정보 내에서만 답변하세요. 
2. 정보가 부족하거나 모르는 내용이라면 "해당 내용은 사내 매뉴얼에서 확인이 어렵습니다. 담당 부서에 문의해 주세요."라고 정중하게 안내하십시오.
3. 추측이나 외부 지식을 활용하여 답변하지 마십시오.
4. 전문적이고 신뢰감 있는 비즈니스 톤을 유지하십시오.
"""

def get_rag_response(query: str, retries=3, delay=10) -> str:
    """
    1. KnowledgeSearch 싱글톤을 이용하여 질문 관련 지식(Context)을 조회
    2. LM Studio 로컬 LLM을 호출하여 정제된 비즈니스 답변을 생성 및 반환 (지연 시 재시도)
    """
    try:
        # KnowledgeSearch 인스턴스 획득 (싱글톤)
        ks = KnowledgeSearch()
        if not ks.is_ready:
            return "Error: 지식 베이스가 로드되지 않았습니다."
            
        # Context 검색
        results = ks.search(query, top_k=3)
        if not results:
            return "해당 내용은 사내 매뉴얼에서 확인이 어렵습니다. 담당 부서에 문의해 주세요."
            
        # Context 조립
        context_parts = []
        for i, r in enumerate(results, 1):
            part = (
                f"[아이디어 {i}]: {r.get('idea_name', 'N/A')}\n"
                f"- 핵심 통증: {r.get('pain_point', 'N/A')}\n"
                f"- 해결 방안: {r.get('solution', 'N/A')}\n"
                f"- 수익화 근거: {r.get('monetization', 'N/A')}\n"
            )
            context_parts.append(part)
        context_str = "\n".join(context_parts)
        
        # 프롬프트 빌드
        user_content = f"""[Context]
{context_str}

질문: {query}
답변:"""

        # LM Studio 호출 (재시도 루프)
        for attempt in range(retries):
            try:
                # LM Studio 모델 정보 자동 감지 및 gemma 우선순위 (Gemma 4 12b 서브)
                r_models = requests.get(f"{LM_STUDIO_URL}/models", timeout=5)
                models_data = r_models.json().get("data", [])
                
                model = None
                for m in models_data:
                    if "gemma" in m["id"].lower():
                        model = m["id"]
                        break
                        
                if not model and models_data:
                    model = models_data[0]["id"]
                    
                if not model:
                    model = "local-model"
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.0,  # 신뢰성 강화를 위해 온도는 0
                    "max_tokens": 1024
                }
                
                response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload, timeout=120)
                if response.status_code == 200:
                    res_json = response.json()
                    if "choices" in res_json:
                        return res_json["choices"][0]["message"]["content"].strip()
                
                print(f"⚠️ RAG attempt {attempt+1}: LM Studio API status {response.status_code}")
            except Exception as e:
                print(f"⚠️ RAG attempt {attempt+1} failed: {e}")
                
            if attempt < retries - 1:
                print(f"⏳ Waiting {delay}s before retrying RAG request...")
                time.sleep(delay)
                
        return "해당 내용은 사내 매뉴얼에서 확인이 어렵습니다. 담당 부서에 문의해 주세요."
        
    except Exception as e:
        return f"Error executing RAG: {e}"

# CLI 테스트용 코드
if __name__ == "__main__":
    print("🤖 RAG Engine 테스트 시작...")
    test_query = "AI 마케팅 자동화 통증 포인트가 무엇인가요?"
    print(f"🔎 쿼리: {test_query}")
    ans = get_rag_response(test_query)
    print(f"📝 답변:\n{ans}")
