import os
import json
import collections
import random
import re

def generate_dashboard():
    base_dir = r'd:\100k\knowledge\md_brain'
    
    # 1. Load data from markdown files in md_brain
    db = []
    if not os.path.exists(base_dir):
        print(f"Error: Directory not found - {base_dir}")
        return

    for root, dirs, files in os.walk(base_dir):
        # Skip hidden or git folders
        if '.git' in root or '.obsidian' in root:
            continue
            
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(root, base_dir)
                if rel_path == '.':
                    category = '_root'
                else:
                    category = rel_path.replace('\\', '/')
                
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    lines = content.split('\n')
                    title = file.replace('.md', '')
                    
                    # Try to extract H1 title
                    if lines and lines[0].startswith('# '):
                        title = lines[0][2:].strip()
                    
                    # Extract tags
                    tags = []
                    tags_match = re.search(r'\*\*태그:\*\*\s*(.+)', content)
                    if tags_match:
                        raw_tags = tags_match.group(1)
                        tags = [t.strip() for t in raw_tags.split() if t.strip().startswith('#')]
                    else:
                        tags = list(set(re.findall(r'(?<!\S)#[a-zA-Z0-9_가-힣]+', content)))
                    
                    # Extract pain point or short description
                    pain_match = re.search(r'## 😟 핵심 통증.*?\n(.*?)\n', content, re.DOTALL)
                    pain = pain_match.group(1).strip() if pain_match else ""
                    if not pain:
                        pain = " ".join(lines[1:5])[:100]
                        
                    # Extract score
                    score_match = re.search(r'\*\*점수:\*\*\s*(\d+)', content)
                    score = int(score_match.group(1)) if score_match else 0
                        
                    db.append({
                        'category': category,
                        'idea_name': title,
                        'pain_point': pain,
                        'score': score,
                        'tags': tags,
                        'filepath': os.path.relpath(filepath, base_dir)
                    })
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    categories = collections.Counter(d.get('category', '_root') for d in db)
    total_ideas = len(db)
    
    # Sort top ideas by score
    top_ideas = sorted(db, key=lambda x: int(x.get('score', 0)), reverse=True)[:10]

    # Vis.js Network Data Preparation
    nodes = []
    edges = []
    
    # Category colors
    palette = ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#fb923c', '#ec4899', '#14b8a6', '#6366f1']
    cat_colors = {}
    
    cat_keys = list(categories.keys())
    for i, cat in enumerate(cat_keys):
        cat_colors[cat] = palette[i % len(palette)]
    
    tag_nodes = set()
    
    # Idea nodes (Sample up to 1000 for performance)
    display_db = db if len(db) <= 1000 else random.sample(db, 1000)
    
    for i, idea in enumerate(display_db):
        idea_id = f"idea_{i}"
        cat = idea.get('category', '_root')
        
        name = idea.get('idea_name', '제목 없음').replace('"', "'").replace('\n', ' ')
        pain = str(idea.get('pain_point', '')).replace('"', "'").replace('\n', ' ')[:100] + "..."
        tags = idea.get('tags', [])
        tag_str = " ".join(tags)
        color = cat_colors.get(cat, '#ffffff')
        
        nodes.append({
            "id": idea_id,
            "label": "", 
            "title": f"<div style='background:#1e293b; padding:10px; border-radius:8px; color:#fff;'><strong style='color:{color}'>{name}</strong><br><span style='font-size:0.8em; color:{color};'>{tag_str}</span><br><br><span style='font-size:0.9em; color:#94a3b8;'>{pain}</span></div>",
            "size": 6,
            "color": {"border": color, "background": "transparent", "hover": {"border": "#ffffff", "background": color}}
        })
        
        # Connect to tag nodes
        for tag in tags:
            tag_id = f"tag_{tag}"
            if tag not in tag_nodes:
                tag_nodes.add(tag)
                nodes.append({
                    "id": tag_id,
                    "label": tag,
                    "size": 12,
                    "font": {"color": "#cbd5e1", "size": 14},
                    "color": {"border": "#ffffff", "background": "#334155"}
                })
            
            edges.append({
                "from": idea_id,
                "to": tag_id,
                "color": {"color": "rgba(255,255,255,0.15)"}
            })
            
    # Fallback to prevent isolated nodes if no tags exist
    if len(tag_nodes) == 0:
        nodes.append({"id": "hub", "label": "MD_BRAIN", "size": 30, "color": {"border": "#f87171", "background": "transparent"}})
        for i, idea in enumerate(display_db):
            edges.append({"from": "hub", "to": f"idea_{i}", "color": {"color": "rgba(255,255,255,0.08)"}})

    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)
    
    # Legend HTML
    legend_html = ""
    for cat, color in cat_colors.items():
        count = categories[cat]
        legend_html += f"""
        <div class="legend-item">
            <span class="dot" style="background-color: {color};"></span>
            <span class="label">{cat}</span>
            <span class="count">{count}</span>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>🧠 지식 네트워크 • MD_BRAIN</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0b0f19;
                --card-bg: #161b22;
                --text: #f8fafc;
                --accent: #5eead4;
            }}
            body {{
                font-family: 'Pretendard', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 20px;
            }}
            .header-area {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                max-width: 1400px;
                margin: 0 auto 20px auto;
                position: relative;
                z-index: 10;
            }}
            .title-section h1 {{
                margin: 0;
                color: var(--accent);
                font-size: 2rem;
                font-weight: 800;
                display: flex;
                align-items: center;
                gap: 10px;
                text-shadow: 0 0 15px rgba(94, 234, 212, 0.4);
            }}
            .subtitle {{
                color: #8b949e;
                font-size: 0.95rem;
                margin-top: 8px;
                letter-spacing: 0.5px;
            }}
            .legend-box {{
                background: #11141c;
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 16px;
                min-width: 200px;
                max-height: 200px;
                overflow-y: auto;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-size: 0.85rem;
            }}
            .legend-item:last-child {{
                margin-bottom: 0;
            }}
            .legend-item .dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 12px;
            }}
            .legend-item .label {{
                color: #c9d1d9;
                flex-grow: 1;
                margin-right: 15px;
            }}
            .legend-item .count {{
                color: #8b949e;
            }}
            
            #mynetwork {{
                width: 100%;
                height: 70vh;
                background: var(--bg);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 16px;
                margin: 0 auto 40px auto;
                max-width: 1400px;
            }}
            .vis-tooltip {{
                position: absolute;
                background: transparent;
                padding: 0;
                border: none;
                pointer-events: none;
            }}
            
            /* Bottom Stats */
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
            }}
            .card {{
                background: var(--card-bg);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid rgba(255,255,255,0.05);
            }}
            h2 {{ margin-top: 0; color: #e2e8f0; font-size: 1.2rem; margin-bottom: 20px; }}
            ul {{ list-style: none; padding: 0; margin: 0; }}
            li {{
                background: rgba(255,255,255,0.02);
                margin-bottom: 12px;
                padding: 16px;
                border-radius: 8px;
                border-left: 3px solid var(--accent);
            }}
            .idea-title {{ font-weight: 600; color: #fff; margin-bottom: 8px; }}
            .idea-desc {{ color: #8b949e; font-size: 0.9rem; line-height: 1.5; }}
            .idea-path {{ color: var(--accent); font-size: 0.75rem; margin-bottom: 8px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="header-area">
            <div class="title-section">
                <h1>✨ 지식 네트워크 • MD_BRAIN</h1>
                <div class="subtitle">{total_ideas} 마크다운 파일 · {len(tag_nodes)} 태그 클러스터 · {len(display_db)} 시각화 노드 · {len(cat_keys)} 디렉토리</div>
            </div>
            <div class="legend-box">
                {legend_html}
            </div>
        </div>

        <div id="mynetwork"></div>
        
        <div class="container">
            <div class="card" style="grid-column: 1 / -1;">
                <h2>🔥 MD_BRAIN 최고 평점 아이디어 Top 10</h2>
                <ul>
"""
    for idea in top_ideas:
        name = idea.get('idea_name', '제목 없음')
        score = idea.get('score', '?')
        pain = str(idea.get('pain_point', ''))
        path = str(idea.get('filepath', ''))
        pain_trunc = pain[:150] + "..." if len(pain) > 150 else pain
        
        html_content += f"""
                    <li>
                        <div class="idea-path">{path}</div>
                        <div class="idea-title">{name} <span style="color:var(--accent); font-size:0.85rem; margin-left:10px;">★ {score}점</span></div>
                        <div class="idea-desc">{pain_trunc}</div>
                    </li>
        """

    html_content += f"""
                </ul>
            </div>
        </div>

        <script>
            // Vis.js Network
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});

            var container = document.getElementById('mynetwork');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    borderWidth: 2,
                    font: {{ color: '#8b949e', face: 'Pretendard' }}
                }},
                edges: {{
                    width: 1,
                    smooth: {{ type: 'continuous' }}
                }},
                physics: {{
                    forceAtlas2Based: {{
                        gravitationalConstant: -26,
                        centralGravity: 0.005,
                        springLength: 230,
                        springConstant: 0.18
                    }},
                    maxVelocity: 146,
                    solver: 'forceAtlas2Based',
                    timestep: 0.35,
                    stabilization: {{ iterations: 150 }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """

    output_path = os.path.join(base_dir, 'knowledge_dashboard.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✨ 네트워크 시각화가 성공적으로 업데이트 되었습니다: {output_path}")
    print(f"해당 경로에서 HTML 파일을 열어 멋진 네트워크 뷰를 확인하세요!")

if __name__ == "__main__":
    generate_dashboard()
