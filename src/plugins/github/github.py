from nonebot.adapters.onebot.v11 import MessageSegment, Message
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import asyncio
from utils.chrome import Chrome
from utils.utils import get_output_path

_WINDOW_WIDTH, _WINDOW_HEIGHT = 1440, 1200

async def get_github_chart(github_id: str, _2d: bool = False) -> Message:
    async with Chrome() as chrome:
        try:
            await chrome.call(chrome.driver.set_window_size, _WINDOW_WIDTH, _WINDOW_HEIGHT)
            await chrome.call(chrome.driver.get, f"https://github.com/{github_id}")
            await asyncio.sleep(3)

            chart = await _find_contribution_chart(chrome, _2d)
            contribution_text = await chrome.call(_scrape_contribution_text, chrome.driver)
            await chrome.call(chrome.driver.execute_script, "arguments[0].scrollIntoView(true);", chart)
            await asyncio.sleep(1)
            output_path = get_output_path(f"{github_id}_chart", temp=True)
            await chrome.call(chart.screenshot, output_path)
            return Message([MessageSegment.text(contribution_text), MessageSegment.image(f"file:///{output_path}")])
        except NoSuchElementException:
            return f"target user \"{github_id}\" not found"
        except TimeoutException:
            return f"访问 github.com/{github_id} 超时"
        except Exception as e:
            return f"获取 {github_id} 的贡献图失败({type(e).__name__})"


async def _find_contribution_chart(chrome: Chrome, _2d: bool):
    if not _2d:
        try:
            return await chrome.call(chrome.driver.find_element, By.CLASS_NAME, "ic-contributions-wrapper")
        except NoSuchElementException:
            pass
    else:
        try:
            button = await chrome.call(
                WebDriverWait(chrome.driver, 3).until,
                EC.element_to_be_clickable((By.XPATH, "//button[@data-ic-option='squares' and contains(@class, 'ic-toggle-option')]")),
            )
            await chrome.call(button.click)
        except (TimeoutException, NoSuchElementException):
            pass
    return await chrome.call(chrome.driver.find_element, By.CLASS_NAME, "js-calendar-graph")


def _scrape_contribution_text(driver) -> str:
    try:
        for el in driver.find_elements(By.CLASS_NAME, "f4.text-normal.mb-2"):
            if "contributions" in el.text:
                return el.text
    except Exception:
        pass
    return "0 contributions in the last year"