import requests
import datetime
import os
import xml.etree.ElementTree as ET
import re

# 1. 카테고리별 키워드 및 의료 필터 강화
CATEGORIES = {
    "🤖 로봇 보조 수술 (Robot-Assisted)": ["ROBOT ASSISTED", "SURGICAL ROBOT", "MAKO", "ROSA", "NAVIO"],
    "🦶 발목 및 족부 (Ankle & Foot)": ["ANKLE ARTHROSCOPY", "TALAR", "ANKLE FRACTURE"],
    "🦵 무릎 및 인공관절 (Knee & TKR)": ["TKR", "TKA", "KNEE ARTHROSCOPY", "KNEE REPLACEMENT"]
}

# 로봇 관련 논문 중 의료용만 골라내기 위한 필수 단어
MEDICAL_FILTER = ["SURGERY", "SURGICAL", "PATIENT", "CLINICAL", "ORTHOPEDIC", "KNEE", "ANKLE", "MEDICINE"]

def fetch_papers():
    today = datetime.date.today()
    seen_links = set()
    
    if os.path.exists("papers.md"):
        with open("papers.md", "r", encoding="utf-8") as f:
            seen_links = set(re.findall(r'https?://arxiv\.org/abs/\S+', f.read()))

    # 검색 쿼리: 의학 관련성이 높은 논문만 가져오도록 키워드 조합
    all_search_terms = [k for v in CATEGORIES.values() for k in v]
    query = " OR ".join([f'all:"{k}"' for k in all_search_terms])
    url = f"https://export.arxiv.org/api/query?search_query={query}&sortOrder=descending&max_results=50"
    
    response = requests.get(url)
    root = ET.fromstring(response.text)
    
    classified_report = {cat: [] for cat in CATEGORIES.keys()}

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
        # 링크를 http에서 https로 강제 변경 (연결성 강화)
        link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip().replace('http://', 'https://')
        
        if link in seen_links: continue

        title_upper = title.upper()
        
        # 카테고리 배정 및 필터링
        for cat, keywords in CATEGORIES.items():
            if any(k in title_upper for k in keywords):
                # 로봇 카테고리의 경우 의료 관련 단어가 반드시 포함되어야 함
                if "🤖" in cat:
                    if not any(mf in title_upper for mf in MEDICAL_FILTER):
                        continue
                
                # 카테고리당 최대 5개까지만 담기
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
                        # 구글챗에서 클릭하기 가장 편한 형태로 링크 제공
                        f.write(f"* **제목:** {p['title']}\n  * **원문링크:** <{p['link']}>\n")
        print("필터링 및 분류 완료!")
    else:
        print("새로 추가할 논문이 없습니다.")

if __name__ == "__main__":
    fetch_papers()
