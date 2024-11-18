from utils.utils import get_asset_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

async def get_chromedriver():
    options = Options()
    options.add_argument("--headless")
    options.add_extension(get_asset_path("chrome/GitHub Isometric Contributions.crx"))
    chrome = webdriver.Chrome(executable_path = get_asset_path("chrome/chromedriver.exe"), options = options)
    return chrome