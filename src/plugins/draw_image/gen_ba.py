from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from nonebot.adapters.onebot.v11 import MessageSegment
from utils.utils import get_output_path
from utils.chrome import get_chromedriver
import os, asyncio

async def gen_ba(left: str, right: str) -> MessageSegment:
    chrome = await get_chromedriver()
    chrome.get("file:///" + os.getcwd() + "/src/assets/ba/ba.html")
    input_left = chrome.find_element(By.ID, "textL")
    input_right = chrome.find_element(By.ID, "textR")
    for _ in range(4): input_left.send_keys(Keys.BACKSPACE)
    for _ in range(7): input_right.send_keys(Keys.BACKSPACE)
    input_left.send_keys(left)
    input_right.send_keys(right)
    output_path = get_output_path("ba")
    await asyncio.sleep(0.5)
    chrome.find_element(By.ID, "canvas").screenshot(output_path)
    chrome.quit()
    return MessageSegment.image("file:///" + output_path)