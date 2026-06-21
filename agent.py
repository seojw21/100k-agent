#!/usr/bin/env python3
"""
agent.py
===================
Dynamic ReAct (Reasoning + Acting) Agent Loop for Connect-AI.
- Watches tasks.json from the Desktop app.
- Dynamically plans and executes tools (Reddit collection, trend harvesting, search).
- Automatically writes generated knowledge nodes to knowledge/md_brain/ and logs to JSONL.
- Marks tasks as completed in tasks.json.
"""

import os
import json
import time
import sys
import requests
from pathlib import Path
from datetime import datetime

# Path Configurations
BASE_DIR = Path(__file__).parent
TASKS_JSON_PATH = Path("/Users/seojeong-won/Library/Application Support/connect-ai-desktop/tasks.json")
LM_STUDIO_URL = "http://localhost:1234/v1"
# Context window for the model.
OLLAMA_NUM_CTX = 32768
OLLAMA_OUTPUT_RESERVE = 4096
# Cap a single tool output so one large result (e.g. a search dump) cannot
# overflow the context on its own.
MAX_TOOL_OUTPUT_CHARS = 8000
MD_BRAIN_DIR = BASE_DIR / "knowledge" / "md_brain"
JSONL_LOG_PATH = BASE_DIR / "knowledge" / "antigravity_brain.jsonl"

# Ensure directories exist
MD_BRAIN_DIR.mkdir(parents=True, exist_ok=True)

# Set stdout to UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Dynamic Tools
def fetch_trends() -> str:
    """Fetch tech and business trends from GeekNews and HackerNews RSS."""
    try:
        return fetch_daily_ideas()
    except Exception as e:
        return f"Error fetching trends: {e}"

def fetch_reddit_pains() -> str:
    """Trigger reddit_collector to gather real customer pain points."""
    try:
        from reddit_collector import collect_all
        new_items, _ = collect_all(only_pain_signals=True)
        return json.dumps(new_items[:5], ensure_ascii=False)
    except Exception as e:
        return f"Error gathering Reddit pain points: {e}"

def search_knowledge_base(query: str) -> str:
    """Search existing 3,000+ Reddit pain points database."""
    try:
        from knowledge_search import KnowledgeSearch
        ks = KnowledgeSearch()
        if ks.is_ready:
            results = ks.search(query, top_k=3)
            return json.dumps(results, ensure_ascii=False)
        return "Knowledge base not loaded."
    except Exception as e:
        return f"Error searching knowledge base: {e}"

def write_brain_node(title: str, markdown_content: str, source_task: str) -> str:
    """Save structured Markdown report to Second Brain and log to JSONL."""
    try:
        safe_title = "".join([c if c.isalnum() else "_" for c in title])
        filename = f"{safe_title}_{int(time.time())}.md"
        file_path = MD_BRAIN_DIR / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "node_file": filename,
            "title": title,
            "source": source_task
        }
        with open(JSONL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        return f"Success: Node saved to {filename} and logged in JSONL."
    except Exception as e:
        return f"Error saving node: {e}"

def run_terminal_command(command: str) -> str:
    """Execute a shell command on the user's computer safely and return stdout/stderr."""
    # Safe command allowlist
    allowlist = ["python", "python3", "pip", "git", "ls", "echo", "cat"]
    
    tokens = command.strip().split()
    if not tokens:
        return "Error: Empty command."
        
    first_cmd = tokens[0].lower()
    if "/" in first_cmd or "\\" in first_cmd:
        first_cmd = Path(first_cmd).name.lower()
        
    if first_cmd not in allowlist:
        return f"Error: Command execution blocked. The command '{tokens[0]}' is not in the safe allowlist ({', '.join(allowlist)})."

    # Forbidden arguments or patterns (blacklist fallback)
    forbidden_patterns = ["rm ", "sudo", ">", "chmod", "chown", "mkfs", "dd ", ":(){:|:&};:"]
    command_lower = command.lower()
    for kw in forbidden_patterns:
        if kw in command_lower:
            return f"Error: Command execution blocked. Command contains forbidden keyword/pattern '{kw}' for security reasons."

    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(BASE_DIR)
        )
        output = f"Exit Code: {result.returncode}\n"
        if result.stdout:
            output += f"Stdout:\n{result.stdout}\n"
        if result.stderr:
            output += f"Stderr:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {e}"

def write_file(path: str, content: str) -> str:
    """Create or overwrite a file on the local disk, restricted to BASE_DIR."""
    try:
        base_resolved = BASE_DIR.resolve()
        
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = base_resolved / file_path
        
        resolved_path = file_path.resolve()
        
        try:
            resolved_path.relative_to(base_resolved)
        except ValueError:
            return f"Error: Path Traversal detected. The path '{path}' resolves outside the allowed workspace directory."

        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File successfully written to {resolved_path}"
    except Exception as e:
        return f"Error writing file: {e}"

# Context management
def _estimate_tokens(text: str) -> int:
    """Rough token estimate. Mixed KO/EN text is handled more accurately.
    - Korean/Non-ASCII characters: ~1.5 tokens per char
    - English/ASCII characters: ~0.3 tokens per char
    """
    if not text:
        return 0
    non_ascii = sum(1 for c in text if ord(c) > 127)
    ascii_chars = len(text) - non_ascii
    return int(non_ascii * 1.5 + ascii_chars * 0.3) + 1


def trim_messages(messages, num_ctx=OLLAMA_NUM_CTX, reserve=OLLAMA_OUTPUT_RESERVE):
    """Drop the oldest conversational turns until the prompt fits the context.

    The system prompt (index 0) and the initial task message (index 1) are always
    kept; only the accumulated assistant/tool-output tail is trimmed.
    """
    if len(messages) <= 2:
        return messages

    budget = num_ctx - reserve
    head = messages[:2]
    tail = messages[2:]

    def total(msgs):
        return sum(_estimate_tokens(m.get("content", "")) for m in msgs)

    while tail and total(head + tail) > budget:
        # Drop the oldest tail turn first.
        tail.pop(0)

    return head + tail


# Model Connector
def ask_gemma_action(messages, retries=3, delay=10):
    """Call LM Studio model to output the next JSON action with retry logic."""
    for attempt in range(retries):
        try:
            base = LM_STUDIO_URL
            r_models = requests.get(f"{base}/models", timeout=5)
            models_data = r_models.json().get("data", [])
            
            # 'gemma' 단어가 포함된 모델 우선 검색
            model = None
            for m in models_data:
                if "gemma" in m["id"].lower():
                    model = m["id"]
                    break
                    
            if not model and models_data:
                model = models_data[0]["id"]
                
            if not model:
                model = "local-model"

            r_chat = requests.post(
                f"{base}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                    "max_tokens": 4096
                },
                timeout=120
            )
            
            if r_chat.status_code == 200:
                res_json = r_chat.json()
                if "choices" in res_json:
                    return res_json["choices"][0]["message"]["content"].strip()
            
            print(f"⚠️ Model request attempt {attempt+1}: LM Studio API status {r_chat.status_code}")
        except Exception as e:
            print(f"⚠️ Model request attempt {attempt+1} failed: {e}")
            
        if attempt < retries - 1:
            print(f"⏳ Waiting {delay}s before retrying LLM action...")
            time.sleep(delay)
            
    print("❌ All LLM action requests failed.")
    return None

# ReAct Loop Orchestrator
def process_task(task: dict):
    print(f"\n⚡ Processing Task: {task['title']}")
    
    # Initialize agent context
    system_prompt = """You are Zealot, the autonomous coordinator of Connect-AI. Your goal is to solve the given task.
You have access to the following tools via JSON actions:
1. {"tool": "fetch_trends", "args": {}} - Get current tech and startup trends.
2. {"tool": "fetch_reddit_pains", "args": {}} - Harvest fresh customer pain points from Reddit.
3. {"tool": "search_knowledge_base", "args": {"query": "<search_term>"}} - Search the 3000+ core pain points database.
4. {"tool": "write_brain_node", "args": {"title": "<node_title>", "markdown_content": "<markdown>"}} - Save the final report as a Second Brain node.
5. {"tool": "run_terminal_command", "args": {"command": "<command_to_run>"}} - Execute shell commands on the computer (e.g. running scripts, pip install, curl).
6. {"tool": "write_file", "args": {"path": "<file_path>", "content": "<file_content>"}} - Write or modify files on the local disk.
7. {"tool": "finish_task", "args": {"summary": "<task_summary>"}} - Finalize and close the task.

Output only a single JSON object matching this schema in every turn:
{"reasoning": "<your step-by-step thinking>", "tool": "<tool_name>", "args": {<arguments>}}
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Task: {task['title']}"}
    ]
    
    steps = 0
    max_steps = 10
    
    while steps < max_steps:
        steps += 1
        messages = trim_messages(messages)
        raw_response = ask_gemma_action(messages)
        if not raw_response:
            break
            
        print(f"🧠 Action Step {steps}: {raw_response}")
        
        # Robust JSON cleaning and extraction
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        # Remove trailing tool call tags if any
        if "<tool_call" in cleaned_response:
            cleaned_response = cleaned_response.split("<tool_call")[0].strip()
        if "<turn" in cleaned_response:
            cleaned_response = cleaned_response.split("<turn")[0].strip()
            
        first_brace = cleaned_response.find("{")
        last_brace = cleaned_response.rfind("}")
        if first_brace != -1 and last_brace != -1:
            cleaned_response = cleaned_response[first_brace:last_brace+1]
            
        try:
            action = json.loads(cleaned_response)
        except Exception as json_err:
            print(f"❌ Model returned invalid JSON ({json_err}). Raw: {raw_response}. Retrying...")
            # Append a correction message to the assistant to prompt correct JSON format
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({"role": "user", "content": "Error: Please output ONLY a valid JSON object matching the schema. Do not output anything else."})
            continue
            
        tool = action.get("tool")
        args = action.get("args", {})
        
        if tool == "finish_task":
            print(f"✅ Task Completed: {args.get('summary')}")
            return True
            
        # Execute tool
        result = ""
        if tool == "fetch_trends":
            result = fetch_trends()
        elif tool == "fetch_reddit_pains":
            result = fetch_reddit_pains()
        elif tool == "search_knowledge_base":
            result = search_knowledge_base(args.get("query", ""))
        elif tool == "write_brain_node":
            result = write_brain_node(args.get("title", "Report"), args.get("markdown_content", ""), task['title'])
        elif tool == "run_terminal_command":
            result = run_terminal_command(args.get("command", ""))
        elif tool == "write_file":
            result = write_file(args.get("path", ""), args.get("content", ""))
        else:
            result = f"Unknown tool: {tool}"
            
        # Update messages (cap oversized tool output to protect the context window)
        result_str = str(result)
        if len(result_str) > MAX_TOOL_OUTPUT_CHARS:
            result_str = result_str[:MAX_TOOL_OUTPUT_CHARS] + "\n...[truncated]"
        messages.append({"role": "assistant", "content": raw_response})
        messages.append({"role": "user", "content": f"Tool Output: {result_str}"})
        time.sleep(1)
        
    return False

# Main Scanning Loop
def main():
    print("🤖 Connect-AI Zealot Agent scanning for open tasks...")
    while True:
        if TASKS_JSON_PATH.exists():
            try:
                with open(TASKS_JSON_PATH, "r", encoding="utf-8") as f:
                    tasks = json.load(f)
            except Exception as e:
                print(f"Error reading tasks: {e}")
                tasks = []
                
            open_tasks = [t for t in tasks if t.get("status") == "open"]
            if open_tasks:
                target_task = open_tasks[0]
                success = process_task(target_task)
                
                if success:
                    # Update status in tasks.json
                    for t in tasks:
                        if t.get("id") == target_task.get("id"):
                            t["status"] = "completed"
                            t["agentEmoji"] = "⚡"
                            
                    try:
                        with open(TASKS_JSON_PATH, "w", encoding="utf-8") as f:
                            json.dump(tasks, f, ensure_ascii=False, indent=2)
                        print(f"💾 Updated task {target_task['id']} status to completed.")
                    except Exception as e:
                        print(f"Error saving tasks: {e}")
            else:
                # Idle check
                time.sleep(5)
        else:
            time.sleep(5)

# Duplicate code from original agent.py helper
def fetch_daily_ideas():
    ideas = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        gn_res = requests.get('https://news.hada.io/rss', headers=headers, timeout=10)
        gn_root = ET.fromstring(gn_res.content)
        gn_items = gn_root.findall('.//item')[:5]
        ideas.append("🇰🇷 [GeekNews trends]")
        for idx, item in enumerate(gn_items, 1):
            ideas.append(f"{idx}. {item.find('title').text}")
    except Exception as e:
        ideas.append(f"GeekNews fail: {e}")
    return "\n".join(ideas)

import xml.etree.ElementTree as ET

if __name__ == "__main__":
    main()
