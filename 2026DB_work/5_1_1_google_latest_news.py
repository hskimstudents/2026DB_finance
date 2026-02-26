import feedparser
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import time
import os

def scrap_google_rss_30days(keyword):
    all_results = []
    now = datetime.now()
    
    print(f"🚀 '{keyword}'의 최근 30일치 뉴스 수집을 시작합니다...")

    # 1. 30일 동안 하루씩 루프를 돌며 수집
    for i in range(120):
        # 검색 시작일과 종료일 설정 (하루 단위)
        start_date = (now - timedelta(days=i+1)).strftime('%Y-%m-%d')
        end_date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 구글 뉴스 전용 날짜 검색 쿼리: after:YYYY-MM-DD before:YYYY-MM-DD
        query = f"{keyword} after:{start_date} before:{end_date}"
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        daily_count = len(feed.entries)
        print(f"📅 {start_date} 수집 중... ({daily_count}건 발견)")

        for entry in feed.entries:
            full_title = entry.title
            
            # 제목과 언론사 분리
            if " - " in full_title:
                title = " - ".join(full_title.split(" - ")[:-1])
                press = full_title.split(" - ")[-1]
            else:
                title = full_title
                press = "언론사"

            # 날짜 파싱
            date_struct = entry.published_parsed
            entry_date = datetime(*date_struct[:6])

            all_results.append({
                "날짜": entry_date.strftime("%Y.%m.%d"),
                "기사 제목": title,
                "매체 이름": press,
                
                "datetime_obj": entry_date
            })
        
        # 구글 서버 부하 방지 및 차단 회피를 위한 짧은 휴식
        time.sleep(0.5)

    if all_results:
        # 2. 데이터프레임 생성 및 중복 제거
        df = pd.DataFrame(all_results)
        df = df.drop_duplicates(subset=['기사 제목']) # 제목이 같은 중복 기사 제거

        # 3. 날짜별 정렬 (과거순: True)
        df = df.sort_values(by="datetime_obj", ascending=True)
        df = df.drop(columns=['datetime_obj'])
#C:\Users\qazyo\Desktop\workspace_DB\2026DB_finance\2026DB_work
        # 4. CSV 저장
        file_name = f"C:\\Users\\qazyo\\Desktop\\workspace_DB\\2026DB_finance\\2026DB_work\\google_news_latest_120days_{now.strftime('%m%d')}.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ 수집 완료!")
        print(f"📂 저장된 파일: {file_name}")
        print(f"📊 총 수집 건수 (중복제거 후): {len(df)}건")
        
        # 샘플 확인
        print("\n--- 날짜순 정렬 결과 샘플 ---")
        print(df.head(10))
    else:
        print("❌ 수집된 기사가 없습니다.")

if __name__ == "__main__":
    # 키워드에 "반도체"를 포함하면 검색 결과가 더 정확해집니다.
    scrap_google_rss_30days("삼성전자 반도체")

