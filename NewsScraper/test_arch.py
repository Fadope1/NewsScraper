class Website:
    ...
    

Article = "Defines what a article is"


class YahooFinance(Website):
    URL: str = "yahoo.finance.com"

    @staticmethod
    def scrape_article(self, url: str) -> Article:
        return Article("some data")

    def get_urls(self, stock: str):
        return ["https://...", ...]

    def __eq__(self, url: str):
        return self.URL in url


class GoogleFinance(Website):
    ...


class Scraper:
    """Base class for scraping websites."""
    ARTICLE_SCRAPER: list[Website] = [YahooFinance, GoogleFinance]

    # ARTICLE_DICT = {YahooFinance.URL: YahooFinance}

    @staticmethod
    def scrape_article(self, url) -> Article:
        return Article("something")

    def scrape_articles(self, urls: list[str]) -> list[Article]:
        articles: list[Article] = []

        for url in urls:
            for scraper in self.ARTICLE_SCRAPER:
                if url == scraper:
                    articles.extend(scraper.scrape_article(url))

        # articles: list[Article] = [self.ARTICLE_DICT.get(url, self).scrape_article(url) for url in urls]

        # for url in urls:
        #     scraper = self.ARTICLE_DICT.get(url, self)
        #     articles.extend(scraper.scrape_article(url))

        x >= 2
        return articles


urls: list[str] = YahooFinance.get_urls("BASF")
urls.extend(GoogleFinance.get_urls("BASF"))
articles: list[Article] = Scraper.scrape_articles(urls: list[str])
