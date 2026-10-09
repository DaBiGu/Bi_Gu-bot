from nonebot.adapters.onebot.v11 import MessageSegment
from utils.utils import get_asset_path, get_output_path
from utils.chrome import Chrome
from selenium.webdriver.common.by import By
import asyncio

async def gen_ba(left: str, right: str) -> MessageSegment:
    async with Chrome() as chrome:
        await chrome.call(chrome.driver.set_window_size, 1200, 900)
        await chrome.get_file(get_asset_path("ba/ba.html"))
        await chrome.call(chrome.driver.execute_script, """
            const loading = document.getElementById('loading');
            window.__ba_t0 = performance.now();
            window.__ba_transition_count = 0;
            new MutationObserver(mutations => {
                for (const m of mutations) {
                    const wasHidden = (m.oldValue || '').split(/\\s+/).includes('hidden');
                    const isHidden = m.target.classList.contains('hidden');
                    if (wasHidden !== isHidden) window.__ba_transition_count++;
                }
            }).observe(loading, {attributes: true, attributeFilter: ['class'], attributeOldValue: true});
        """)
        loaded = await chrome.wait_js("""
            return window.__ba_transition_count >= 2 ||
                   (performance.now() - window.__ba_t0 > 800 &&
                    document.getElementById('loading').classList.contains('hidden') &&
                    document.fonts.status === 'loaded');
        """, timeout=15.0)
        if not loaded: return MessageSegment.text("ba 卡片生成失败: 页面加载超时")
        await chrome.call(chrome.driver.execute_script, """
            window.__ba_transition_count = 0;
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                el.value = val;
                el.dispatchEvent(new Event('input', {bubbles: true}));
            };
            setVal('textL', arguments[0]);
            setVal('textR', arguments[1]);
        """, left, right)
        await chrome.wait_js("""
            return window.__ba_transition_count >= 2 &&
                   document.getElementById('loading').classList.contains('hidden');
        """)
        await asyncio.sleep(0.15)
        await chrome.call(chrome.driver.execute_script, "window.scrollTo(0, 0);")
        output_path = get_output_path("ba")
        canvas = await chrome.call(chrome.driver.find_element, By.ID, "canvas")
        await chrome.call(canvas.screenshot, output_path)
        return MessageSegment.image("file:///" + output_path)