from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime

def get_press_name(url):
    """URL을 분석하여 언론사 이름을 반환하는 함수"""
    press_map = {
        'chosun.com': '조선일보',
        'biz.chosun.com': '조선비즈',
        'tvchosun.com': 'TV조선',
        'yna.co.kr': '연합뉴스',
        'hankyung.com': '한국경제',
        'mk.co.kr': '매일경제',
        'sedaily.com': '서울경제',
        'edaily.co.kr': '이데일리',
        'newsis.com': '뉴시스',
        'news1.kr': '뉴스1',
        'asiae.co.kr': '아시아경제',
        'mt.co.kr': '머니투데이',
        'heraldcorp.com': '헤럴드경제',
        'fnnews.com': '파이낸셜뉴스',
        'khan.co.kr': '경향신문',
        'hani.co.kr': '한겨레',
        'donga.com': '동아일보',
        'joongang.co.kr': '중앙일보',
        'segye.com': '세계일보',
        'ytn.co.kr': 'YTN',
        'sbs.co.kr': 'SBS',
        'kbs.co.kr': 'KBS',
        'mbn.co.kr': 'MBN',
        'jtbc.co.kr': 'JTBC',
        'zdnet.co.kr': '지디넷코리아',
        'inews24.com': '아이뉴스24',
        'digitaltimes.co.kr': '디지털타임스'
    }
    
    for domain, name in press_map.items():
        if domain in url:
            return name
    return "언론사" # 매칭되는 게 없을 때 기본값

def scrap_naver_perfect(keyword, pages=1):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    results = []
    
    try:
        for p in range(pages):
            start_val = p * 10 + 1
            # url = f"https://search.naver.com/search.naver?where=news&query={keyword}&pd=1&start={start_val}"
            url= "https://search.naver.com/search.naver?ssc=tab.news.all&query=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds=2026.02.25&de=2026.02.25&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom20260225to20260225&is_sug_officeid=0&office_category=0&service_area=0"
            driver.get(url)
            time.sleep(5) 

            # 사용자님 환경에서 유일하게 작동하는 a 태그 방식
            all_links = driver.find_elements(By.TAG_NAME, "a")
            
            for el in all_links:
                try:
                    title = el.text.strip()
                    link = el.get_attribute("href")
                    
                    if len(title) > 10 and any(kw in title for kw in ["삼성", "반도체", "전자"]):
                        if link and "naver.com" not in link:
                            if not any(res['기사 제목'] == title for res in results):
                                
                                # 매체 이름 추출 (URL 기반)
                                press = get_press_name(link)
                                
                                # 날짜 및 내용 확보 시도
                                try:
                                    parent = el.find_element(By.XPATH, "./ancestor::li")
                                    content = parent.find_element(By.CSS_SELECTOR, "div.news_dsc, .api_txt_lines").text.strip()
                                    # 날짜는 최대한 텍스트에서 추출, 안되면 오늘 날짜
                                    date_text = parent.find_element(By.CSS_SELECTOR, ".info, .date").text.strip()
                                    date = date_text if len(date_text) < 15 else datetime.now().strftime("%Y.%m.%d")
                                except:
                                    content = title
                                    date = datetime.now().strftime("%Y.%m.%d")
                                
                                results.append({
                                    "기사 제목": title,
                                    "날짜": date,
                                    "매체 이름": press,
                                    "내용": content
                                })
                except:
                    continue
            print(f"✅ {p+1}페이지 완료... 현재 {len(results)}건 확보")
            
    finally:
        if results:
            df = pd.DataFrame(results)
            df = df.drop_duplicates(subset=['기사 제목'])
            df = df[["기사 제목", "날짜", "매체 이름", "내용"]]
            df.to_csv("naver_news_perfect.csv", index=False, encoding='utf-8-sig')
            print(f"\n🎉 드디어 완성! 매체 이름까지 분류된 'naver_news_perfect.csv'를 확인하세요.")
        driver.quit()

if __name__ == "__main__":
    scrap_naver_perfect("삼성전자 반도체", pages=3)