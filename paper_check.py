import requests
import datetime
import os
import xml.etree.ElementTree as ET
import re

# 1. 카테고리별 키워드 설정
CATEGORIES = {
    "🤖 로봇 보조 수술 (Robot-Assisted)": ["ROBOT", "MAKO", "NAVIO", "ROSA", "NAVIGAT"],
    "🦶 발목 및 족부 (Ankle & Foot)": ["ANKLE", "TALAR", "ACHILLES", "FOOT"],
    "🦵 무릎 및 일반 관절경 (Knee & General)": ["KNEE", "TKR", "TKA", "ARTHROSCOP", "ACL"]
}

def fetch_papers():
    today = datetime.date.today()
    seen_links = set()
    
    # 중복 체크를 위한 기존 링크 읽기
    if os.path.exists("papers.md"):
        with open("papers.md", "r", encoding="utf-8") as f:
            seen_links = set(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', f.read()))

    # arXiv API 검색 (모든 키워드 통합 검색)
    all_keywords = [k for v in CATEGORIES.values() for k in v]
    query = " OR ".join([f'all:"{k}"' for k in all_keywords])
    url = f"http://export.arxiv.org/api/query?search_query={query}&sortOrder=descending&max_results=30"
    
    response = requests.get(url)
    root = ET.fromstring(response.text)
    
    # 분류를 위한 바구니(Dictionary) 준비
    classified_report = {cat: [] for cat in CATEGORIES.keys()}

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
        link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
        
        if link in seen_links:
            continue

        # 제목 분석 후 카테고리 배정
        title_upper = title.upper()
        assigned = False
        for cat, keywords in CATEGORIES.items():
            if any(k in title_upper for k in keywords):
                classified_report[cat].append({"title": title, "link": link})
                assigned = True
                break # 한 논문은 하나의 카테고리에만 배정
        
    # 결과가 있을 때만 파일에 기록 및 보고서 작성
    has_new_content = any(len(papers) > 0 for papers in classified_report.values())

    if has_new_content:
        with open("papers.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n## 📅 {today} 지능형 논문 분류 보고\n")
            for cat, papers in classified_report.items():
                if papers: # 해당 카테고리에 신규 논문이 있을 때만 섹션 생성
                    f.write(f"\n### {cat}\n")
                    for p in papers:
                        f.write(f"* **제목:** {p['title']}\n  * **링크:** {p['link']}\n")
        print("신규 논문 분류 완료!")
    else:
        print("오늘 추가된 신규 논문이 없습니다.")

if __name__ == "__main__":
    fetch_papers()
