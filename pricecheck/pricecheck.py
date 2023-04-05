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
        options.headless = False
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

        url = f"https://www.google.com/search?q={quote_plus(query)}"

        print(f"[info] searching: `{query}` -> `{url}`")

        self.driver.get(url)
        time.sleep(0.5)

        try:
            if self.driver.find_element(By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"):
                print("[warning] captcha detected!")
                input()
        except:
            pass

        item_selector = "div.yuRUbf"

        queried = False
        while True:
            results = self.driver.find_elements(By.CSS_SELECTOR, item_selector)
            if not results:
                print("[warning] no results found")
                if queried:
                    return []
                time.sleep(1)
                queried = True
                continue
            break
        
        print(f"Found {len(results)} results")
        if n_items > len(results):
            n_items = len(results)

        urls = []
        for item in results[:n_items]:
            link = item.find_element(By.CSS_SELECTOR, "a")
            urls.append(link.get_attribute("href"))
        
        print(f"Scraped {len(urls)} elements")
        return urls


class Scraper:
    def __init__(self):
        self.loader = Loader("table.xlsx")
        self.browser = Browser()

        for item in self.loader.data:
            print(f"Item: {item['name']}")
            price = item['price']
            query = f"{item['name']} site:csgostash.com"
            urls = self.browser.search(query, n_items=1)
            if not urls:
                print("[warning] items not found for item")
                continue
            print(f"[data] item url: {urls[0]}")
        # print("Found:", self.browser.search("fnatic (gold) site:csgostash.com"))
