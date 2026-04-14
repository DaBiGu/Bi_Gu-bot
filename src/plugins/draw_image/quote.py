from io import BytesIO
from typing import Iterable
import datetime
import json
import os
import random

import requests, numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent

from utils.fonts import get_font, get_embedded_font
from utils.text_layout import pick_font_and_wrap_by_width
from utils.utils import get_IO_path, get_copyright_str, get_output_path

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

def save_quote_record(group_id: int, user_id: int, quote_text: str, msg_time: str = "") -> int:
    db = load_quote_db()
    quote_id = get_next_quote_id(db)
    data = db.setdefault("data", {})
    group_key = str(group_id)
    if group_key not in data or not isinstance(data[group_key], dict): data[group_key] = {}
    data[group_key][str(quote_id)] = {"user_id": user_id, "quote_text": quote_text, "msg_time": msg_time}
    save_quote_db(db)
    return quote_id

def search_quote_records(group_id: int, keyword: str) -> list[tuple[int, dict]]:
    db = load_quote_db()
    group_quotes = db.get("data", {}).get(str(group_id), {})
    if not isinstance(group_quotes, dict): return []
    matched: list[tuple[int, dict]] = []
    for quote_id_str, record in group_quotes.items():
        if not isinstance(record, dict): continue
        text = str(record.get("quote_text", ""))
        if keyword in text:
            quote_id = int(quote_id_str)
            matched.append((quote_id, record))
    return matched

def get_quote_record_by_id(group_id: int, quote_id: int) -> tuple[dict | None, bool]:
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
    alpha = np.where(xs <= (boundary_2d - fade_width), 255.0, np.where(xs >= boundary_2d, 0.0, 255.0 * (boundary_2d - xs) / max(1, fade_width)))
    return Image.fromarray(alpha.astype(np.uint8), mode = "L")

def _format_quote_text(text: str) -> str:
    text = text.strip()
    return "「[N/A]」" if not text else text if (text.startswith("「") and text.endswith("」")) else f"「{text}」"


def _format_msg_time(raw_time: int | float | None) -> str:
    if raw_time is None: return ""
    try: return datetime.datetime.fromtimestamp(int(raw_time)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception: return ""

def fix_tail_single_char(lines: list[str], draw: ImageDraw.ImageDraw,
                          font: Image.Image, max_width: int) -> list[str]:
    if len(lines) < 2: return lines
    tail = lines[-1].strip()
    if len(tail) != 1: return lines
    merged = lines[-2] + lines[-1]
    if draw.textlength(merged, font = font) <= max_width:
        lines[-2] = merged
        lines.pop()
        return lines
    if len(lines[-2]) >= 2:
        lines[-1] = lines[-2][-1] + lines[-1]
        lines[-2] = lines[-2][:-1]
    return lines

def put_quote_text(image: Image.Image, text: str, nickname: str, msg_time: str = "", quote_id: int = 0) -> Image.Image:
    width, height = image.size
    draw = ImageDraw.Draw(image)
    name_font = get_embedded_font("sourcehan-sans", "noto-color-emoji", size = int(height * 0.08))
    time_font = get_font("sourcehan-sans", int(height * 0.05))
    max_width = int(width * 0.48)
    right_padding = int(width * 0.07)
    right_edge = width - right_padding
    text_left = right_edge - max_width
    text = _format_quote_text(text)
    quote_font, lines, line_gap, line_height = pick_font_and_wrap_by_width(
        text, draw, get_embedded_font, ("sourcehan-sans", "noto-color-emoji"),
        [int(height * p) for p in [0.16, 0.14, 0.12, 0.10, 0.085, 0.074, 0.064, 0.056, 0.050]],
        max_width = max_width, max_lines = 10, use_jieba = True,
        line_gap = int(height * 0.02), max_text_height = int(height * 0.52), min_font_size = 16)
    lines = fix_tail_single_char(lines, draw, quote_font, max_width)
    quote_h = len(lines) * line_height + (len(lines) - 1) * line_gap
    name_h = name_font.getbbox("Ag")[3] - name_font.getbbox("Ag")[1]
    time_h = time_font.getbbox("Ag")[3] - time_font.getbbox("Ag")[1] if msg_time else 0
    name_gap = int(height * 0.07)
    time_gap = int(height * 0.05) if msg_time else 0
    block_h = quote_h + name_gap + name_h + time_gap + time_h
    start_y = (height - block_h) // 2

    y = start_y
    for line in lines:
        draw.text((text_left, y), line, fill = (244, 244, 244), font = quote_font)
        y += line_height + line_gap
    y += name_gap
    nickname_text = f"@{nickname}"
    nickname_w = draw.textlength(nickname_text, font = name_font)
    draw.text((right_edge - nickname_w, y), nickname_text, fill = (130, 130, 130), font = name_font)
    if msg_time:
        y += name_h + time_gap
        time_w = draw.textlength(msg_time, font = time_font)
        draw.text((right_edge - time_w, y), msg_time, fill = (110, 110, 110), font = time_font)
    quote_id_text = f"Quote #{quote_id:06d}"
    quote_id_w = draw.textlength(quote_id_text, font = time_font)
    draw.text((right_edge - quote_id_w, y + name_gap), quote_id_text,
              fill = (110, 110, 110), font = time_font)
    '''
    copyright_font = get_font("sourcehan-sans", int(height * 0.036))
    copyright_text = get_copyright_str()
    copyright_w = draw.textlength(copyright_text, font = copyright_font)
    copyright_bottom_padding = int(height * 0.025)
    copyright_h = copyright_font.getbbox("Ag")[3] - copyright_font.getbbox("Ag")[1]
    draw.text((width - copyright_w - int(right_padding * 0.5), height - copyright_bottom_padding - copyright_h),
              copyright_text, fill = (244, 244, 244), font = copyright_font)
    '''
    return image


def render_quote_card(text: str, nickname: str, qq: int | str,
                      msg_time: str = "",
                      quote_id: int = 0,
                      output_path: str | None = None,
                      size: tuple[int, int] = (2160, 720)) -> str:
    width, height = size
    avatar = load_qq_avatar(qq, size = 640)
    left_width = int(width * 0.40)
    avatar_panel = fit_cover(avatar, (left_width, height))
    avatar_panel = ImageEnhance.Contrast(avatar_panel).enhance(1.06)
    avatar_panel = ImageEnhance.Brightness(avatar_panel).enhance(0.92)
    avatar_panel = avatar_panel.filter(ImageFilter.GaussianBlur(radius = 0.8))

    quote_img = Image.new("RGB", size, (0, 0, 0))
    mask = get_arc_fade_mask(left_width, height, radius_ratio = 7.2,
                             center_y_ratio = 0.60, edge_offset = 36, fade_width = 28)
    quote_img.paste(avatar_panel, (0, 0), mask)
    quote_img = put_quote_text(quote_img, text, nickname, msg_time = msg_time, quote_id = quote_id)

    output_path = output_path or get_output_path("quote")
    quote_img.save(output_path)
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
    group_members_raw = await bot.call_api("get_group_member_list", group_id = group_id)
    for member in group_members_raw:
        if str(member.get("user_id")) == str(user_id): return member["nickname"]
    return str(user_id)

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
        output_path = render_quote_card(quote_text, nickname, user_id, msg_time = msg_time, quote_id = quote_id)
        return Message([MessageSegment.image("file:///" + output_path)])
    except Exception as exc:
        return f"生成引用图失败: {exc}"

async def draw_quote_from_search(bot: Bot, event: GroupMessageEvent, keyword: str) -> Message | str:
    matched = search_quote_records(event.group_id, keyword)
    if not matched: return f"本群未找到包含关键词“{keyword}”的引用内容"
    quote_id, record = random.choice(matched)
    user_id = int(record.get("user_id", 0) or 0)
    quote_text = str(record.get("quote_text", "[N/A]"))
    msg_time = str(record.get("msg_time", ""))
    nickname = await get_member_nickname(bot, event.group_id, user_id)
    output_path = render_quote_card(quote_text, nickname, user_id, msg_time = msg_time, quote_id = quote_id)
    return Message([MessageSegment.image("file:///" + output_path)])

def get_search_result_text(group_id: int, keyword: str) -> str:
    matched = search_quote_records(group_id, keyword)
    if not matched: return f"本群未找到包含关键词“{keyword}”的引用内容"
    lines = [f"本群包含关键词“{keyword}”的引用内容如下："]
    for quote_id, record in sorted(matched, key = lambda item: item[0]):
        user_id = record.get("user_id", "[N/A]")
        content = str(record.get("quote_text", "[N/A]")).replace("\n", " ")
        lines.append(f"Quote #{quote_id:06d} | {user_id} | {content}")
    return "\n".join(lines)

async def draw_quote_from_id(bot: Bot, event: GroupMessageEvent, quote_id: int) -> Message | str:
    record, in_other_group = get_quote_record_by_id(event.group_id, quote_id)
    if record is None: return "未找到对应编号的引用内容" if not in_other_group else "对应的内容不在本群中"
    user_id = int(record.get("user_id", 0) or 0)
    quote_text = str(record.get("quote_text", "[N/A]"))
    msg_time = str(record.get("msg_time", ""))
    nickname = await get_member_nickname(bot, event.group_id, user_id)
    output_path = render_quote_card(quote_text, nickname, user_id, msg_time = msg_time, quote_id = quote_id)
    return Message([MessageSegment.image("file:///" + output_path)])