import os
import re
import sys
import json
import uuid
import datetime
import requests
import subprocess

# Ensure correct stdout encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = os.getenv("GEMINI_API_KEY")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(ROOT_DIR, "00_Raw")
WIKI_DIR = os.path.join(ROOT_DIR, "10_Wiki")
META_DIR = os.path.join(ROOT_DIR, "20_Meta")

def get_default_categories():
    return [
        "10_Wiki/🛠️ Projects",
        "10_Wiki/💡 Topics",
        "10_Wiki/⚖️ Decisions",
        "10_Wiki/🚀 Skills"
    ]

def init_directories():
    os.makedirs(RAW_DIR, exist_ok=True)
    for cat in get_default_categories():
        os.makedirs(os.path.join(ROOT_DIR, cat), exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)

def init_policy():
    policy_path = os.path.join(META_DIR, "Policy.md")
    if not os.path.exists(policy_path):
        initial_policy = """# 🧠 P-Reinforce RL Policy (Classification Policy)

## ⚖️ RL Weights
- **$w_1$ (Categorization Accuracy):** 0.4
- **$w_2$ (Graph Connectivity):** 0.4
- **$w_3$ (User Satisfaction):** 0.2

## 📋 행동 정책 (Action Policies)
1. **기존 분류 (Exploitation):** 의미적 유사도 85% 이상 시 기존 폴더에 지식을 배치한다.
2. **신규 생성 (Exploration):** 기존 카테고리에 맞지 않는 새로운 개념 등장 시 즉시 상위 개념을 도출하여 새 폴더를 생성한다.
3. **구조 재설계 (Refactoring):** 특정 폴더의 파일이 12개를 초과하면 하위 카테고리로 세분화(Refactoring)를 제안한다.

## 📝 사용자 피드백 로그 (RL Updates)
- [2026-05-03] P-Reinforce 엔진이 성공적으로 초기화되었습니다. 기본 가중치가 설정되었습니다.
"""
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(initial_policy)

def init_graph():
    graph_path = os.path.join(META_DIR, "Graph.json")
    if not os.path.exists(graph_path):
        initial_graph = {
            "nodes": [],
            "links": []
        }
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(initial_graph, f, indent=2, ensure_ascii=False)

def read_policy_content():
    policy_path = os.path.join(META_DIR, "Policy.md")
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def load_graph():
    graph_path = os.path.join(META_DIR, "Graph.json")
    if os.path.exists(graph_path):
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"nodes": [], "links": []}

def save_graph(graph_data):
    graph_path = os.path.join(META_DIR, "Graph.json")
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)

def get_existing_folders():
    folders = []
    if os.path.exists(WIKI_DIR):
        for root, dirs, _ in os.walk(WIKI_DIR):
            for d in dirs:
                full_path = os.path.join(root, d)
                rel = os.path.relpath(full_path, ROOT_DIR).replace("\\", "/")
                folders.append(rel)
    if not folders:
        return get_default_categories()
    return folders

def is_raw_file_processed(raw_rel_path, graph_data):
    for node in graph_data.get("nodes", []):
        if node.get("raw_source") == raw_rel_path:
            return True
    return False

def generate_content_via_llm(prompt, model="gemini-2.5-flash", retries=3):
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts":[{"text": prompt}]}]}
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429:
                import time
                time.sleep(10)
                continue
        except Exception:
            pass
    return ""

def extract_json(response_text):
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)

def process_raw_file(file_path):
    rel_raw = os.path.relpath(file_path, ROOT_DIR).replace("\\", "/")
    print(f"🔄 파일 처리 중: {rel_raw}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    existing_categories = get_existing_folders()
    policy = read_policy_content()
    
    prompt = f"""You are the P-Reinforce Architect (The Autonomous Gardener), a knowledge engine that transforms raw information into high-quality, structured wiki files based on RL policies.

Original Document Content:
\"\"\"
{content}
\"\"\"

Existing Categories in `10_Wiki/`:
{json.dumps(existing_categories, ensure_ascii=False, indent=2)}

Current Categorization Policy from `20_Meta/Policy.md`:
\"\"\"
{policy}
\"\"\"

Task:
Analyze the original document content, extract its key patterns and insights, classify it correctly, and synthesize high-quality structured content following Karpathy's LLM-Wiki architecture.

Please output your response as a valid JSON object strictly containing the following keys (DO NOT output anything else before or after the JSON, do NOT wrap in ```json ``` markdown code blocks):
{{
  "category": "String. The target category folder path within 10_Wiki/. Must start with '10_Wiki/'. Use existing folders if similarity is >= 85%. E.g., '10_Wiki/💡 Topics/AI Business'. If no existing folder fits, generate a new specific category/folder under one of the 4 root folders: '10_Wiki/🛠️ Projects/', '10_Wiki/💡 Topics/', '10_Wiki/⚖️ Decisions/', '10_Wiki/🚀 Skills/'. For example, if it's about psychology and there is no psychology folder, derive '10_Wiki/💡 Topics/Psychology'.",
  "title": "String. Suitable title for the document.",
  "confidence_score": Float between 0.0 and 1.0. RL confidence score.,
  "tags": ["tag1", "tag2"],
  "karpathy_summary": "String. Single-sentence core insight.",
  "synthesized_content": "String. Extract patterns and detail bullet points.",
  "contradictions": "String. Past contradictions or policy reinforcement details.",
  "parent": "String. Parent concept/category name.",
  "related": ["concept_A", "concept_B"]
}}
"""
    try:
        response_text = generate_content_via_llm(prompt)
        parsed = extract_json(response_text)
    except Exception as e:
        print(f"❌ JSON 파싱 실패 ({rel_raw}): {e}")
        # fallback parsing or generic template
        parsed = {
            "category": "10_Wiki/💡 Topics",
            "title": os.path.basename(file_path).replace(".md", ""),
            "confidence_score": 0.5,
            "tags": ["General"],
            "karpathy_summary": "자동 요약 생성 실패",
            "synthesized_content": content,
            "contradictions": "N/A",
            "parent": "10_Wiki",
            "related": []
        }
        
    doc_id = str(uuid.uuid4())
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Check category path
    cat_path = parsed.get("category", "10_Wiki/💡 Topics")
    if not cat_path.startswith("10_Wiki/"):
        cat_path = "10_Wiki/💡 Topics/" + cat_path.replace("10_Wiki/", "")
        
    full_cat_path = os.path.join(ROOT_DIR, cat_path)
    os.makedirs(full_cat_path, exist_ok=True)
    
    # Save the markdown Wiki file
    safe_title = parsed.get("title", "Untitled").replace("/", "-").replace("\\", "-")
    filename = f"{safe_title}.md"
    target_file_path = os.path.join(full_cat_path, filename)
    
    wiki_template = f"""---
id: {doc_id}
category: "[[{cat_path}]]"
confidence_score: {parsed.get('confidence_score', 0.8)}
tags: {json.dumps(parsed.get('tags', []), ensure_ascii=False)}
last_reinforced: {today}
github_commit: "latest"
---

# [[{parsed.get('title', safe_title)}]]

## 📌 한 줄 통찰 (The Karpathy Summary)
> {parsed.get('karpathy_summary', '')}

## 📖 구조화된 지식 (Synthesized Content)
{parsed.get('synthesized_content', '')}

## ⚠️ 모순 및 업데이트 (Contradictions & RL Update)
- **과거 데이터와의 충돌:** 없음
- **정책 변화:** {parsed.get('contradictions', '이 문서를 통해 강화된 분류 기준 설명')}

## 🔗 지식 연결 (Graph)
- **Parent:** [[{parsed.get('parent', '10_Wiki')}]]
- **Related:** {', '.join([f'[[{r}]]' for r in parsed.get('related', [])])}
- **Raw Source:** [[{rel_raw}]]
"""
    with open(target_file_path, "w", encoding="utf-8") as f:
        f.write(wiki_template)
        
    # Update graph data
    graph = load_graph()
    graph["nodes"].append({
        "id": doc_id,
        "title": parsed.get("title", safe_title),
        "path": os.path.relpath(target_file_path, ROOT_DIR).replace("\\", "/"),
        "category": cat_path,
        "tags": parsed.get("tags", []),
        "raw_source": rel_raw
    })
    
    # Create links
    for rel_concept in parsed.get("related", []):
        graph["links"].append({
            "source": doc_id,
            "target": rel_concept,
            "type": "related"
        })
    if parsed.get("parent"):
        graph["links"].append({
            "source": doc_id,
            "target": parsed.get("parent"),
            "type": "parent"
        })
        
    save_graph(graph)
    print(f"✅ 파일 저장 완료: {target_file_path}")
    return filename

def update_index():
    index_path = os.path.join(META_DIR, "Index.md")
    content = "# 🗺️ Wiki Index (Table of Contents)\n\n"
    content += "에이전트가 관리하는 지식 위키의 전체 폴더 트리입니다.\n\n"
    
    if os.path.exists(WIKI_DIR):
        for root, dirs, files in os.walk(WIKI_DIR):
            rel_path = os.path.relpath(root, ROOT_DIR).replace("\\", "/")
            if rel_path == "10_Wiki":
                continue
            
            # Subfolders
            depth = rel_path.count("/") - 1
            if depth >= 0:
                indent = "  " * depth
                folder_name = os.path.basename(root)
                content += f"{indent}- **📁 {folder_name}** (`{rel_path}`)\n"
                
            for file in files:
                if file.endswith(".md"):
                    file_indent = "  " * (depth + 1)
                    title = file.replace(".md", "")
                    file_rel = os.path.join(root, file)
                    clean_rel = os.path.relpath(file_rel, ROOT_DIR).replace("\\", "/")
                    content += f"{file_indent}- 📄 [{title}](file:///{ROOT_DIR}/{clean_rel})\n"
                    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Index.md 업데이트 완료")

def check_refactoring_proposal():
    policy_path = os.path.join(META_DIR, "Policy.md")
    proposals = []
    if os.path.exists(WIKI_DIR):
        for root, _, files in os.walk(WIKI_DIR):
            md_files = [f for f in files if f.endswith(".md")]
            if len(md_files) > 12:
                rel = os.path.relpath(root, ROOT_DIR).replace("\\", "/")
                proposals.append(f"- [⚠️ 구조 재설계 제안] `{rel}` 폴더에 {len(md_files)}개의 문서가 있습니다. 하위 카테고리로 세분화하는 것을 권장합니다.")
                
    if proposals:
        with open(policy_path, "a", encoding="utf-8") as f:
            f.write("\n## ⚠️ 구조 재설계 제안 (Refactoring Proposal)\n")
            f.writelines(proposals)
        print("✅ 구조 재설계 제안이 Policy.md에 추가되었습니다.")

def git_sync(action_summary):
    try:
        subprocess.run(["git", "add", "."], capture_output=True, text=True)
        commit_msg = f"[P-Reinforce] {action_summary}"
        subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        print(f"🚀 Git Sync 완료: {commit_msg}")
    except Exception as e:
        print(f"ℹ️ Git 동기화 정보: {e}")

def main():
    print("🌿 P-Reinforce 지식 정원사 작동을 시작합니다...")
    init_directories()
    init_policy()
    init_graph()
    
    graph = load_graph()
    
    processed_count = 0
    # Search all md files in 00_Raw
    if os.path.exists(RAW_DIR):
        for root, _, files in os.walk(RAW_DIR):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel_raw = os.path.relpath(full_path, ROOT_DIR).replace("\\", "/")
                    if not is_raw_file_processed(rel_raw, graph):
                        try:
                            process_raw_file(full_path)
                            processed_count += 1
                        except Exception as e:
                            print(f"❌ 파일 처리 오류 ({rel_raw}): {e}")
                            
    if processed_count > 0:
        update_index()
        check_refactoring_proposal()
        git_sync(f"3개 문서 지식화 및 연결 최적화 ({datetime.date.today().strftime('%Y-%m-%d')})")
    else:
        print("ℹ️ 새로 처리할 문서가 없습니다.")
        
    print("🌿 P-Reinforce 지식 정원사 작업을 성공적으로 마쳤습니다.")

if __name__ == "__main__":
    main()
