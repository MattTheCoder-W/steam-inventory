from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from urllib.parse import quote_plus
from random_user_agent.user_agent import UserAgent
import time

from .loader import Loader


class Browser:
    def __init__(self):
        options = Options()
        options.headless = True
        rotator = UserAgent()
        ua = rotator.get_random_user_agent()
        options.add_argument(f"user-agent={ua}")
        print("[info] using UserAgent:", ua)
        self.driver = webdriver.Firefox(options=options)
        self.decline_cookies()
    
    def decline_cookies(self):
        button_selector = "button#W0wltc"
        self.driver.get("https://google.com")

        for _ in range(10):
            button = self.driver.find_element(By.CSS_SELECTOR, button_selector)
            if not button:
                button = None
                print("[ERROR] Button not found!")
                time.sleep(0.1)
                continue
            button.click()
            print("[success] cookies declined")
            break
        if not button:
            raise Exception("Cannot locate cookie decline button!")
    
    def search(self, query: str, n_items: int = 1) -> list:
        if n_items <= 0:
            return []

        # url = f"https://www.google.com/search?q={quote_plus(query)}"
        url = f"https://duckduckgo.com/?q={quote_plus(query)}"

        # print(f"[info] searching: `{query}` -> `{url}`")

        self.driver.get(url)

        try:
            if self.driver.find_element(By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"):
                print("[warning] captcha detected!")
                input()
        except:
            pass

        # item_selector = "div.yuRUbf"
        item_selector = "div.nrn-react-div"

        queried = False
        while True:
            results = self.driver.find_elements(By.CSS_SELECTOR, item_selector)
            if not results:
                # print("[warning] no results found")
                if queried:
                    return []
                time.sleep(1)
                queried = True
                continue
            break
        
        # print(f"Found {len(results)} results")
        if n_items > len(results):
            n_items = len(results)

        urls = []
        for item in results[:n_items]:
            link = item.find_element(By.CSS_SELECTOR, 'a[data-testid="result-title-a"]')
            urls.append(link.get_attribute("href"))
        
        # print(f"Scraped {len(urls)} elements")
        return urls

    def scrape_price(self, data: dict):
        if not data['url']:
            print("No URL!")
            return None

        self.driver.add_cookie({"name":"currency","domain":"csgostash.com","value":"eyJpdiI6InlubmZoYmhkRVEwQkZGa2dkY21SZXc9PSIsInZhbHVlIjoiUGwvYjdPN3l1ZmNvVGNGMUpad0tRSUorVmZ6Ty9LcDRDR2VRTHZOb3ZhVU90NmpzQ0g1Mlp0L2xHUG02ejJRTiIsIm1hYyI6ImM4MTkwYjAxODdlMTdhN2IyMzY1ZGVhOTMxNWJlZTA4ZDI3NzA0YWI4Nzc2M2FkZjY1OTkwNjBiNDNjNGRiNzUiLCJ0YWciOiIifQ"})
        self.driver.get(data['url'])

        price_element = self.driver.find_element(By.CSS_SELECTOR, 'a.btn.btn-default.market-button-item')
        price_value = price_element.text
        print(f"Value is: {price_value}")
        return price_value

class Scraper:
    def __init__(self):
        self.loader = Loader("stage-2.xlsx")
        self.browser = Browser()

        for i, item in enumerate(self.loader.data):
            if item['url']:
                print("[info] item already has url, skipping!")
                continue
            print(f"[{i+1}/{len(self.loader.data)}] Item: {item['name']}")
            price = item['price']
            query = f"{item['name']} {item['type']} site:csgostash.com"
            urls = self.browser.search(query, n_items=1)
            if not urls:
                print("[warning] items not found for item")
                continue
            self.loader.data[i]['url'] = urls[0]
        
        self.loader.save_urls("stage-3.xlsx")

        self.check_prices()
    
    def check_prices(self):
        self.browser.driver.get(self.loader.data[0]['url'])
        for i, item in enumerate(self.loader.data):
            print(f"[{i+1}/{len(self.loader.data)}] Scraping item: {item['name']}")
            price = self.browser.scrape_price(item)
            self.loader.data[i]['last_price'] = price
        
        self.loader.save_prices("stage-3.xlsx")


