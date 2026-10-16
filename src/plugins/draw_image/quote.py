from io import BytesIO
from typing import Iterable, Optional
import asyncio, base64, datetime, json, os, random, re, requests
from html import escape as html_escape

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent

from utils.chrome import Chrome, file_url
from utils.fonts import get_font_path
from utils.text_layout import tokenize_text
from utils.utils import get_IO_path, get_output_path, load_asset_html

quote_data_json_path = get_IO_path("quote", "json")

def load_quote_db() -> dict:
    if not os.path.exists(quote_data_json_path): return {"current_quote_id": 0, "data": {}}
    try:
        with open(quote_data_json_path, "r", encoding = "utf-8") as f: data = json.load(f)
        if not isinstance(data, dict): return {"current_quote_id": 0, "data": {}}
        current_id = int(data.get("current_quote_id", 0) or 0)
        quote_data = data.get("data", {})
        if not isinstance(quote_data, dict): quote_data = {}
        return {"current_quote_id": current_id, "data": quote_data}
    except Exception: return {"current_quote_id": 0, "data": {}}

def save_quote_db(data: dict) -> None:
    with open(quote_data_json_path, "w", encoding = "utf-8") as f:
        json.dump(data, f, ensure_ascii = False)

def get_next_quote_id(db: dict) -> int:
    current_id = int(db.get("current_quote_id", 0) or 0)
    next_id = current_id + 1
    db["current_quote_id"] = next_id
    return next_id

def save_quote_record(group_id: int, user_id: int, quote_text: str, msg_time: str = "") -> Optional[int]:
    db = load_quote_db()
    data = db.setdefault("data", {})
    group_key = str(group_id)
    if group_key not in data or not isinstance(data[group_key], dict): data[group_key] = {}
    if any(isinstance(record, dict)
        and int(record.get("user_id", 0) or 0) == int(user_id)
        and str(record.get("msg_time", "")) == str(msg_time)
        and str(record.get("quote_text", "")) == str(quote_text)
        for record in data[group_key].values()
    ): return None
    quote_id = get_next_quote_id(db)
    data[group_key][str(quote_id)] = {"user_id": user_id, "quote_text": quote_text, "msg_time": msg_time}
    save_quote_db(db)
    return quote_id

def search_quote_records(group_id: int, keyword: Optional[str] = None,
                         target_user_id: Optional[int] = None) -> list[tuple[int, dict]]:
    db = load_quote_db()
    group_quotes = db.get("data", {}).get(str(group_id), {})
    if not isinstance(group_quotes, dict): return []
    matched: list[tuple[int, dict]] = []
    for quote_id_str, record in group_quotes.items():
        if not isinstance(record, dict): continue
        record_user_id = int(record.get("user_id", 0) or 0)
        text = str(record.get("quote_text", ""))
        if target_user_id is not None and record_user_id != int(target_user_id):
            continue
        if keyword is not None and keyword not in text:
            continue
        quote_id = int(quote_id_str)
        matched.append((quote_id, record))
    return matched

def get_quote_record_by_id(group_id: int, quote_id: int) -> tuple[Optional[dict], bool]:
    db = load_quote_db()
    quote_key = str(quote_id)
    data = db.get("data", {})
    group_quotes = data.get(str(group_id), {})
    if isinstance(group_quotes, dict) and quote_key in group_quotes and isinstance(group_quotes[quote_key], dict):
        return group_quotes[quote_key], False
    for gid, quotes in data.items():
        if str(gid) == str(group_id) or not isinstance(quotes, dict):
            continue
        if quote_key in quotes:
            return None, True
    return None, False

def load_qq_avatar(qq: int | str, size: int = 640) -> Image.Image:
    qq_str = str(qq).strip()
    if not qq_str.isdigit(): raise ValueError(f"Invalid QQ number: {qq}")
    avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={qq_str}&s={size}"
    response = requests.get(avatar_url, timeout = 12)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")

def _format_quote_text(text: str) -> str:
    text = text.strip()
    return "「[N/A]」" if not text else text if (text.startswith("「") and text.endswith("」")) else f"「{text}」"


def _format_msg_time(raw_time: Optional[int | float]) -> str:
    if raw_time is None: return ""
    try: return datetime.datetime.fromtimestamp(int(raw_time)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception: return ""

def _mark_break_points(text: str) -> str:
    marked = "\u200b".join(tokenize_text(text))
    return re.sub("\u200b(?=[\ufe0f\u200d\U0001F3FB-\U0001F3FF])", "", marked)

def fit_cover(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    src_w, src_h = image.size
    tgt_w, tgt_h = target_size
    src_ratio, tgt_ratio = src_w / src_h, tgt_w / tgt_h
    if src_ratio > tgt_ratio:
        new_h, new_w = tgt_h, int(tgt_h * src_ratio)
    else:
        new_w, new_h = tgt_w, int(tgt_w / src_ratio)
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left, top = (new_w - tgt_w) // 2, (new_h - tgt_h) // 2
    return resized.crop((left, top, left + tgt_w, top + tgt_h))


def get_arc_fade_mask(width: int, height: int, radius_ratio: float = 3.8,
                      center_y_ratio: float = 0.30, edge_offset: int = 10,
                      fade_width: int = 18) -> Image.Image:
    radius = max(height * radius_ratio, float(height) + 1.0)
    cy = height * center_y_ratio
    y_anchor = height * 0.58
    boundary_anchor = width - edge_offset
    root_anchor = np.sqrt(max(radius * radius - (y_anchor - cy) * (y_anchor - cy), 1.0))
    cx = boundary_anchor - root_anchor

    ys = np.arange(height, dtype = np.float32)
    dy = ys - cy
    dy_eff = np.where(dy < 0, dy * 1.18, dy * 0.72)
    inside = np.clip(radius * radius - dy_eff * dy_eff, 1.0, None)
    boundary = np.clip(cx + np.sqrt(inside), 0, width - 1)

    xs = np.arange(width, dtype = np.float32)[None, :]
    boundary_2d = boundary[:, None]
    alpha = np.where(xs <= (boundary_2d - fade_width), 255.0,
                     np.where(xs >= boundary_2d, 0.0,
                              255.0 * (boundary_2d - xs) / max(1, fade_width)))
    return Image.fromarray(alpha.astype(np.uint8), mode = "L")


def _render_avatar_panel(qq: int | str, panel_size: tuple[int, int]) -> str:
    panel = fit_cover(load_qq_avatar(qq), panel_size)
    panel = ImageEnhance.Contrast(panel).enhance(1.06)
    panel = ImageEnhance.Brightness(panel).enhance(0.92)
    panel = panel.filter(ImageFilter.GaussianBlur(radius = 0.8))
    canvas = Image.new("RGBA", panel_size, (0, 0, 0, 0))
    canvas.paste(panel, (0, 0), get_arc_fade_mask(panel_size[0], panel_size[1],
                                                  radius_ratio = 7.2, center_y_ratio = 0.60,
                                                  edge_offset = 36, fade_width = 28))
    buffer = BytesIO()
    canvas.save(buffer, format = "PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def build_quote_card_html(text: str, nickname: str, avatar_src: str, msg_time: str = "",
                          quote_id: int = 0, size: tuple[int, int] = (2160, 720)) -> str:
    template, css = load_asset_html("quote_card")
    width, height = size
    css = (css.replace("{{CARD_W}}", f"{int(width)}px")
              .replace("{{CARD_H}}", f"{int(height)}px")
              .replace("{{FONT_SANS_URL}}", file_url(get_font_path("sourcehan-sans")))
              .replace("{{FONT_EMOJI_URL}}", file_url(get_font_path("noto-color-emoji"))))

    time_block = ""
    if msg_time:
        time_block = f'            <div class="msg-time">{html_escape(msg_time)}</div>\n'

    return (template.replace("{{STYLE_BLOCK}}", f"<style>\n{css}\n</style>")
                    .replace("{{AVATAR_SRC}}", avatar_src)
                    .replace("{{QUOTE_TEXT}}", html_escape(_mark_break_points(_format_quote_text(text))))
                    .replace("{{NICKNAME}}", html_escape(f"@{nickname}"))
                    .replace("{{MSG_TIME_BLOCK}}", time_block)
                    .replace("{{QUOTE_ID}}", html_escape(f"Quote #{quote_id:06d}")))


async def render_quote_card(text: str, nickname: str, qq: int | str,
                            msg_time: str = "",
                            quote_id: int = 0,
                            output_path: Optional[str] = None,
                            size: tuple[int, int] = (2160, 720)) -> str:
    output_path = output_path or get_output_path("quote")
    avatar_src = await asyncio.to_thread(_render_avatar_panel, qq, (int(size[0] * 0.40), size[1]))
    card_html = build_quote_card_html(text, nickname, avatar_src, msg_time, quote_id, size = size)
    async with Chrome() as chrome:
        await chrome.screenshot_html(card_html, output_path,
                                     min_window_width = size[0], min_window_height = size[1])
    return output_path


def extract_plain_text(message_segments: Iterable[dict]) -> str:
    text_parts = []
    for seg in message_segments:
        seg_type = seg.get("type")
        data = seg.get("data", {})
        if seg_type == "text": text_parts.append(data.get("text", ""))
    text = "".join(text_parts).strip()
    return text if text else "[N/A]"


async def get_member_nickname(bot: Bot, group_id: int, user_id: int | str) -> str:
    member = await bot.call_api("get_group_member_info", group_id = group_id, user_id = user_id, no_cache = True)
    nickname = str(user_id)
    try: nickname = member.get("card") or member.get("nickname") or str(user_id)
    except Exception: nickname = str(user_id)
    return nickname

async def draw_quote_from_reply(bot: Bot, event: GroupMessageEvent) -> Message | str:
    if not event.reply: return "请先回复一条群消息，再使用 /q"
    try:
        raw_msg = await bot.call_api("get_msg", message_id = event.reply.message_id)
        sender = raw_msg.get("sender", {})
        user_id = sender.get("user_id") or raw_msg.get("user_id")
        if user_id is None: return "无法获取被引用用户信息"
        nickname = await get_member_nickname(bot, event.group_id, user_id)
        quote_text = extract_plain_text(raw_msg.get("message", []))
        msg_time = _format_msg_time(raw_msg.get("time"))
        quote_id = save_quote_record(event.group_id, int(user_id), quote_text, msg_time)
        if quote_id is None: return "该条消息已经被存入过了"
        output_path = await render_quote_card(quote_text, nickname, user_id, msg_time = msg_time, quote_id = quote_id)
        return Message([MessageSegment.image("file:///" + output_path)])
    except Exception as exc:
        return f"生成引用图失败: {exc}"

async def draw_quote_from_search(bot: Bot, event: GroupMessageEvent,
                                 keyword: Optional[str] = None,
                                 target_user_id: Optional[int] = None) -> Message | str:
    matched = search_quote_records(event.group_id, keyword = keyword, target_user_id = target_user_id)
    if not matched:
        if target_user_id is not None:
            nickname = await get_member_nickname(bot, event.group_id, target_user_id)
            return f"本群未找到成员“{nickname}”的引用内容"
        return f"本群未找到包含关键词“{keyword}”的引用内容" if keyword is not None else "本群暂无引用内容"
    quote_id, record = random.choice(matched)
    user_id = int(record.get("user_id", 0) or 0)
    quote_text = str(record.get("quote_text", "[N/A]"))
    msg_time = str(record.get("msg_time", ""))
    nickname = await get_member_nickname(bot, event.group_id, user_id)
    output_path = await render_quote_card(quote_text, nickname, user_id, msg_time = msg_time, quote_id = quote_id)
    return Message([MessageSegment.image("file:///" + output_path)])

async def get_search_result_text(bot: Bot, group_id: int,
                                 keyword: Optional[str] = None,
                                 target_user_id: Optional[int] = None) -> str:
    matched = search_quote_records(group_id, keyword = keyword, target_user_id = target_user_id)
    if not matched:
        if target_user_id is not None:
            nickname = await get_member_nickname(bot, group_id, target_user_id)
            return f"本群未找到成员“{nickname}”的引用内容"
        return f"本群未找到包含关键词“{keyword}”的引用内容"

    if target_user_id is not None:
        nickname = await get_member_nickname(bot, group_id, target_user_id)
        lines = [f"本群成员“{nickname}”的引用内容如下："]
    else: lines = [f"本群包含关键词“{keyword}”的引用内容如下："]

    content_lines: list[str] = []
    for quote_id, record in sorted(matched, key = lambda item: item[0]):
        user_id = record.get("user_id", "[N/A]")
        nickname = await get_member_nickname(bot, group_id, user_id)
        content = str(record.get("quote_text", "[N/A]")).replace("\n", " ")
        content_lines.append(f"Quote #{quote_id:06d} | {nickname} | {content}")

    lines += content_lines[:5] + [f"[...{len(content_lines) - 10}条更多内容...]"] + content_lines[-5:] if len(content_lines) > 12 else content_lines
    return "\n".join(lines)

async def draw_quote_from_id(bot: Bot, event: GroupMessageEvent, quote_id: int) -> Message | str:
    record, in_other_group = get_quote_record_by_id(event.group_id, quote_id)
    if record is None: return "未找到对应编号的引用内容" if not in_other_group else "对应的内容不在本群中"
    user_id = int(record.get("user_id", 0) or 0)
    quote_text = str(record.get("quote_text", "[N/A]"))
    msg_time = str(record.get("msg_time", ""))
    nickname = await get_member_nickname(bot, event.group_id, user_id)
    output_path = await render_quote_card(quote_text, nickname, user_id, msg_time = msg_time, quote_id = quote_id)
    return Message([MessageSegment.image("file:///" + output_path)])