#!/usr/bin/env python3
import os
import json
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Path Configuration - 상대 경로 자동 획득으로 하드코딩 제거
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LM Studio 포트 설정 (1234)
LM_STUDIO_URL = "http://localhost:1234/v1"
MD_BRAIN_DIR = os.path.join(BASE_DIR, "knowledge", "md_brain")
JSONL_LOG_PATH = os.path.join(BASE_DIR, "knowledge", "antigravity_brain.jsonl")
RAW_EVENTS_DIR = os.path.join(BASE_DIR, "knowledge", "raw_events")

# Ensure target directories exist
os.makedirs(MD_BRAIN_DIR, exist_ok=True)
os.makedirs(RAW_EVENTS_DIR, exist_ok=True)

# Thread Pool for non-blocking file processing
executor = ThreadPoolExecutor(max_workers=2)

def ask_gemma_to_structure(raw_content, retries=3, delay=10):
    """Query the local Gemma 4 model via LM Studio with robust retry logic for loading delays."""
    for attempt in range(retries):
        try:
            r_models = requests.get(f"{LM_STUDIO_URL}/models", timeout=5)
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
                
            if attempt == 0:
                print(f"🧠 Selected LLM Model: {model}")
            
            prompt = f"""Analyze the following raw trend/complaint data and format it as a Connect-AI knowledge node.

Raw Data:
{raw_content}

Formatting Rules:
1. Write a Frontmatter block (---) at the top with:
   - 'tags: [trend, monetization]'
   - 'id: SPEC-TREND-{int(time.time())}'
2. Use a concise and engaging business title as the main heading (#).
3. In the body, summarize:
   - Core Pain Point (what is the user frustration?)
   - Proposed Solution (how to resolve it?)
   - Monetization Strategy (how to capture value?)
4. Add wiki links at the bottom connecting it to other nodes in your Second Brain (e.g. [[NomadGuard AI]], [[SveaTax]]).
"""
            
            r_chat = requests.post(
                f"{LM_STUDIO_URL}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                },
                timeout=120
            )
            
            if r_chat.status_code == 200:
                res_json = r_chat.json()
                if "choices" in res_json:
                    return res_json["choices"][0]["message"]["content"].strip()
                    
            print(f"⚠️ Attempt {attempt+1}: LM Studio API status {r_chat.status_code}. Response: {r_chat.text[:200]}")
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} exception: {e}")
            
        if attempt < retries - 1:
            print(f"⏳ Waiting {delay}s before retry...")
            time.sleep(delay)
            
    print("❌ All LLM structure requests failed.")
    return None

def save_to_brain(title, content_md, file_source):
    """Store raw JSONL entry and output the Markdown node for Connect-AI Lab."""
    # Write Markdown file for the visualization graph
    safe_title = "".join([c if c.isalnum() else "_" for c in title])
    filename = f"{safe_title}_{int(time.time())}.md"
    file_path = os.path.join(MD_BRAIN_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_md)
    print(f"✅ Created new knowledge node: {file_path}")
    
    # Save the log entry to JSONL
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "node_file": filename,
        "title": title,
        "source": file_source
    }
    with open(JSONL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    print(f"💾 Data accumulated in: {JSONL_LOG_PATH}")

def process_single_file(filepath):
    """Process a single raw event file and structure it via LLM."""
    try:
        if not os.path.exists(filepath):
            return
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        if not content:
            try:
                os.remove(filepath)
            except Exception:
                pass
            return
            
        filename = os.path.basename(filepath)
        print(f"📡 Processing event file: {filename}")
        analyzed_md = ask_gemma_to_structure(content)
        
        if analyzed_md:
            title = os.path.splitext(filename)[0]
            save_to_brain(title, analyzed_md, filename)
            
        try:
            os.remove(filepath)
            print(f"🗑️ Cleaned up event file: {filename}")
        except Exception as e:
            print(f"⚠️ Could not delete processed file {filepath}: {e}")
    except Exception as e:
        print(f"❌ Error processing event file {filepath}: {e}")

def process_single_file_with_delay(filepath, delay=0.5):
    """Wait briefly before processing to ensure file write is complete."""
    time.sleep(delay)
    process_single_file(filepath)

def initial_scan():
    """Scan existing files in RAW_EVENTS_DIR before starting watchdog."""
    if not os.path.exists(RAW_EVENTS_DIR):
        return
    files = [f for f in os.listdir(RAW_EVENTS_DIR) if f.endswith('.txt')]
    for file in files:
        full_path = os.path.join(RAW_EVENTS_DIR, file)
        process_single_file(full_path)

class EventFileHandler(FileSystemEventHandler):
    """Watchdog event handler for raw event files."""
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.txt'):
            print(f"🔔 File created event: {event.src_path}")
            executor.submit(process_single_file_with_delay, event.src_path)
            
    def on_moved(self, event):
        if event.is_directory:
            return
        if event.dest_path.endswith('.txt'):
            print(f"🔔 File moved/renamed event: {event.dest_path}")
            executor.submit(process_single_file_with_delay, event.dest_path)

def main():
    print("🤖 Connect-AI Zero-Touch Loop active. Watching RAW_EVENTS_DIR...")
    # 1. Scan pre-existing files
    initial_scan()
    
    # 2. Start watchdog observer
    event_handler = EventFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=RAW_EVENTS_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    executor.shutdown(wait=True)

if __name__ == "__main__":
    main()
