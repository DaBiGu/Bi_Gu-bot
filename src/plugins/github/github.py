from nonebot.adapters.onebot.v11 import MessageSegment
from selenium.webdriver.common.by import By
import time, asyncio
from utils.chrome import get_chromedriver
from utils.utils import get_output_path

async def get_github_chart(github_id: str) -> MessageSegment:
    chrome = await get_chromedriver()
    chrome.get(f"https://github.com/{github_id}")
    await asyncio.sleep(3)
    chrome.maximize_window() 
    try: chart = chrome.find_element(By.CLASS_NAME, "ic-contributions-wrapper")
    except: return MessageSegment.text(f"Target user \"{github_id}\" not found")
    chrome.execute_script("arguments[0].scrollIntoView(true);", chart)
    await asyncio.sleep(1) 
    output_path = get_output_path("github_chart")
    chart.screenshot(output_path)
    chrome.quit()
    return MessageSegment.image("file:///" + output_path)