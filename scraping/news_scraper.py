# scraping/news_scraper.py

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List

import pandas as pd


@dataclass
class NewsArticle:
    """개별 뉴스 기사의 원본 정보를 담는 데이터 구조."""
    ticker: str           # 예: '005930'
    company_name: str     # 예: '삼성전자'
    date: datetime        # 기사 날짜
    title: str            # 기사 제목
    press: Optional[str]  # 언론사
    reporter: Optional[str]  # 기자 이름 (없으면 None)
    content: str          # 기사 본문
    url: str              # 기사 링크


class NewsScraper:
    """
    여러 종목에 대해 뉴스 기사를 수집하는 클래스의 골격.
    나중에 실제 스크래핑 로직(네이버/다음/언론사 사이트)을 이 안에 채워 넣을 거야.
    """

    def __init__(self):
        # 나중에 세션, 헤더, 프록시 같은 설정도 여기서 관리
        pass

    def scrape(
        self,
        ticker: str,
        company_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """
        start_date ~ end_date 기간 동안의 뉴스를 수집해서
        pandas DataFrame으로 반환하는 메인 함수.

        지금은 일단 '골격용'이라 더미 데이터 한 줄만 만들어서 구조만 테스트해볼 거야.
        나중에 실제 웹 스크래핑 코드를 여기에 채워 넣자.
        """
        dummy_article = NewsArticle(
            ticker=ticker,
            company_name=company_name,
            date=start_date,
            title=f"[더미] {company_name} 뉴스 제목 예시",
            press="테스트언론사",
            reporter=None,
            content="이것은 더미 뉴스 본문입니다. 나중에 실제 스크래핑으로 대체됩니다.",
            url="https://example.com/dummy",
        )

        df = pd.DataFrame([asdict(dummy_article)])
        return df
