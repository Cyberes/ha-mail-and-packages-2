import os
from typing import Optional

import chromedriver_autoinstaller
import undetected_chromedriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeDriverManager:
    __driver: Optional[webdriver.Chrome] = None

    @classmethod
    def start(cls):
        cls.__driver = None
        os.system('killall -9 chrome')
        chromedriver_autoinstaller.install()
        options = Options()
        cls.__driver = undetected_chromedriver.Chrome(options=options)

    @classmethod
    def end(cls):
        if cls.__driver:
            cls.__driver.quit()
            cls.__driver = None

    @classmethod
    def driver(cls) -> webdriver.Chrome:
        if cls.__driver is None:
            raise ValueError("Driver is not started. Call ChromeDriverManager.start() first.")
        return cls.__driver
