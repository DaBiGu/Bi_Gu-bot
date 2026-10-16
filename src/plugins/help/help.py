import os
import html as html_utils
from nonebot.adapters.onebot.v11 import MessageSegment
from utils.utils import get_copyright_str, get_output_path, get_asset_path, load_asset_html
from utils.chrome import Chrome, file_url

async def draw_help(helper_message: str, current_page: int, total_pages: int) -> MessageSegment:
    template, css = load_asset_html("help_card")
    background_path = get_asset_path("images/help_background.png")
    background_url = file_url(background_path) if os.path.exists(background_path) else ""

    footer = f"{get_copyright_str()}  |  Page {current_page} of {total_pages}"
    html_content = (
        template
        .replace("{{STYLE_BLOCK}}", f"<style>\n{css}\n</style>")
        .replace("{{BG_URL}}", background_url)
        .replace("{{CONTENT}}", html_utils.escape(helper_message.strip("\n")))
        .replace("{{FOOTER}}", html_utils.escape(footer))
    )

    output_path = get_output_path("help")
    async with Chrome() as chrome:
        await chrome.screenshot_html(html_content, output_path, root_id="card-root")
    return MessageSegment.image(f"file:///{output_path}")