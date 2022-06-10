"""
Utils for scraping with selenium or simple requests.get()
"""

## Local imports ##
from Exceptions import CannotAcceptCookies

## in-build imports ##
from typing import Optional, Union
from datetime import date
from abc import ABC, abstractmethod
import requests

## other imports ##
from attr import define
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft  import EdgeChromiumDriverManager

Function = type(lambda:_)


@define(frozen=True)
class Article:
    """This defines how a article should be structured."""
    headline: str
    body: str
    author: Optional[str]
    date: Optional[str | date]


class Website(ABC):
    COOKIE_ACCEPT: set[str.lower] = {
        "alle akzeptieren",
        "accept all",
        "alle cookies akzeptieren",
        "accept all cookies",
        "akzeptieren und fortfahren",
        "accept and continue",
        "ich akzeptiere",
        "i accept",
        "akzeptieren",
        "accept",
        "consent"
    }

    def __init__(self, url: str):
        self.base_url = url

    def __recursive_find_all(self, soup, search, search_keys, n=0):
        id = search_keys[n]
        if len(search)-1 == n: # if last layer
            return soup.find_all(id, attrs=search[id]) # list[str]

        # not last layer
        results: list[str] = []
        for result in soup.find_all(id, attrs=search[id]):
            results.extend(self.__recursive_find_all(result, search, search_keys, n+1))
        return results

    def recursive_find_all(self, soup, search: dict[str, dict]) -> list:
        """Recursivly find all items by content and attrs."""
        search_keys = list(search) # ['ul', 'li', 'a']

        return self.__recursive_find_all(soup, search, search_keys)

    @abstractmethod
    def scrape_article(self, article_url: str) -> Article:
        """Scrape the url to find Article infos."""

    @abstractmethod
    def scrape_urls(self, stock: str) -> list[str]:
        """Scrape the url to find all sub news urls."""


class _NewsScraper(ABC):
    """Private base scraper class."""
    def __init__(self, url):
        self.url = url

    def get_encoding(self, text: str) -> str:
        """Get encoding of a string."""
        return "utf-8" # TODO

    def convert_to_scraper(self, content: str) -> BeautifulSoup:
        """Convert the website to a soup object."""
        return BeautifulSoup(content, 'html.parser')

    @abstractmethod
    def load(self, *args, **kwargs) -> BeautifulSoup:
        """This should load in a website."""


class SeleniumScraper(_NewsScraper):
    """This is to scrape using selenium - loading in all data etc."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = webdriver.EdgeOptions()
        # options.add_argument('--headless')
        self.driver = webdriver.Edge(EdgeChromiumDriverManager().install(), options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # TODO: handle known exception...
        pass

    def load(self, scroll_to_bottom: Function | bool = True, accept_cookies=True) -> BeautifulSoup:
        """This initalizes the page and loads the data."""
        self.driver.get(self.url)
        self.__accept_cookies() if accept_cookies else None
        # self.__scroll_to_bottom() if scroll_to_bottom else None
        print("Decision point", scroll_to_bottom, type(scroll_to_bottom))
        if isinstance(scroll_to_bottom, Function):
            print("nice")
            scroll_to_bottom(self.driver, WebDriverWait, Keys)
        elif scroll_to_bottom == True:
            print("not nice")
            self.__scroll_to_bottom()
        else:
            print("what??")

        # scroll_to_bottom() if isinstance(scroll_to_bottom, Function) else self.__scroll_to_bottom()
        return self.convert_to_scraper(self.driver.page_source)

    def __scroll_to_bottom(self) -> None:
        """This functions scrolls to the bottom of a webpage -> loads in all data."""
        # while not self.__is_fully_loaded():
        # scroll 20 times to bottom and wait for side load
            # WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, '')))

        # always returns true -> other way of checking for end of page
        while (result:=lambda driver: driver.execute_script('return document.readyState') != 'complete')(self.driver):
            self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
            WebDriverWait(self.driver, 5).until(result)

    def __accept_cookies(self, xpath:str="") -> None: # plan b -> x_path as input
        """Accepts all cookies."""
        # cookies = self.driver.manage().getCookies(); # Returns the List of all Cookies
        # self.driver.manage().getCookieNamed(arg0); # Returns the specific cookie according to name
        # self.driver.manage().addCookie(arg0); # Creates and adds the cookie
        button = self.driver.find_element_by_xpath("//*[@id='consent-page']/div/div/div/form/div[2]/div[2]/button") # TODO: only works for yf
        button.click()


class RequestScraper(_NewsScraper):
    """This is for simple requests with get function."""

    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def load(self, **kwargs) -> BeautifulSoup:
        if 'headers' not in kwargs: # add a header
            kwargs['headers'] = self.HEADER
        website = requests.get(self.url, **kwargs)
        # TODO: scraping here
        website.encoding = self.get_encoding(website.content)

        return self.convert_to_scraper(website.content)


if __name__ == '__main__':
    with SeleniumScraper(url="test") as scraper:
        print(scraper.url)

    with RequestScraper(url="test") as scraper:
        print(scraper.url)
