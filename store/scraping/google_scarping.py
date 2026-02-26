import feedparser
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse

def scrap_google_rss_7days(keyword):
    # 1. 키워드 설정 및 URL 인코딩
    # 'when:7d' 옵션을 추가하여 구글 서버단에서 일주일치만 필터링하도록 합니다.
    search_query = f"{keyword} when:7d"
    encoded_keyword = urllib.parse.quote(search_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    
    print(f"🚀 '{keyword}'의 최근 7일치 뉴스를 수집 중입니다...")
    
    # 2. RSS 피드 읽기
    feed = feedparser.parse(rss_url)
    results = []

    # 오늘 날짜와 일주일 전 날짜 계산 (필터링용)
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    for entry in feed.entries:
        # 날짜 데이터 파싱
        date_struct = entry.published_parsed
        entry_date = datetime(*date_struct[:6])

        # 최근 7일 이내 기사만 수집 (RSS에서 필터링이 안 될 경우를 대비한 2차 검증)
        if entry_date >= seven_days_ago:
            full_title = entry.title
            
            # 제목과 언론사 분리
            if " - " in full_title:
                title = " - ".join(full_title.split(" - ")[:-1])
                press = full_title.split(" - ")[-1]
            else:
                title = full_title
                press = "언론사"

            results.append({
                "날짜": entry_date.strftime("%Y.%m.%d"),
                "기사 제목": title,
                "매체 이름": press,
                "링크": entry.link,
                "datetime_obj": entry_date # 정렬을 위한 임시 객체
            })

    if results:
        # 3. 데이터프레임 생성
        df = pd.DataFrame(results)
        
        # 4. 날짜별 정렬 (최신순: ascending=False, 과거순: ascending=True)
        # 과거부터 현재까지 흐름을 보려면 True가 좋습니다.
        df = df.sort_values(by="datetime_obj", ascending=True)
        
        # 임시 날짜 객체 컬럼 삭제
        df = df.drop(columns=['datetime_obj'])

        # 5. CSV 저장
        file_name = f"google_news_7days_{datetime.now().strftime('%m%d')}.csv"
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ 수집 및 정렬 완료!")
        print(f"📂 저장된 파일: {file_name}")
        print(f"📊 총 수집 건수: {len(df)}건")
        
        # 결과 확인 (날짜순 정렬 확인용)
        print("\n--- 날짜순 정렬 결과 (과거 -> 현재) ---")
        print(df[['날짜', '기사 제목']].head(10))
    else:
        print("❌ 최근 일주일 이내의 기사를 찾지 못했습니다.")

if __name__ == "__main__":
    # 실행 전 pip install feedparser 하셨는지 확인해주세요!
    scrap_google_rss_7days("삼성전자 반도체")