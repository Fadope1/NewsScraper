from bs4 import BeautifulSoup

BASE_URL = "https://finance.yahoo.com"
STOCK = "MSFT"
STOCK_URL = BASE_URL + f"/quote/{STOCK}/news?p={STOCK}"

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft  import EdgeChromiumDriverManager
options = webdriver.EdgeOptions()
options.add_argument('--headless')
driver = webdriver.Edge(EdgeChromiumDriverManager().install(), options=options)
driver.get(STOCK_URL)

# click accept cookies button
button = driver.find_element_by_xpath("//*[@id='consent-page']/div/div/div/form/div[2]/div[2]/button")
button.click()

# wait for load
WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'mrt-node-latestQuoteNewsStream-0-Stream')))

[driver.find_element_by_tag_name('body').send_keys(Keys.END) for _ in range(15)] # TODO: how to load complete page? Where is the end

soup = BeautifulSoup(driver.page_source, 'html.parser')


links = []
for link in soup.find_all('ul', attrs={'class': 'My(0) P(0) Wow(bw) Ov(h)'}):
    try:
        for link in link.find_all('li'):
            for link in link.find_all('a'):
                link = link.get('href')
                if link.startswith('/') and not link.startswith('/video'):
                    if link not in links:
                        links.append(BASE_URL+link)
    except Exception as e:
        continue

import pandas as pd

# df = pd.DataFrame(links, columns =['url'])
# df.to_csv(f"yahoo-finance_{STOCK}_urls.csv")
# [print(">", link) for link in links]

headlines = []
import requests
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# get links content and headers
for link in links: # get class = caas-body
    site = requests.get(link, verify=False, headers=headers)
    # site.encoding = "CP-1252" # "utf-8" # TODO: build encoder definer
    soup = BeautifulSoup(site.content, 'html.parser')
    try:
        found_headlines = soup.select('h1[data-test-locator="headline"]')[0]
        headlines.append(found_headlines.text)
    except Exception:
        continue

# [print(headline) for headline in headlines]
df = pd.DataFrame(list(zip(links, headlines)), columns =['url', 'headline'])

df.to_csv(f"yahoo-finance_{STOCK}.csv")

print(df.head())
