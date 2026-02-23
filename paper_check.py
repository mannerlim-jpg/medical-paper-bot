import requests
import datetime
import os
import xml.etree.ElementTree as ET
import re

# 1. 카테고리별 키워드 - 로봇 보조 TKR에 집중하도록 수정
CATEGORIES = {
    "🤖 로봇 보조 TKR (Robot-Assisted TKR)": ["ROBOT ASSISTED TKR", "ROBOT ASSISTED TKA", "ROBOTIC TKR", "ROBOTIC TKA", "ROBOTIC TOTAL KNEE"],
    "🦵 일반 TKR 및 인공관절 (General TKR)": ["TOTAL KNEE REPLACEMENT", "TOTAL KNEE ARTHROPLASTY", "TKR", "TKA"],
    "🔍 무릎 및 발목 관절경 (Arthroscopy)": ["KNEE ARTHROSCOPY", "ANKLE ARTHROSCOPY", "ARTHROSCOPIC SURGERY"]
}

def fetch_papers():
    today = datetime.date.today()
    seen_links = set()
    
    # 중복 체크
    if os.path.exists("papers.md"):
        with open("papers.md", "r", encoding="utf-8") as f:
            seen_links = set(re.findall(r'https?://arxiv\.org/abs/\S+', f.read()))

    # arXiv API 검색
    all_search_terms = [k for v in CATEGORIES.values() for k in v]
    query = " OR ".join([f'all:"{k}"' for k in all_search_terms])
    url = f"https://export.arxiv.org/api/query?search_query={query}&sortOrder=descending&max_results=50"
    
    response = requests.get(url)
    root = ET.fromstring(response.text)
    
    classified_report = {cat: [] for cat in CATEGORIES.keys()}

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
        link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip().replace('http://', 'https://')
        
        if link in seen_links: continue

        title_upper = title.upper()
        
        # 카테고리 배정 로직
        for cat, keywords in CATEGORIES.items():
            if any(k in title_upper for k in keywords):
                # 🤖 로봇 카테고리의 경우 'KNEE'나 'TKR/TKA'가 제목에 반드시 포함되어야 함 (이중 필터)
                if "🤖" in cat:
                    if not any(target in title_upper for target in ["KNEE", "TKR", "TKA"]):
                        continue
                
                if len(classified_report[cat]) < 5:
                    classified_report[cat].append({"title": title, "link": link})
                break
        
    has_new_content = any(len(papers) > 0 for papers in classified_report.values())

    if has_new_content:
        with open("papers.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n## 📅 {today} 신규 논문 브리핑\n")
            for cat, papers in classified_report.items():
                if papers:
                    f.write(f"\n### {cat}\n")
                    for p in papers:
                        # 링크를 괄호 없이 Raw URL로 제공하여 클릭 문제 해결
                        f.write(f"* **제목:** {p['title']}\n  * **원문:** {p['link']}\n")
        print("필터링 및 분류 완료!")
    else:
        print("새로 추가할 논문이 없습니다.")

if __name__ == "__main__":
    fetch_papers()
