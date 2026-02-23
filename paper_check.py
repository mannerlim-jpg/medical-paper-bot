import requests
import datetime

# 검색할 키워드 목록
KEYWORDS = ["TKR", "Robot assisted TKR", "Knee arthroscopy", "Ankle arthroscopy"]

def fetch_papers():
    today = datetime.date.today()
    # arXiv API 사용 (의학/기술 관련 논문 검색)
    base_url = "http://export.arxiv.org/api/query?search_query="
    
    # 키워드들을 검색 쿼리로 변환
    query = " OR ".join([f'all:"{k}"' for k in KEYWORDS])
    url = base_url + query + "&sortOrder=descending&max_results=5"
    
    response = requests.get(url)
    content = response.text
    
    # 간단한 결과물 생성 (papers.md 파일에 적을 내용)
    with open("papers.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n### 📅 {today} 최신 논문 검색 결과\n")
        found = False
        
        # 실제 논문 데이터에서 제목과 링크만 추출 (간이 방식)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            link = entry.find('{http://www.w3.org/2005/Atom}id').text
            f.write(f"* **제목:** {title.strip()}\n  * **링크:** {link}\n")
            found = True
        
        if not found:
            f.write("* 오늘은 검색된 새 논문이 없습니다.\n")

if __name__ == "__main__":
    fetch_papers()
