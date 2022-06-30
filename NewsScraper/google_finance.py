from utils import SeleniumScraper, RequestScraper, Article, Website


class GoogleFinance(Website):
    URL = "https://www.google.com/finance/"

    def __init__(self):
        super().__init__(self.URL)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def scrape_urls(self, stock: str) -> list[str]:
        """Scrape all news urls from google finance."""
        # TODO: Search function for finding stock exchange
        search_url = f"https://www.google.com/finance/quote/{stock.upper()}:NASDAQ"

        with RequestScraper(search_url) as scraper:
            soup = scraper.load(verify=False)

        found = soup.find('div', attrs={'class': 'b4EnYd'})
        if found:
            raise Exception("Stock not found")

        news_list = []
        news_objects = soup.find_all('div', {'class': 'yY3Lee'})
        for news in news_objects:
            news_list.append(news.find('div').find('div').find('a'))

        urls: set = {""}
        news_urls: list = []
        for news in news_list:
            url = news.get('href')
            title = news.find('div')
            if not url or if not title or url in urls:
                continue
            if not url.startswith("https"):
                continue

            title = title.find('div', attrs={'class': 'Yfwt5'})

            urls.add(url) # duplicate checking
            news_urls.append([url, title.text])

        return news_urls

    def scrape_article(self, url) -> Article:
        # TODO: Check if article is from google else throw exception "Can't Scrape non google Articles"
        pass


if __name__ == '__main__':
    with GoogleFinance() as scraper:
        urls = scraper.scrape_urls("MSFT")
        [print(">", url) for url in urls]

        # for url in urls:
        #     print(scraper.scrape_article(url))
