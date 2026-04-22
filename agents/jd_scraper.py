import os
import random
import sys
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()


def start():
    [_, url] = sys.argv
    if url is not None:
        scrape_jd(url)


def scrape_jd(url: str):
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context(user_agent=os.getenv("USER_AGENT"))
    context.add_init_script(
        """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    )
    page = context.new_page()
    page.goto("https://google.com")
    time.sleep(random.uniform(2, 4))
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    # job_data = page.locator(".decorated-job-posting__details").inner_text()
    # print(job_data)


if __name__ == "__main__":
    start()
