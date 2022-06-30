from utils import SeleniumScraper, RequestScraper, Article, Website


class YahooFinance(Website):
    URL = "https://finance.yahoo.com"
    COOKIES_XPATH = "//*[@id='consent-page']/div/div/div/form/div[2]/div[2]/button"

    def __init__(self):
        super().__init__(self.URL)

    def __eq__(self, url: str) -> bool:
        return self.URL in url

    @staticmethod
    def __scroll_to_bottom(driver, waiter, key):
        # yahoo customized script for scrolling to bottom of page
        for _ in range(15):
            driver.find_element_by_tag_name('body').send_keys(key.END)
            waiter(driver, 5).until(lambda _: True)

    def scrape_urls(self, stock: str) -> list[str]:
        """Get all news urls from stock."""
        news_urls: set[str] = set()

        search_url: str = self.base_url + f"/quote/{stock}/news?p={stock}"
        with SeleniumScraper(search_url) as scraper:
            soup = scraper.load(scroll_to_bottom=self.__scroll_to_bottom)

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


class GoogleFinance(Website):
    """Google finance news scraping scraper."""
    URL = "https://www.google.com/finance/"

    def __init__(self):
        super().__init__(self.URL)

    def __eq__(self, url: str) -> bool:
        return False

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
        for news in news_list:
            url = news.get('href')
            title = news.find('div')
            if not url or not title or url in urls:
                continue
            if not url.startswith("https"): # TODO: exlude videos etc.
                continue

            title = title.find('div', attrs={'class': 'Yfwt5'})

            urls.add(url)

        return urls

    def scrape_article(self, url) -> Article:
        NotImplemented("Cannot scrape Google articles.")


class Spiegel(Website):
    """Scraper for scraping the german news site 'der Spiegel'."""
    URL = "https://www.spiegel.de/"

    def __init__(self):
        super().__init__(self.URL)

    def __eq__(self, other):
        raise NotImplementedError("...")
    
    def scrape_urls(self, urls: list[str]):
        raise NotImplementedError("...")

    def scrape_article(self, article_url: str) -> Article:
        raise NotImplementedError("...")


ARTICLE_SCRAPER: set[Website] = {YahooFinance}

def scrape_articles(urls: list[str]) -> set[Article]:
    """Find scraper for url and scrape the content article."""
    articles: set[Article] = set()

    for url in urls:
        for article_scraper in ARTICLE_SCRAPER:

            s = article_scraper()
            if s == url:
                articles.add(s.scrape_article(url)) # add check if article was scraped succesfull?
                break # go to next url if article was scraped
    
    return articles


if __name__ == "__main__":
    s = Spiegel()

    stock = "MSFT"
    # urls: set[str] = YahooFinance().scrape_urls(stock)
    # urls.update(GoogleFinance().scrape_urls(stock))

    # articles: set[Article] = scrape_articles(urls)
    # print(articles)