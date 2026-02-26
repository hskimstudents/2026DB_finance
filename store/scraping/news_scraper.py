# scraping/news_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd


class NewsScraper:

    def __init__(self):
        # 헤더를 좀 더 실제 브라우저처럼 세팅
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    def scrape_naver_news(self, keyword: str, page: int = 1) -> pd.DataFrame:
        """
        네이버 뉴스 검색 결과에서
        제목 / 링크 / 언론사 / 날짜를 수집한다.
        (셀렉터를 최대한 단순화: a.news_tit 기준)
        """

        start = (page - 1) * 10 + 1
        url = (
            "https://search.naver.com/search.naver"
            f"?where=news&sm=tab_opt&query={keyword}&start={start}"
        )

        print("[INFO] 요청 URL:", url)
        resp = requests.get(url, headers=self.headers)
        print("[INFO] status code:", resp.status_code)

        soup = BeautifulSoup(resp.text, "lxml")

        # 디버깅용: 원하면 주석 풀고 HTML 저장해서 직접 구조 확인도 가능
        with open("naver_debug.html", "w", encoding="utf-8") as f:
            f.write(resp.text)

        articles = []

        # 핵심: 제목 링크 a.news_tit만 일단 싹 긁어온다
        title_tags = soup.select("a.news_tit")
        print("[INFO] 찾은 a.news_tit 개수:", len(title_tags))

        for a_tag in title_tags:
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "").strip()

            # a.news_tit의 상위 div.news_area를 기준으로 언론사/날짜 추출 시도
            news_area = a_tag.find_parent("div", class_="news_area")

            if news_area:
                press_tag = news_area.select_one("a.info.press")
                press = press_tag.get_text(strip=True) if press_tag else "Unknown"

                info_tags = news_area.select("span.info")
                date = info_tags[-1].get_text(strip=True) if info_tags else "Unknown"
            else:
                press = "Unknown"
                date = "Unknown"

            articles.append(
                {
                    "title": title,
                    "press": press,
                    "date": date,
                    "url": link,
                }
            )

        df = pd.DataFrame(articles)
        return df
    # def scrape_naver_news(self, keyword: str, page: int = 1) -> pd.DataFrame:
    #     """
    #     네이버 뉴스 검색 결과에서
    #     제목 / 링크 / 언론사 / 날짜만 수집
    #     """

    #     start = (page - 1) * 10 + 1
    #     url = (
    #         "https://search.naver.com/search.naver"
    #         f"?where=news&sm=tab_opt&query={keyword}&start={start}"
    #     )

    #     print("[INFO] 요청 URL:", url)
    #     resp = requests.get(url, headers=self.headers)
    #     print("[INFO] status code:", resp.status_code)

    #     soup = BeautifulSoup(resp.text, "lxml")

    #     articles = []

    #     # 핵심 포인트: 뉴스 검색 결과는 ul.list_news > li 구조인 경우가 많음
    #     li_list = soup.select("ul.list_news > li")
    #     print("[INFO] 찾은 li 개수:", len(li_list))

    #     for li in li_list:
    #         # 제목 & 링크
    #         a_tag = li.select_one("a.news_tit")
    #         if not a_tag:
    #             continue

    #         title = a_tag.get_text(strip=True)
    #         link = a_tag.get("href", "").strip()

    #         # 언론사
    #         press_tag = li.select_one("a.info.press")
    #         press = press_tag.get_text(strip=True) if press_tag else "Unknown"

    #         # 날짜 (여러 span.info 중 마지막 항목인 경우가 많음)
    #         info_tags = li.select("span.info")
    #         date = info_tags[-1].get_text(strip=True) if info_tags else "Unknown"

    #         articles.append(
    #             {
    #                 "title": title,
    #                 "press": press,
    #                 "date": date,
    #                 "url": link,
    #             }
    #         )

    #     df = pd.DataFrame(articles)
    #     return df
