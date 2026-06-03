import os
import json
import time
import requests
import google.generativeai as genai

# ==========================================
# AI Agents for Solopreneurs - WP Automator
# ==========================================

WP_URL = "https://your-wordpress-site.com/wp-json/wp/v2"
WP_USERNAME = os.environ.get("WP_USERNAME", "admin")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "xxxx xxxx xxxx xxxx")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class WPAgenticPipeline:
    def __init__(self):
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
    def step1_planning_gemini(self):
        print("[Step 1] Planning: Gathering Solopreneur Automation Trends via Gemini...")
        prompt = """
        You are an expert SaaS and Automation analyst for solopreneurs.
        Analyze and provide 3 trending AI agent automation workflows used by English-speaking 1-person businesses.
        Format the output STRICTLY as a JSON array of objects. Do not include markdown code blocks.
        Each object should have:
        - "tool_name": Primary tool used (e.g., Make.com, Zapier, Claude)
        - "category": Marketing, Customer Support, Analytics, etc.
        - "core_problem": What solopreneur pain point it solves.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            data = json.loads(raw_text.strip())
            print(f"-> Found {len(data)} trends.")
            return data
        except Exception as e:
            print(f"Error fetching from Gemini: {e}. Using fallback mock data.")
            return [
                {
                    "tool_name": "Make.com + Claude",
                    "category": "SEO & Content",
                    "core_problem": "Spending too much time writing blog posts instead of building products."
                }
            ]

    def step2_structuring_and_localization(self, data):
        print("[Step 2 & 3] Localization: Generating engaging English micro-copy...")
        structured_posts = []
        
        for item in data:
            print(f"   -> Processing: {item['tool_name']}")
            
            localized_title = f"Automate {item['category']} with {item['tool_name']}"
            
            content_prompt = f"""
            Write a short, engaging 2-paragraph blueprint for a solopreneur to automate {item['category']} using {item['tool_name']}.
            The core problem it solves is: {item['core_problem']}.
            Format it as HTML paragraphs `<p>...</p>`.
            """
            
            try:
                response = self.gemini_model.generate_content(content_prompt)
                html_content = response.text.strip()
            except Exception as e:
                html_content = f"<p>Here is the blueprint to automate your {item['category']}...</p>"
            
            # Use affiliate link pattern for monetization
            affiliate_base = item['tool_name'].split()[0].lower().replace('.com', '')
            affiliate_link = f"https://{affiliate_base}.com/?ref=solopreneur_directory"
            
            post_data = {
                "title": localized_title,
                "content": html_content,
                "status": "publish",
                "acf": { 
                    "category_tag": item['category'],
                    "tool_name": item['tool_name'],
                    "action_button_text": "Download Blueprint",
                    "affiliate_link": affiliate_link
                }
            }
            structured_posts.append(post_data)
            time.sleep(2) # rate limit prevention
            
        return structured_posts

    def step4_publish_local_markdown(self, posts):
        print("[Step 4] Deployment: Saving to local markdown for monetization review...")
        
        out_path = os.path.join(os.path.dirname(__file__), "monetized_directory.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("# 🚀 AI Agents for Solopreneurs Directory\n\n")
            for post in posts:
                f.write(f"## {post['title']}\n")
                f.write(f"**Category:** {post['acf']['category_tag']} | **Tool:** {post['acf']['tool_name']}\n\n")
                f.write(f"{post['content']}\n\n")
                f.write(f"💰 [**{post['acf']['action_button_text']} (Affiliate Link)**]({post['acf']['affiliate_link']})\n\n")
                f.write("---\n\n")
        
        print(f"-> Successfully saved directory content to {out_path}")

if __name__ == "__main__":
    print("==================================================")
    print(" Initiating AI Agentic Workflow for WP Directory ")
    print("==================================================")
    
    pipeline = WPAgenticPipeline()
    trends = pipeline.step1_planning_gemini()
    wp_posts = pipeline.step2_structuring_and_localization(trends)
    pipeline.step4_publish_local_markdown(wp_posts)
    
    print("\n[✓] Workflow Complete. Check monetized_directory.md.")
