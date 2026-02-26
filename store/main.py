from scraping.news_scraper import NewsScraper


def main():
    scraper = NewsScraper()

    df = scraper.scrape_naver_news("삼성전자", page=1)

    print(df.head())
    print("총 기사 수:", len(df))


if __name__ == "__main__":
    main()
