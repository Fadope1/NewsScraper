from utils import SeleniumScraper, RequestScraper, Article, Website


class YahooFinance(Website):
    URL = "https://finance.yahoo.com"
    COOKIES_XPATH = "//*[@id='consent-page']/div/div/div/form/div[2]/div[2]/button"

    def __init__(self):
        super().__init__(self.URL)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        # TODO
        pass

    @staticmethod
    def __scroll_to_bottom(driver, waiter, key):
        # yahoo customized script for scrolling to bottom of page
        print("yahoo scrolling started")

        for _ in range(15):
            driver.find_element_by_tag_name('body').send_keys(key.END)
            waiter(driver, 5).until(lambda _: False) # to fast -> wait for some class


    def scrape_urls(self, stock: str) -> list[str]:
        """Get all news urls from stock."""
        news_urls: set[str] = set()

        search_url: str = self.base_url + f"/quote/{stock}/news?p={stock}"
        with SeleniumScraper(search_url) as scraper:
            soup = scraper.load(scroll_to_bottom=YahooFinance.__scroll_to_bottom)

        list_objects = self.list_find_all(
                            soup,
                            {
                               'ul': {'class', 'My(0) P(0) Wow(bw) Ov(h)'},
                               'li': {},
                               'a': {}
                            }
                        )

        for object in list_objects:
            link = object.get('href')
            if link.startswith('/') and not link.startswith('/video'):
                if link not in news_urls:
                    news_urls.add(self.URL+link)

        return news_urls

    def scrape_article(self, url) -> Article:
        """Scrape all data from a given url to article."""

        with RequestScraper(url) as scraper:
            soup = scraper.load(verify=False) # basf ssl protection

        headline = soup.select('h1[data-test-locator="headline"]')[0]
        body = soup.find('div', attrs={'class': 'caas-body'})
        author = soup.find('span', attrs={'class': 'caas-author-byline-collapse'})
        date = soup.find('time')

        article = Article(
            headline = headline.text,
            body = body.text,
            author = author.text,
            date  = date.text
        )

        return article


if __name__ == '__main__':
    import pandas as pd

    # TODO: scrape to csv file
    with YahooFinance() as scraper:
        urls = scraper.scrape_urls(stock="MSFT")
        articles: list[Article] = []
        for url in urls:
            articles.append(scraper.scrape_article(url))

        [print("> ", article.headline, article.date, article.author) for article in articles]

    # df = pd.DataFrame(list(zip(urls, articles)))
    # df.to_csv("MSFT.csv")
