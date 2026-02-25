import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time

def get_samsung_news(limit=5):
    # 1. 네이버 뉴스 검색 결과 URL (삼성전자 검색)
    # start 파라미터를 조절하면 페이지 이동이 가능합니다 (1, 11, 21...)
    search_url = f"https://search.naver.com/search.naver?where=news&query=삼성전자"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. 뉴스 기사 링크 추출 (네이버 인링크 및 언론사 직링크 포함)
    news_items = soup.select("a.news_tit")
    
    count = 0
    results = []

    print(f"--- '삼성전자' 관련 뉴스 수집 시작 (목표: {limit}개) ---")

    for item in news_items:
        if count >= limit:
            break
            
        url = item['href']
        
        try:
            # 3. newspaper4k를 이용한 본문 추출
            article = Article(url, language='ko') 
            article.download()
            article.parse()
            
            # 데이터 저장
            news_data = {
                "title": article.title,
                "date": article.publish_date,
                "text": article.text[:200] + "...", # 본문은 앞부분만 저장 (샘플)
                "url": url
            }
            results.append(news_data)
            
            print(f"[{count+1}] 수집 완료: {article.title}")
            count += 1
            
            # 서버 과부하 방지를 위한 짧은 휴식
            time.sleep(1) 
            
        except Exception as e:
            print(f"실패 ({url}): {e}")
            continue

    return results

# 실행: 5개의 기사 가져오기
news_list = get_samsung_news(limit=5)

# 결과 출력
print("\n--- 수집 결과 요약 ---")
for news in news_list:
    print(f"제목: {news['title']}\n링크: {news['url']}\n")