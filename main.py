# main.py

from datetime import datetime, timedelta

from scraping.news_scraper import NewsScraper


def main():
    scraper = NewsScraper()

    ticker = "005930"
    company_name = "삼성전자"

    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)

    df = scraper.scrape(
        ticker=ticker,
        company_name=company_name,
        start_date=start_date,
        end_date=end_date,
    )

    print(df.head())
    print("수집된 (현재는 더미) 기사 수:", len(df))


if __name__ == "__main__":
    main()
