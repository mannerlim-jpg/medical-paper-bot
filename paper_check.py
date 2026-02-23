import requests
import datetime
import os
import xml.etree.ElementTree as ET

# 검색할 키워드 목록
KEYWORDS = ["TKR", "Robot assisted TKR", "Knee arthroscopy", "Ankle arthroscopy"]

def fetch_papers():
    today = datetime.date.today()
    # 1. 기존에 보고했던 논문 링크들을 읽어옵니다.
    seen_links = set()
    if os.path.exists("papers.md"):
        with open("papers.md", "r", encoding="utf-8") as f:
            content = f.read()
            # 파일 내용 중 http로 시작하는 링크들을 찾아 목록에 넣습니다.
            import re
            links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
            seen_links = set(links)

    # 2. arXiv API로 최신 논문 검색
    base_url = "http://export.arxiv.org/api/query?search_query="
    query = " OR ".join([f'all:"{k}"' for k in KEYWORDS])
    url = base_url + query + "&sortOrder=descending&max_results=20" # 검색 범위를 조금 늘렸습니다.
    
    response = requests.get(url)
    root = ET.fromstring(response.text)
    
    new_papers = []
    
    # 3. 새로 찾은 논문 중 중복되지 않은 것만 골라냅니다.
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
        link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
        
        # '은하계(Galaxy)' 같은 엉뚱한 키워드가 섞이는 것을 방지하기 위한 보조 장치
        # 제목에 키워드 중 하나라도 포함되어 있는지 확인합니다.
        title_upper = title.upper()
        if not any(k.upper() in title_upper for k in KEYWORDS):
            continue

        # 이미 보낸 링크가 아닌 경우에만 저장 목록에 추가
        if link not in seen_links:
            new_papers.append({"title": title, "link": link})

    # 4. 결과 기록 (중복이 없는 경우만 파일에 추가)
    if new_papers:
        with open("papers.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n### 📅 {today} 신규 논문 알림\n")
            for paper in new_papers:
                f.write(f"* **제목:** {paper['title']}\n  * **링크:** {paper['link']}\n")
        print(f"{len(new_papers)}개의 새로운 논문을 찾았습니다.")
    else:
        print("새로 추가할 중복되지 않은 논문이 없습니다.")

if __name__ == "__main__":
    fetch_papers()
