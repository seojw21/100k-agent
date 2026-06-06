#!/usr/bin/env python3
import os
import json
import time
import requests
from datetime import datetime

# Path Configuration
BASE_DIR = "/Users/seojeong-won/GEMMA 4"
LM_STUDIO_URL = "http://localhost:1234/v1"
MD_BRAIN_DIR = os.path.join(BASE_DIR, "knowledge", "md_brain")
JSONL_LOG_PATH = os.path.join(BASE_DIR, "knowledge", "antigravity_brain.jsonl")
RAW_EVENTS_DIR = os.path.join(BASE_DIR, "knowledge", "raw_events")

# Ensure target directories exist
os.makedirs(MD_BRAIN_DIR, exist_ok=True)
os.makedirs(RAW_EVENTS_DIR, exist_ok=True)

def ask_gemma_to_structure(raw_content):
    """Query the local Gemma 4 model via LM Studio to parse and analyze the raw trend data."""
    try:
        r_models = requests.get(f"{LM_STUDIO_URL}/models", timeout=5)
        model = r_models.json()["data"][0]["id"]
        
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
        return r_chat.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"❌ LLM request failed: {e}")
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

def check_for_events():
    """Scan the events directory for new files to process."""
    if not os.path.exists(RAW_EVENTS_DIR):
        return
        
    files = [f for f in os.listdir(RAW_EVENTS_DIR) if f.endswith('.txt')]
    for file in files:
        full_path = os.path.join(RAW_EVENTS_DIR, file)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            if not content:
                os.remove(full_path)
                continue
                
            print(f"📡 Event detected: {file}")
            # Request Gemma 4 analysis
            analyzed_md = ask_gemma_to_structure(content)
            
            if analyzed_md:
                # Derive title from filename
                title = os.path.splitext(file)[0]
                save_to_brain(title, analyzed_md, file)
                
            os.remove(full_path)
        except Exception as e:
            print(f"❌ Error processing event file {file}: {e}")

def main():
    print("🤖 Connect-AI Zero-Touch Loop active. Scanning for new events...")
    while True:
        check_for_events()
        time.sleep(5)

if __name__ == "__main__":
    main()
