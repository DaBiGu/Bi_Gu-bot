from utils.utils import get_asset_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import asyncio

async def get_chromedriver():
    options = Options()
    options.add_argument("--headless")
    options.add_extension(get_asset_path("chrome/GitHub Isometric Contributions.crx"))
    chrome = webdriver.Chrome(executable_path = get_asset_path("chrome/chromedriver.exe"), options = options)
    return chrome


async def screenshot_html_card(html_path: str, output_path: str, root_id: str = "card-root", min_window_width: int = 0, min_window_height: int = 0) -> None:
    chrome = await get_chromedriver()
    try:
        chrome.get("file:///" + html_path.replace("\\", "/"))
        await asyncio.sleep(0.9)
        size = chrome.execute_script(
            """
            const root = document.getElementById(arguments[0]);
            if (!root) {
                return {width: document.body.scrollWidth || 0, height: document.body.scrollHeight || 0};
            }
            const rect = root.getBoundingClientRect();
            return {width: Math.ceil(rect.width), height: Math.ceil(rect.height)};
            """,
            root_id,
        )
        width = max(int(size.get("width", 0)) + 80, min_window_width)
        height = max(int(size.get("height", 0)) + 120, min_window_height)
        chrome.set_window_size(max(1, width), max(1, height))
        await asyncio.sleep(0.3)
        chrome.find_element(By.ID, root_id).screenshot(output_path)
    finally:
        chrome.quit()