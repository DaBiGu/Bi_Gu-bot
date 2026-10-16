from utils.utils import get_asset_path
from utils.platforms import get_platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import asyncio, atexit, os, platform, tempfile, time
from pathlib import Path

PAGE_LOAD_TIMEOUT = 30.0
SCRIPT_TIMEOUT = 15.0
MAX_CONCURRENT_BROWSERS = 2
HEALTH_CHECK_TIMEOUT = 5.0

EXTENSION_PATH = get_asset_path("chrome/GitHub Isometric Contributions.crx")

def chromedriver_filename() -> str:
    return "chromedriver.exe" if get_platform() == "windows" else "chromedriver"

def chromedriver_platform_tag() -> str:
    current = get_platform()
    if current == "windows": return "win64"
    if current == "macos": return "mac-arm64" if platform.machine() in ("arm64", "aarch64") else "mac-x64"
    return "linux64"

def file_url(path: str) -> str:
    return Path(path).resolve().as_uri()

def launch_driver(load_extension: bool, page_load_timeout: float):
    options = Options()
    options.add_argument("--headless")
    if load_extension and os.path.exists(EXTENSION_PATH):
        try:
            options.add_extension(EXTENSION_PATH)
        except Exception:
            pass
    driver = webdriver.Chrome(
        executable_path = get_asset_path(f"chrome/{chromedriver_filename()}"),
        options = options,
    )
    driver.set_page_load_timeout(page_load_timeout)
    driver.set_script_timeout(SCRIPT_TIMEOUT)
    return driver

def quit_driver(driver) -> None:
    if driver is None: return
    try:
        driver.quit()
    except Exception:
        pass

class DriverPool:
    def __init__(self, size: int) -> None:
        self.size = max(1, int(size))
        self.sem = None
        self.sem_loop = None
        self.idle = []

    def semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        if self.sem is None or self.sem_loop is not loop:
            self.discard_all()
            self.sem, self.sem_loop = asyncio.Semaphore(self.size), loop
        return self.sem

    def discard_all(self) -> None:
        for driver in self.idle: quit_driver(driver)
        self.idle.clear()

    @staticmethod
    async def is_alive(driver) -> bool:
        try:
            await asyncio.wait_for(asyncio.to_thread(driver.execute_script, "return 1"), timeout = HEALTH_CHECK_TIMEOUT)
            return True
        except Exception:
            return False

    async def acquire(self):
        sem = self.semaphore()
        await sem.acquire()
        try:
            while self.idle:
                driver = self.idle.pop()
                if await self.is_alive(driver): return driver
                await asyncio.to_thread(quit_driver, driver)
            return await asyncio.to_thread(launch_driver, True, PAGE_LOAD_TIMEOUT)
        except BaseException:
            sem.release()
            raise

    async def release(self, driver, reusable: bool = True) -> None:
        if reusable and driver is not None:
            self.idle.append(driver)
        else:
            await asyncio.to_thread(quit_driver, driver)
        self.semaphore().release()

    async def close(self) -> None:
        self.discard_all()

    def shutdown(self) -> None:
        self.discard_all()


POOL = DriverPool(MAX_CONCURRENT_BROWSERS)
atexit.register(POOL.shutdown)

async def close_browser_pool() -> None:
    await POOL.close()

class Chrome:
    def __init__(self, page_load_timeout: float = PAGE_LOAD_TIMEOUT, load_extension: bool = True):
        self.driver = None
        self.page_load_timeout = page_load_timeout
        self.load_extension = load_extension
        self.from_pool = False

    async def __aenter__(self):
        if self.load_extension:
            self.driver = await POOL.acquire()
            self.from_pool = True
        else:
            self.driver = await asyncio.to_thread(launch_driver, False, self.page_load_timeout)
            self.from_pool = False

        try:
            await asyncio.to_thread(self.driver.set_page_load_timeout, self.page_load_timeout)
            await asyncio.to_thread(self.driver.set_script_timeout, SCRIPT_TIMEOUT)
        except Exception:
            pass
        return self

    async def __aexit__(self, type, val, tb):
        driver, self.driver = self.driver, None
        if driver is None: return
        if not self.from_pool:
            await asyncio.to_thread(quit_driver, driver)
            return
        await POOL.release(driver, reusable = type is None)

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

    def render_html(self, html_path: str, output_path: str, root_id: str, min_window_width: int, min_window_height: int) -> None:
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

        viewport_width = max(int(size.get("width", 0)), min_window_width, 1)
        viewport_height = max(int(size.get("height", 0)), min_window_height, 1)
        self.driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {"width": viewport_width, "height": viewport_height, "deviceScaleFactor": 1, "mobile": False},
        )
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
            await self.call(self.render_html, html_path, output_path, root_id, min_window_width, min_window_height)
        finally:
            if temp_file and os.path.exists(temp_file):
                try: os.remove(temp_file)
                except OSError: pass

    def render_url(self, url: str, output_path: str, by, value: str, pre_sleep: float, post_scroll_sleep: float, maximize: bool) -> None:
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
        await self.call(self.render_url, url, output_path, by, value, pre_sleep, post_scroll_sleep, maximize)

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