from utils.utils import get_asset_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import asyncio, os, tempfile, time
from pathlib import Path

PAGE_LOAD_TIMEOUT = 30.0
SCRIPT_TIMEOUT = 15.0
MAX_CONCURRENT_BROWSERS = 2

_slots = None
_slots_loop = None


def _browser_slots() -> asyncio.Semaphore:
    global _slots, _slots_loop
    loop = asyncio.get_running_loop()
    if _slots is None or _slots_loop is not loop:
        _slots, _slots_loop = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS), loop
    return _slots

def file_url(path: str) -> str:
    return Path(path).resolve().as_uri()

class Chrome:
    def __init__(self, page_load_timeout: float = PAGE_LOAD_TIMEOUT, load_extension: bool = True):
        self.driver = None
        self.page_load_timeout = page_load_timeout
        self.load_extension = load_extension
        self._extension_path = get_asset_path("chrome/GitHub Isometric Contributions.crx")
        self._slot = None

    def _launch(self):
        """同步启动 driver, 由 __aenter__ 丢到线程里执行。"""
        options = Options()
        options.add_argument("--headless")
        if self.load_extension and os.path.exists(self._extension_path):
            try:
                options.add_extension(self._extension_path)
            except Exception:
                pass
        driver = webdriver.Chrome(executable_path = get_asset_path("chrome/chromedriver.exe"), options = options)
        driver.set_page_load_timeout(self.page_load_timeout)
        driver.set_script_timeout(SCRIPT_TIMEOUT)
        return driver

    async def __aenter__(self):
        self._slot = _browser_slots()
        await self._slot.acquire()
        try:
            self.driver = await asyncio.to_thread(self._launch)
        except BaseException:
            self._slot.release()
            self._slot = None
            raise
        return self

    async def __aexit__(self, type, val, tb):
        try:
            if self.driver: await self.call(self.driver.quit)
        finally:
            self.driver = None
            if self._slot is not None:
                self._slot.release()
                self._slot = None

    async def call(self, fn, *args, **kwargs):
        if not self.driver: raise RuntimeError("Chrome instance not initialized")
        return await asyncio.to_thread(fn, *args, **kwargs)

    async def get_file(self, path: str) -> None:
        if not self.driver: raise RuntimeError("Chrome instance not initialized")
        await self.call(self.driver.get, file_url(path))

    async def wait_js(self, script: str, timeout: float = 10.0, interval: float = 0.05) -> bool:
        if not self.driver: raise RuntimeError("Chrome instance not initialized")
        deadline = time.monotonic() + timeout
        while True:
            if await self.call(self.driver.execute_script, script): return True
            if time.monotonic() >= deadline: return False
            await asyncio.sleep(interval)

    def _render_html(self, html_path: str, output_path: str, root_id: str, min_window_width: int, min_window_height: int) -> None:
        self.driver.get(file_url(html_path))
        time.sleep(0.9)
        size = self.driver.execute_script(
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
        self.driver.set_window_size(max(1, width), max(1, height))
        time.sleep(0.3)
        self.driver.find_element(By.ID, root_id).screenshot(output_path)

    async def screenshot_html(self, source: str, output_path: str, root_id: str = "card-root", min_window_width: int = 0, min_window_height: int = 0) -> None:
        if not self.driver: raise RuntimeError("Chrome instance not initialized")

        is_html_string = source.strip().startswith("<") or "<html" in source.lower()
        if is_html_string:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html", delete=False) as f:
                f.write(source)
                html_path = f.name
            temp_file = html_path
        else:
            html_path, temp_file = source, None

        try:
            await self.call(self._render_html, html_path, output_path, root_id, min_window_width, min_window_height)
        finally:
            if temp_file and os.path.exists(temp_file):
                try: os.remove(temp_file)
                except OSError: pass

    def _render_url(self, url: str, output_path: str, by, value: str, pre_sleep: float, post_scroll_sleep: float, maximize: bool) -> None:
        self.driver.get(url)
        time.sleep(pre_sleep)
        if maximize: self.driver.maximize_window()
        element = self.driver.find_element(by, value)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(post_scroll_sleep)
        element.screenshot(output_path)

    async def screenshot_url(self, url: str, output_path: str, by, value: str, pre_sleep: float = 3.0, post_scroll_sleep: float = 1.0, maximize: bool = True) -> None:
        if not self.driver:
            raise RuntimeError("Chrome instance not initialized. Use 'async with Chrome()' context.")
        await self.call(self._render_url, url, output_path, by, value, pre_sleep, post_scroll_sleep, maximize)

    async def screenshot(self, source: str, output_path: str, **kwargs) -> None:
        if source.startswith(("http://", "https://")):
            by = kwargs.get("by")
            value = kwargs.get("value")
            if by is None or value is None:
                raise ValueError("URL mode requires 'by' and 'value' parameters")
            await self.screenshot_url(
                source, output_path, by, value,
                pre_sleep=kwargs.get("pre_sleep", 3.0),
                post_scroll_sleep=kwargs.get("post_scroll_sleep", 1.0),
                maximize=kwargs.get("maximize", True)
            )
        else:
            await self.screenshot_html(
                source, output_path,
                root_id=kwargs.get("root_id", "card-root"),
                min_window_width=kwargs.get("min_window_width", 0),
                min_window_height=kwargs.get("min_window_height", 0)
            )