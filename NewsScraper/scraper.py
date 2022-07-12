"""
Scraper for scraping websites urls and the corresponding articles.
"""

from bs4 import BeautifulSoup
from utils import SeleniumScraper, RequestScraper, Article, Website

import requests


class YahooFinance(Website):
    URL = "https://finance.yahoo.com"
    COOKIES_XPATH = "//*[@id='consent-page']/div/div/div/form/div[2]/div[2]/button"

    def __init__(self) -> None:
        super().__init__(self.URL)

    def __eq__(self, url: str) -> bool:
        return self.URL in url

    @staticmethod
    def __scroll_to_bottom(driver, waiter, key):
        # yahoo customized script for scrolling to bottom of page
        for _ in range(15):
            driver.find_element_by_tag_name('body').send_keys(key.END)
            waiter(driver, 5).until(lambda _: True)

    def get_urls(self, stock: str) -> list[str]:
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

    def get_article(self, url) -> Article:
        """Scrape all data from a given url to article."""

        with RequestScraper(url) as scraper:
            soup = scraper.load(verify=False) # basf ssl protection

        headline = soup.select('h1[data-test-locator="headline"]')[0]
        body = soup.find('div', attrs={'class': 'caas-body'})
        author = soup.find('span', attrs={'class': 'caas-author-byline-collapse'})
        date = soup.find('time')

        article: Article = Article(
            headline = headline.text,
            body = body.text,
            author = author.text,
            date  = date.text
        )

        return article


# TODO: get_article => headline, author, date
class Spiegel(Website):
    """Spiegel.de news api scraper."""
    URL: str = "https://www.spiegel.de/"

    def __init__(self) -> None:
        super().__init__(self.URL)

    def __eq__(self, url: str) -> bool:
        return self.URL in url

    def ctr_api_url(self, stock: str, length: int | str = 30) -> str:
        """Construct the url for searching in spiegel.de"""
        # TODO: inspect url more -> since/ max.pages param?
        return f"{self.URL}services/sitesearch/search?segments=spon%2Cspon_paid%2Cspon_international%2Cmmo%2Cmmo_paid%2Chbm%2Chbm_paid&after=-2208988800&before=1657025585&page_size={length}&page=1&q={stock}"

    def get_urls(self, stock: str) -> set[str]:
        """Call the spiegel.de api and parse the json data to find the news urls."""
        api_url: str = self.ctr_api_url(stock)
        
        result: dict = requests.get(api_url).json()
        
        urls: set[str] = set()

        for result in result["results"]:
            urls.add(result["url"])

        return urls

    def get_article(self, url: str) -> Article:
        with RequestScraper(url) as scraper:
            soup: BeautifulSoup = scraper.load()

        raw_body: list[BeautifulSoup] = self.list_find_all(soup, {'div': {'data-sara-click-el': 'body_element'}, 'p': {}})
        body: str = ""
        for paragraph in raw_body:
            body += paragraph.text

        article: Article = Article(
            headline="Empty",
            body=body
        )

        return article


# TODO
class ManagerMagazin(Website):
    ...


class GoogleFinance(Website):
    """Google finance news scraping scraper."""
    URL = "https://www.google.com/finance/"

    def __init__(self) -> None:
        super().__init__(self.URL)

    def __eq__(self, url: str) -> bool:
        raise False # because google has no articles it cannot be scraped -> always False

    def get_urls(self, stock: str) -> list[str]:
        """Scrape all news urls from google finance."""
        # TODO: Search function for finding stock exchange
        search_url = f"{self.URL}quote/{stock.upper()}:NASDAQ"

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

    def get_article(self, url) -> Article:
        NotImplementedError("Cannot scrape Google articles.")


ARTICLE_SCRAPER: set[Website] = {YahooFinance, Spiegel}

def get_articles(urls: list[str], scraper: set[Website] = ARTICLE_SCRAPER) -> set[Article]:
    """Find scraper for url and scrape the content article."""
    articles: set[Article] = set()

    for url in urls:
        for article_scraper in scraper:

            s = article_scraper()
            if s == url:
                articles.add(s.get_article(url)) # add check if article was scraped succesfull?
                break # go to next url if article was scraped
    
    return articles


if __name__ == "__main__":
    stock = "BASF"
    # urls: set[str] = YahooFinance().get_urls(stock)
    # urls.update(GoogleFinance().get_urls(stock))

    scraper = Spiegel()
    urls = scraper.get_urls(stock)
    articles: set[Article] = get_articles(urls)
    