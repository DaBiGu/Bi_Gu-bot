from nonebot.adapters.onebot.v11 import MessageSegment, Message
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from utils.chrome import get_chromedriver
from utils.utils import get_output_path

async def get_github_chart(github_id: str, _2d: bool = False) -> Message:
    chrome = await get_chromedriver()
    try:
        chrome.get(f"https://github.com/{github_id}")
        await asyncio.sleep(3)
        chrome.maximize_window()
        if _2d:
            button = WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-ic-option='squares' and contains(@class, 'ic-toggle-option')]"))
            )
            button.click()
            chart = chrome.find_element(By.CLASS_NAME, "js-calendar-graph")
        else:
            chart = chrome.find_element(By.CLASS_NAME, "ic-contributions-wrapper")
        _text = "0 contributions in the last year"
        texts = chrome.find_elements_by_class_name("f4.text-normal.mb-2")
        for text in texts:
            if "contributions" in text.text: _text = text.text
        chrome.execute_script("arguments[0].scrollIntoView(true);", chart)
        await asyncio.sleep(1)
        output_path = get_output_path(f"{github_id}_chart", temp = True)  
        chart.screenshot(output_path)
        return Message([MessageSegment.text(_text), MessageSegment.image(f"file:///{output_path}")])
    except Exception:
        return f"target user \"{github_id}\" not found"