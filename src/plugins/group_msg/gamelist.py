from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from utils.utils import get_asset_path, get_output_path, get_copyright_str, load_asset_html
from utils.chrome import screenshot_html_card
from PIL import Image
import html as html_utils
import os, tempfile, math

def calc_page_size_by_bg(bg_path: str) -> tuple[int, int]:
    page_width, page_height = 1320, 900
    if not bg_path: return page_width, page_height
    try:
        with Image.open(bg_path) as img: bg_w, bg_h = img.size
        if bg_w > 0 and bg_h > 0:
            # Keep ratio and allow moderate upscale inside bounds.
            max_w, max_h = 2000, 1400
            scale = min(max_w / bg_w, max_h / bg_h)
            page_width = max(1, int(bg_w * scale))
            page_height = max(1, int(bg_h * scale))
    except Exception: pass
    return page_width, page_height


def split_gamelist_pages(game_rows: list[dict], page_width: int, page_height: int) -> list[list[dict]]:
    root_lr_padding = 36 * 2
    game_col_width = 260
    row_col_gap = 14
    row_lr_padding = 16 * 2
    avatar_size = 46
    avatar_gap = 8
    row_min_avatars_h = 56
    row_vertical_padding = 28
    row_gap = 12

    top_reserved = 34 + 64 + 20
    bottom_reserved = 24 + 16 + 24
    available_h = max(220, page_height - top_reserved - bottom_reserved)

    avatars_area_w = max(120, page_width - root_lr_padding - game_col_width - row_col_gap - row_lr_padding)
    avatars_per_line = max(1, avatars_area_w // (avatar_size + avatar_gap))

    def estimate_row_h(member_count: int) -> int:
        line_count = max(1, math.ceil(member_count / avatars_per_line))
        avatars_h = max(row_min_avatars_h, line_count * avatar_size + max(0, line_count - 1) * avatar_gap)
        return avatars_h + row_vertical_padding

    pages: list[list[dict]] = []
    current_page: list[dict] = []
    used_h = 0

    for row in game_rows:
        row_h = estimate_row_h(int(row.get("member_count", 0)))
        next_h = row_h if not current_page else used_h + row_gap + row_h
        if current_page and next_h > available_h:
            pages.append(current_page)
            current_page = [row]
            used_h = row_h
        else:
            current_page.append(row)
            used_h = next_h

    if current_page:
        pages.append(current_page)
    return pages if pages else [[]]


async def draw_gamelist(data: dict, group_id: str, bot: Bot, event: GroupMessageEvent, brief: bool = False) -> str | Message | MessageSegment:
    group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
    nicknames = {}
    for member in group_members_raw:
        nicknames[member["user_id"]] = member["nickname"]

    if group_id not in data or not data[group_id]:
        return "本群暂无游戏列表"

    if brief:
        return "====== 本群游戏列表 ======\n" + ", ".join([str(game) for game in data[group_id]])

    template, css = load_asset_html("gamelist_card")
    game_rows = []
    for game in data[group_id]:
        avatars = []
        for member_id in data[group_id][game]:
            member_id_str = str(member_id)
            try:
                member_nickname = nicknames.get(int(member_id_str), member_id_str)
            except Exception:
                member_nickname = member_id_str
            avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={member_id_str}&s=100"
            avatars.append(
                f'<img class="avatar" src="{avatar_url}" title="{html_utils.escape(str(member_nickname))}" alt="{html_utils.escape(str(member_nickname))}"/>'
            )
        avatars_html = "".join(avatars) if avatars else '<span class="empty">暂无成员</span>'
        game_rows.append({
            "game": str(game),
            "member_count": len(data[group_id][game]),
            "row_html": f'<div class="row"><div class="game-name">{html_utils.escape(str(game))}</div><div class="avatars">{avatars_html}</div></div>',
        })

    bg_path = get_asset_path("images/gamelist_card_background.png")
    bg_url = ("file:///" + bg_path.replace("\\", "/")) if bg_path else ""
    page_width, page_height = calc_page_size_by_bg(bg_path)
    pages = split_gamelist_pages(game_rows, page_width, page_height)

    output_paths = []
    total_pages = len(pages)
    for page_index, page_rows in enumerate(pages, 1):
        page_css = css.replace("{{BG_IMAGE_URL}}", bg_url)
        page_css += f"\n:root {{ --page-width: {page_width}px; --page-height: {page_height}px; }}\n"
        footer = f"{get_copyright_str()} | Page {page_index} of {total_pages}"
        html_content = template.replace("{{STYLE_BLOCK}}", f"<style>\n{page_css}\n</style>") \
            .replace("{{GROUP_ID}}", html_utils.escape(group_id)) \
            .replace("{{ROWS}}", "\n".join([row["row_html"] for row in page_rows])) \
            .replace("{{FOOTER}}", html_utils.escape(footer))

        with tempfile.NamedTemporaryFile(mode = "w", encoding = "utf-8", suffix = ".html", delete = False) as f:
            f.write(html_content)
            html_path = f.name

        output_path = get_output_path(f"gamelist_p{page_index}")
        try:
            await screenshot_html_card(html_path = html_path, output_path = output_path, min_window_width = page_width + 80, min_window_height = page_height + 120)
            output_paths.append(output_path)
        finally:
            if os.path.exists(html_path):
                os.remove(html_path)

    message = Message([MessageSegment.image("file:///" + path) for path in output_paths]) if len(output_paths) > 1 else MessageSegment.image("file:///" + output_paths[0])
    return message